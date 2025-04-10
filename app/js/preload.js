const { contextBridge, ipcRenderer, shell } = require('electron');

contextBridge.exposeInMainWorld('electronShell', {
    openExternal: (url) => shell.openExternal(url)
});

// Basic general-purpose invokers (logs, clients)
contextBridge.exposeInMainWorld('electron', {
    getLogs: (service, lines) => ipcRenderer.invoke('get-logs', service, lines),
    checkClients: () => ipcRenderer.invoke('check-clients'),
    invoke: (channel, ...args) => ipcRenderer.invoke(channel, ...args),
});

// Main app communication
contextBridge.exposeInMainWorld('api', {
    // UI Actions
    openUpdatePopup: () => ipcRenderer.send('open-update-popup'),
    sendUpdateStart: (settings) => ipcRenderer.send('start-update', settings),
    sendDashboardStart: () => ipcRenderer.send('minidash-start'),
    sendJournalsStart: () => ipcRenderer.send('journals-start'),
    quitApp: () => ipcRenderer.send('quit-app'),

    // IPC listeners (used for installed/latest versions etc.)
    receive: (channel, func) => {
        ipcRenderer.on(channel, (event, ...args) => func(...args));
    }
});

// Service & sudo controls
contextBridge.exposeInMainWorld('electronAPI', {
    getStatus: (serviceName) => ipcRenderer.invoke('get-status', serviceName),
    checkServicesStatus: () => ipcRenderer.invoke('get-running-services'),
    startServices: (settings) => ipcRenderer.send('startServices', settings),
    stopServices: (settings) => ipcRenderer.send('stopServices', settings),
    requireSudo: () => ipcRenderer.invoke('check-sudo-privileges'),
    notifySudoRequired: (callback) => {
        ipcRenderer.on('sudo-required', (event, message) => callback(message));
    },
    receive: (channel, func) => {
        const validChannels = [
            'get-latest-versions', 'minidash-settings', 'get-installed-versions',
            'update-settings', 'process-output', 'process-complete', 'sudo-required'
        ];
        if (validChannels.includes(channel)) {
            ipcRenderer.on(channel, (event, ...args) => func(...args));
        }
    },
});
