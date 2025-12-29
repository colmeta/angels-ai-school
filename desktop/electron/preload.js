const { contextBridge, ipcRenderer } = require('electron');

// Expose protected methods to renderer process
contextBridge.exposeInMainWorld('electronAPI', {
    // Local storage
    getStoredData: (key) => ipcRenderer.invoke('get-stored-data', key),
    setStoredData: (key, value) => ipcRenderer.invoke('set-stored-data', key, value),
    deleteStoredData: (key) => ipcRenderer.invoke('delete-stored-data', key),

    // App info
    getAppVersion: () => ipcRenderer.invoke('get-app-version'),

    // Sync events
    onSyncData: (callback) => ipcRenderer.on('sync-data', callback),

    // Platform info
    platform: process.platform,
    isDesktop: true
});
