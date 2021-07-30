require('update-electron-app')()
const {handleSquirrelEvent} = require('./squirrel_event')

// this should be placed at top of main.js to handle setup events quickly
if (handleSquirrelEvent()) {
  // squirrel event handled and app will exit in 1000ms, so don't do anything else
  return;
}

// Modules to control application life and create native browser window
const {app, BrowserWindow, nativeImage} = require('electron');
const {spawn} = require('child_process');
const {get} = require('http');
const {resolve} = require('path');

const {getFreePort} = require('./utils');

const mainPort = getFreePort();

// launch the backend
spawn('ictrl_be.exe', [mainPort], {cwd: resolve(__dirname, 'ictrl_be')});

// This method will be called when Electron has finished
// initialization and is ready to create browser windows.
// Some APIs can only be used after this event occurs.
app.whenReady().then(() => {
    // Create the browser window.
    const mainWindow = new BrowserWindow({
        width: 800,
        height: 600,
        show: false,
        autoHideMenuBar: true,
        webPreferences: {
            nativeWindowOpen: true
        }
    });

    mainWindow.loadURL(`http://localhost:${mainPort}`);

    mainWindow.removeMenu();
    mainWindow.setAppDetails({
        appId: 'iCtrl'
    });

    mainWindow.once('ready-to-show', () => {
        mainWindow.maximize();
    });

    mainWindow.webContents.on('new-window', (event, url) => {
        event.preventDefault();

        const newWindow = new BrowserWindow({
            width: 800,
            height: 600,
            show: false,
            autoHideMenuBar: true,
            webPreferences: {
                nativeWindowOpen: true
            }
        });
        newWindow.loadURL(url);

        newWindow.removeMenu();
        newWindow.once('ready-to-show', () => {
            const url = newWindow.getURL();
            newWindow.setAppDetails({
                appId: url
            });
            const split = url.split('/');
            const sessionId = split[split.length - 1];
            const feature = split[split.length - 2];
            get({
                hostname: 'localhost',
                port: mainPort,
                path: `/favicon/${feature}/${sessionId}`,
            }, (res) => {
                res.on('data', (data) => {
                    const icon = nativeImage.createFromBuffer(data);
                    newWindow.setIcon(icon);
                });
            });

            newWindow.maximize();
        });

    });

    // Open the DevTools.
    // mainWindow.webContents.openDevTools()
});

// Quit when all windows are closed, except on macOS. There, it's common
// for applications and their menu bar to stay active until the user quits
// explicitly with Cmd + Q.
app.on('window-all-closed', () => {
    app.quit();
});

// In this file you can include the rest of your app's specific main process
// code. You can also put them in separate files and require them here.
