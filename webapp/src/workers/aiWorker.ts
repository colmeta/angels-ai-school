import { pipeline, env } from "@xenova/transformers";
import Tesseract from "tesseract.js";

// Configuration
env.allowLocalModels = false;
env.useBrowserCache = true;

let generator: any = null;
let transcriber: any = null;

/**
 * Handle messages from the main thread
 */
self.onmessage = async (event) => {
    const { type, data } = event.data;

    switch (type) {
        case 'LOAD_MODEL':
            await loadModels(data.modelId);
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
        default:
            console.warn('[AI Worker] Unknown message type:', type);
    }
};

/**
 * Load models with progress reporting
 */
async function loadModels(modelId: string) {
    try {
        self.postMessage({ type: 'STATUS', data: 'loading' });

        // 1. Load Text Generator (Gemma)
        generator = await pipeline('text-generation', modelId, {
            progress_callback: (progress: any) => {
                self.postMessage({ type: 'PROGRESS', data: { ...progress, model: 'text' } });
            }
        });

        // 2. Load Speech Transcriber (Whisper)
        transcriber = await pipeline('automatic-speech-recognition', 'Xenova/whisper-tiny.en', {
            progress_callback: (progress: any) => {
                self.postMessage({ type: 'PROGRESS', data: { ...progress, model: 'voice' } });
            }
        });

        self.postMessage({ type: 'STATUS', data: 'ready' });
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

        // If it looks like a list or a command, we could parse it
        // await parseCommand(text); 
    } catch (error: any) {
        self.postMessage({ type: 'ERROR', data: error.message });
    }
}

/**
 * Parse a command using the local generator
 */
async function parseCommand(text: string) {
    if (!generator) {
        self.postMessage({ type: 'ERROR', data: 'Text engine not loaded' });
        return;
    }

    try {
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
            self.postMessage({ type: 'RESULT', data: JSON.parse(jsonMatch[0]) });
        } else {
            throw new Error("Failed to parse intent");
        }
    } catch (error: any) {
        self.postMessage({ type: 'ERROR', data: error.message });
    }
}
