const { app, BrowserWindow, ipcMain, Menu } = require('electron');
const path = require('path');
const Store = require('electron-store');
const { autoUpdater } = require('electron-updater');

const store = new Store();

let mainWindow;

function createWindow() {
    mainWindow = new BrowserWindow({
        width: 1400,
        height: 900,
        minWidth: 1024,
        minHeight: 768,
        icon: path.join(__dirname, '../assets/icon.png'),
        webPreferences: {
            nodeIntegration: false,
            contextIsolation: true,
            preload: path.join(__dirname, 'preload.js'),
            webSecurity: true
        },
        backgroundColor: '#0f172a',
        show: false, // Show when ready
    });

    // Load the web app
    const isDev = process.env.NODE_ENV === 'development';

    if (isDev) {
        mainWindow.loadURL('http://localhost:3000');
        mainWindow.webContents.openDevTools();
    } else {
        mainWindow.loadFile(path.join(__dirname, '../webapp/dist/index.html'));
    }

    // Show when ready
    mainWindow.once('ready-to-show', () => {
        mainWindow.show();
    });

    // Handle window close
    mainWindow.on('closed', () => {
        mainWindow = null;
    });

    // Create application menu
    createMenu();

    // Check for updates (production only)
    if (!isDev) {
        checkForUpdates();
    }
}

function createMenu() {
    const template = [
        {
            label: 'File',
            submenu: [
                {
                    label: 'Sync Data',
                    accelerator: 'CmdOrCtrl+S',
                    click: () => {
                        mainWindow.webContents.send('sync-data');
                    }
                },
                { type: 'separator' },
                {
                    label: 'Exit',
                    accelerator: 'CmdOrCtrl+Q',
                    click: () => {
                        app.quit();
                    }
                }
            ]
        },
        {
            label: 'Edit',
            submenu: [
                { role: 'undo' },
                { role: 'redo' },
                { type: 'separator' },
                { role: 'cut' },
                { role: 'copy' },
                { role: 'paste' }
            ]
        },
        {
            label: 'View',
            submenu: [
                { role: 'reload' },
                { role: 'forceReload' },
                { type: 'separator' },
                { role: 'resetZoom' },
                { role: 'zoomIn' },
                { role: 'zoomOut' },
                { type: 'separator' },
                { role: 'togglefullscreen' }
            ]
        },
        {
            label: 'Help',
            submenu: [
                {
                    label: 'Documentation',
                    click: async () => {
                        const { shell } = require('electron');
                        await shell.openExternal('https://angels-ai.com/docs');
                    }
                },
                {
                    label: 'Check for Updates',
                    click: () => {
                        checkForUpdates();
                    }
                },
                { type: 'separator' },
                {
                    label: 'About',
                    click: () => {
                        const { dialog } = require('electron');
                        dialog.showMessageBox({
                            type: 'info',
                            title: 'Angels AI School',
                            message: 'Angels AI School Management',
                            detail: `Version: ${app.getVersion()}\nElectron: ${process.versions.electron}\nChrome: ${process.versions.chrome}\nNode: ${process.versions.node}`
                        });
                    }
                }
            ]
        }
    ];

    const menu = Menu.buildFromTemplate(template);
    Menu.setApplicationMenu(menu);
}

function checkForUpdates() {
    autoUpdater.checkForUpdatesAndNotify();
}

// IPC Handlers
ipcMain.handle('get-stored-data', async (event, key) => {
    return store.get(key);
});

ipcMain.handle('set-stored-data', async (event, key, value) => {
    store.set(key, value);
    return true;
});

ipcMain.handle('delete-stored-data', async (event, key) => {
    store.delete(key);
    return true;
});

ipcMain.handle('get-app-version', async () => {
    return app.getVersion();
});

// Auto-updater events
autoUpdater.on('update-available', () => {
    const { dialog } = require('electron');
    dialog.showMessageBox({
        type: 'info',
        title: 'Update Available',
        message: 'A new version is available. It will be downloaded in the background.',
    });
});

autoUpdater.on('update-downloaded', () => {
    const { dialog } = require('electron');
    dialog.showMessageBox({
        type: 'info',
        title: 'Update Ready',
        message: 'Update downloaded. Restart the app to install.',
        buttons: ['Restart', 'Later']
    }).then((result) => {
        if (result.response === 0) {
            autoUpdater.quitAndInstall();
        }
    });
});

// App lifecycle
app.whenReady().then(createWindow);

app.on('window-all-closed', () => {
    if (process.platform !== 'darwin') {
        app.quit();
    }
});

app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) {
        createWindow();
    }
});

// Handle offline/online events
app.on('browser-window-created', (event, window) => {
    window.webContents.on('did-fail-load', (event, errorCode, errorDescription) => {
        if (errorCode === -106) {
            // Network error - load offline page
            window.loadFile(path.join(__dirname, '../webapp/offline.html'));
        }
    });
});
