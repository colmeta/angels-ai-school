/**
 * AI Configuration System
 * Supports three tiers: Core (offline), Hybrid (smart sync), Flash (cloud)
 */
export const AI_CONFIGS = {
    core: {
        mode: 'core',
        models: {
            text: 'Xenova/gemma-2b',
            voice: 'Xenova/whisper-tiny.en',
            ocr: 'tesseract.js',
            quantized: false
        },
        features: {
            cloudSync: false,
            cloudFallback: false,
            offlineOnly: true
        },
        limits: {
            minRAM: 1024,
            maxRAM: Infinity,
            maxConcurrent: 3,
            appSize: 200
        },
        storage: {
            local: true,
            cloud: false
        }
    },
    hybrid: {
        mode: 'hybrid',
        models: {
            text: 'Xenova/distilgpt2', // Smaller, quantized model
            voice: 'Xenova/whisper-tiny.en',
            ocr: 'tesseract.js',
            quantized: true
        },
        features: {
            cloudSync: true,
            cloudFallback: true, // User can enable
            offlineOnly: false
        },
        limits: {
            minRAM: 512,
            maxRAM: 1024,
            maxConcurrent: 1,
            appSize: 50
        },
        storage: {
            local: true,
            cloud: true,
            cloudProvider: 'r2'
        }
    },
    flash: {
        mode: 'flash',
        models: {
            text: 'none', // Uses cloud APIs
            voice: 'Xenova/whisper-tiny.en', // Keep voice local for privacy
            ocr: 'tesseract.js',
            quantized: false
        },
        features: {
            cloudSync: true,
            cloudFallback: true,
            offlineOnly: false
        },
        limits: {
            minRAM: 256,
            maxRAM: 512,
            maxConcurrent: 5,
            appSize: 30
        },
        storage: {
            local: true,
            cloud: true,
            cloudProvider: 'r2'
        }
    }
};
export function detectDeviceCapabilities() {
    // Detect RAM (only works in Chrome with performance.memory API)
    let estimatedRAM = 1024; // Default to 1GB
    if ('memory' in performance) {
        const memory = performance.memory;
        if (memory && memory.jsHeapSizeLimit) {
            estimatedRAM = Math.floor(memory.jsHeapSizeLimit / (1024 * 1024));
        }
    }
    else if ('deviceMemory' in navigator) {
        // Device Memory API (more accurate)
        estimatedRAM = navigator.deviceMemory * 1024;
    }
    const isMobile = /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent);
    const hasInternet = navigator.onLine;
    // Recommend mode based on RAM
    let recommendedMode;
    if (estimatedRAM >= 1024) {
        recommendedMode = 'core';
    }
    else if (estimatedRAM >= 512) {
        recommendedMode = 'hybrid';
    }
    else {
        recommendedMode = 'flash';
    }
    return {
        ram: estimatedRAM,
        isMobile,
        hasInternet,
        recommendedMode
    };
}
/**
 * Get current AI configuration
 * Can be overridden by A/B test or user preference
 */
export async function getAIConfig() {
    const userPreference = localStorage.getItem('ai_mode');
    if (userPreference)
        return AI_CONFIGS[userPreference];
    // Try A/B Test first
    const experimentMode = localStorage.getItem('ab_test_ai_mode');
    if (experimentMode)
        return AI_CONFIGS[experimentMode];
    const capabilities = detectDeviceCapabilities();
    return AI_CONFIGS[capabilities.recommendedMode];
}
/**
 * Set user's AI mode preference
 */
export function setAIMode(mode) {
    localStorage.setItem('ai_mode', mode);
    window.location.reload(); // Reload to apply new config
}
/**
 * Get user-friendly description of current mode
 */
export function getAIModeDescription(mode) {
    const descriptions = {
        core: '200MB app, works 100% offline, highest power usage, >1GB RAM required',
        hybrid: '50MB app, on-device AI + cloud sync, balanced performance, 512MB RAM',
        flash: '30MB app, cloud-powered AI, fastest and lightest, 256MB RAM'
    };
    return descriptions[mode];
}
/**
 * Check if device meets minimum requirements for a mode
 */
export function canRunMode(mode) {
    const capabilities = detectDeviceCapabilities();
    const config = AI_CONFIGS[mode];
    return capabilities.ram >= config.limits.minRAM;
}
