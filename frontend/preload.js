const { contextBridge, ipcRenderer } = require('electron');

contextBridge.exposeInMainWorld('electronAPI', {
  setOpacity: (val) => ipcRenderer.send('set-opacity', val),
  setClickThrough: (enable) => ipcRenderer.send('set-click-through', enable),
  minimizeApp: () => ipcRenderer.send('minimize-app'),
  closeApp: () => ipcRenderer.send('close-app'),
  onClickThroughToggled: (callback) => ipcRenderer.on('click-through-toggled', (_event, value) => callback(value))
});
