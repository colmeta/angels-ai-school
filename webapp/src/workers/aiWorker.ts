import { pipeline, env } from "@xenova/transformers";
import Tesseract from "tesseract.js";

// Configuration
env.allowLocalModels = false;
env.useBrowserCache = true;

let generator: any = null;
let transcriber: any = null;
let currentMode: 'core' | 'hybrid' | 'flash' = 'hybrid';
let deviceRAM: number = 1024;

/**
 * Device capability detection
 */
function detectCapabilities() {
    let estimatedRAM = 1024;

    if ('memory' in performance) {
        const memory = (performance as any).memory;
        if (memory && memory.jsHeapSizeLimit) {
            estimatedRAM = Math.floor(memory.jsHeapSizeLimit / (1024 * 1024));
        }
    }

    const isMobile = /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent);

    return {
        ram: estimatedRAM,
        isMobile,
        mode: estimatedRAM >= 1024 ? 'core' : (estimatedRAM >= 512 ? 'hybrid' : 'flash') as 'core' | 'hybrid' | 'flash'
    };
}

/**
 * Handle messages from the main thread
 */
self.onmessage = async (event) => {
    const { type, data } = event.data;

    switch (type) {
        case 'INIT':
            await init(data.mode);
            break;
        case 'LOAD_MODEL':
            await loadModels(data.modelId, data.mode);
            break;
        case 'PARSE_COMMAND':
            await parseCommand(data.text);
            break;
        case 'PROCESS_VOICE':
            await processVoice(data.audio);
            break;
        case 'PROCESS_OCR':
            await processOCR(data.image);
            break;
        case 'GET_CAPABILITIES':
            self.postMessage({ type: 'CAPABILITIES', data: detectCapabilities() });
            break;
        default:
            console.warn('[AI Worker] Unknown message type:', type);
    }
};

/**
 * Initialize worker with mode detection
 */
async function init(preferredMode?: 'core' | 'hybrid' | 'flash') {
    const capabilities = detectCapabilities();
    deviceRAM = capabilities.ram;
    currentMode = preferredMode || capabilities.mode;

    self.postMessage({
        type: 'INITIALIZED',
        data: {
            mode: currentMode,
            ram: deviceRAM,
            capabilities
        }
    });
}

/**
 * Load models based on mode
 */
async function loadModels(modelId?: string, mode?: 'core' | 'hybrid' | 'flash') {
    const targetMode = mode || currentMode;

    try {
        self.postMessage({ type: 'STATUS', data: 'loading' });

        // MODE-SPECIFIC MODEL LOADING
        if (targetMode === 'core') {
            // Full models for high-RAM devices
            generator = await pipeline('text-generation', modelId || 'Xenova/gemma-2b', {
                quantized: false,
                progress_callback: (progress: any) => {
                    self.postMessage({ type: 'PROGRESS', data: { ...progress, model: 'text' } });
                }
            });

        } else if (targetMode === 'hybrid') {
            // Quantized/smaller models for medium-RAM devices
            generator = await pipeline('text-generation', modelId || 'Xenova/distilgpt2', {
                quantized: true,
                progress_callback: (progress: any) => {
                    self.postMessage({ type: 'PROGRESS', data: { ...progress, model: 'text' } });
                }
            });

        } else if (targetMode === 'flash') {
            // Skip text model loading - will use cloud API
            generator = null;
            self.postMessage({
                type: 'PROGRESS',
                data: { status: 'ready', progress: 100, model: 'text', message: 'Using cloud AI' }
            });
        }

        // Voice and OCR models load for all modes (for privacy)
        if (deviceRAM >= 256) {  // Only if device can handle it
            transcriber = await pipeline('automatic-speech-recognition', 'Xenova/whisper-tiny.en', {
                progress_callback: (progress: any) => {
                    self.postMessage({ type: 'PROGRESS', data: { ...progress, model: 'voice' } });
                }
            });
        }

        self.postMessage({
            type: 'STATUS',
            data: 'ready',
            mode: targetMode
        });

    } catch (error: any) {
        self.postMessage({ type: 'ERROR', data: error.message });
    }
}

/**
 * Handle Voice to Intent
 */
async function processVoice(audio: Float32Array) {
    if (!transcriber) {
        self.postMessage({ type: 'ERROR', data: 'Voice engine not loaded' });
        return;
    }

    try {
        const output = await transcriber(audio, {
            chunk_length_s: 30,
            stride_length_s: 5,
        });

        const text = output.text;
        self.postMessage({ type: 'TRANSCRIPT', data: text });

        // Auto-parse the transcript into an intent
        await parseCommand(text);
    } catch (error: any) {
        self.postMessage({ type: 'ERROR', data: error.message });
    }
}

/**
 * Handle OCR (Image to Text)
 */
async function processOCR(image: string | File) {
    try {
        self.postMessage({ type: 'OCR_STATUS', data: 'processing' });

        const result = await Tesseract.recognize(image, 'eng', {
            logger: m => {
                if (m.status === 'recognizing text') {
                    self.postMessage({ type: 'PROGRESS', data: { progress: m.progress * 100, model: 'ocr' } });
                }
            }
        });

        const text = result.data.text;
        self.postMessage({ type: 'OCR_RESULT', data: text });

    } catch (error: any) {
        self.postMessage({ type: 'ERROR', data: error.message });
    }
}

/**
 * Parse command - handles both local and cloud modes
 */
async function parseCommand(text: string) {
    try {
        if (currentMode === 'flash') {
            // Use cloud API for Flash mode
            await parseCommandCloud(text);
        } else {
            // Use local model for Core/Hybrid modes
            await parseCommandLocal(text);
        }
    } catch (error: any) {
        self.postMessage({ type: 'ERROR', data: error.message });
    }
}

/**
 * Parse command using local model (Core, Hybrid)
 */
async function parseCommandLocal(text: string) {
    if (!generator) {
        self.postMessage({ type: 'ERROR', data: 'Text engine not loaded' });
        return;
    }

    const prompt = `You are a school assistant. Extract action and data from: "${text}"
    Output valid JSON only. Example: {"action": "attendance", "entity": "student", "name": "John"}`;

    const output = await generator(prompt, {
        max_new_tokens: 128,
        temperature: 0.1,
        do_sample: false,
        return_full_text: false
    });

    const resultText = output[0].generated_text;
    const jsonMatch = resultText.match(/\{.*\}/s);

    if (jsonMatch) {
        self.postMessage({
            type: 'RESULT',
            data: JSON.parse(jsonMatch[0]),
            source: 'local'
        });
    } else {
        throw new Error("Failed to parse intent");
    }
}

/**
 * Parse command using cloud API (Flash mode)
 */
async function parseCommandCloud(text: string) {
    // Send message to main thread to handle cloud request
    // (Worker can't make fetch requests with auth easily)
    self.postMessage({
        type: 'CLOUD_REQUEST',
        data: { text }
    });
}

// Auto-initialize on worker load
init();
