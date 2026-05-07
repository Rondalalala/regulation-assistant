const { app, BrowserWindow } = require('electron');
const path = require('path');
const { createLocalServer } = require('./server.cjs');

let mainWindow;
let server;

const DIST_PATH = path.join(__dirname, '..', 'dist');
const SERVER_PORT = 8080;

async function createWindow() {
  try {
    server = await createLocalServer(DIST_PATH, SERVER_PORT);
  } catch (err) {
    console.error('[main] failed to start server:', err);
    app.quit();
    return;
  }

  mainWindow = new BrowserWindow({
    width: 1400,
    height: 900,
    minWidth: 1000,
    minHeight: 700,
    title: '西北投资制度助手 v2.1',
    webPreferences: {
      preload: path.join(__dirname, 'preload.cjs'),
      contextIsolation: true,
      nodeIntegration: false,
    },
  });

  mainWindow.loadURL(`http://127.0.0.1:${SERVER_PORT}`);

  mainWindow.on('closed', () => {
    mainWindow = null;
  });
}

app.whenReady().then(createWindow);

app.on('window-all-closed', () => {
  if (server) {
    server.close(() => {
      console.log('[main] server closed');
    });
  }
  if (process.platform !== 'darwin') {
    app.quit();
  }
});

app.on('activate', () => {
  if (BrowserWindow.getAllWindows().length === 0) {
    createWindow();
  }
});
