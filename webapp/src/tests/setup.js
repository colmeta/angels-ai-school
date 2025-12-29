import { afterEach } from 'vitest';
import { cleanup } from '@testing-library/react';
import '@testing-library/jest-dom/vitest';
// Cleanup after each test
afterEach(() => {
    cleanup();
});
// Mock IntersectionObserver
global.IntersectionObserver = class IntersectionObserver {
    constructor() { }
    disconnect() { }
    observe() { }
    takeRecords() {
        return [];
    }
    unobserve() { }
};
// Mock matchMedia
Object.defineProperty(window, 'matchMedia', {
    writable: true,
    value: (query) => ({
        matches: false,
        media: query,
        onchange: null,
        addListener: () => { },
        removeListener: () => { },
        addEventListener: () => { },
        removeEventListener: () => { },
        dispatchEvent: () => true,
    }),
});
// Mock localStorage
const localStorageMock = {
    getItem: (key) => null,
    setItem: (key, value) => { },
    removeItem: (key) => { },
    clear: () => { },
};
global.localStorage = localStorageMock;
// Mock fetch
global.fetch = async (input, init) => {
    return new Response(JSON.stringify({}), {
        status: 200,
        headers: { 'Content-Type': 'application/json' },
    });
};
