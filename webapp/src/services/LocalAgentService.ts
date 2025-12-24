/**
 * Local Agent Service
 * ===================
 * Manages the Edge AI Web Worker.
 * Loads the model locally and provides a simple API for parsing commands.
 */
import { getAIConfig } from '../config/aiConfig';

export type AIStatus = 'idle' | 'loading' | 'ready' | 'error';

class LocalAgentService {
    private worker: Worker | null = null;
    private status: AIStatus = 'idle';
    private progress: number = 0;
    private listeners: Set<(status: AIStatus, progress: number) => void> = new Set();
    private transcriptListeners: Set<(text: string) => void> = new Set();
    private ocrListeners: Set<(text: string) => void> = new Set();
    private currentResolver: ((value: any) => void) | null = null;

    constructor() {
        if (typeof window !== 'undefined' && 'Worker' in window) {
            this.initWorker();
        }
    }

    private initWorker() {
        // Vite handles the ?worker suffix automatically
        this.worker = new Worker(
            new URL('../workers/aiWorker.ts', import.meta.url),
            { type: 'module' }
        );

        this.worker.onmessage = (event) => {
            const { type, data } = event.data;

            switch (type) {
                case 'STATUS':
                    this.status = data;
                    this.notify();
                    break;
                case 'PROGRESS':
                    // Transformers.js progress is an object with { progress: 0-100 }
                    this.progress = data.progress || 0;
                    this.notify();
                    break;
                case 'RESULT':
                    if (this.currentResolver) {
                        this.currentResolver(data);
                        this.currentResolver = null;
                    }
                    break;
                case 'TRANSCRIPT':
                    this.notifyTranscript(data);
                    break;
                case 'OCR_RESULT':
                    this.notifyOCR(data);
                    break;
                case 'ERROR':
                    this.status = 'error';
                    console.error('[LocalAgent] Worker Error:', data);
                    this.notify();
                    break;
            }
        };
    }

    /**
     * Start loading the model
     * Suggested model: Xenova/gemma-2b-it-quantized
     */
    async loadModel() {
        if (this.status === 'ready' || this.status === 'loading') return;

        const config = await getAIConfig();
        const modelId = config.models.text;

        this.worker?.postMessage({
            type: 'LOAD_MODEL',
            data: { modelId }
        });
    }

    /**
     * Parse text locally
     */
    async parse(text: string): Promise<any> {
        if (this.status !== 'ready') {
            throw new Error('AI Engine not ready');
        }

        return new Promise((resolve) => {
            this.currentResolver = resolve;
            this.worker?.postMessage({
                type: 'PARSE_COMMAND',
                data: { text }
            });
        });
    }

    /**
     * Process Voice Audio (Float32Array)
     */
    async processVoice(audio: Float32Array) {
        this.worker?.postMessage({
            type: 'PROCESS_VOICE',
            data: { audio }
        });
    }

    /**
     * Process OCR Image (String URL or File)
     */
    async processOCR(image: string | File) {
        this.worker?.postMessage({
            type: 'PROCESS_OCR',
            data: { image }
        });
    }

    subscribe(fn: (status: AIStatus, progress: number) => void) {
        this.listeners.add(fn);
        return () => this.listeners.delete(fn);
    }

    subscribeTranscript(fn: (text: string) => void) {
        this.transcriptListeners.add(fn);
        return () => this.transcriptListeners.delete(fn);
    }

    subscribeOCR(fn: (text: string) => void) {
        this.ocrListeners.add(fn);
        return () => this.ocrListeners.delete(fn);
    }

    private notify() {
        this.listeners.forEach(fn => fn(this.status, this.progress));
    }

    private notifyTranscript(text: string) {
        this.transcriptListeners.forEach(fn => fn(text));
    }

    private notifyOCR(text: string) {
        this.ocrListeners.forEach(fn => fn(text));
    }

    getStatus() { return this.status; }
    getProgress() { return this.progress; }
}

export const localAgent = new LocalAgentService();
