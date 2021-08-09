require('update-electron-app')();
const {handleSquirrelEvent} = require('./squirrel_event');

// this should be placed at top of main.js to handle setup events quickly
if (handleSquirrelEvent()) {
    // squirrel event handled and app will exit in 1000ms, so don't do anything else
    return;
}

// Modules to control application life and create native browser window
const {app, BrowserWindow, nativeImage, Menu} = require('electron');
const {spawn} = require('child_process');
const {get} = require('http');
const {resolve} = require('path');

const {getFreePort} = require('./utils');

const mainPort = getFreePort();

const isMac = process.platform === 'darwin';

/* launch the backend and disable the menu bar*/
// the backend process handle
let ictrl_be = null;
if (isMac) {
    console.log(resolve(__dirname, 'ictrl_be'));
    ictrl_be = spawn('./ictrl_be', [mainPort], {cwd: resolve(__dirname, 'ictrl_be')});

    // need to have a 'window' role in the menu on mac
    //  to show all windows when right-clicking on the dock icon
    const menuTemplate = [{
        role: 'window',
        submenu: [
            {
                role: 'minimize'
            },
            {
                role: 'close'
            }
        ]
    }];
    Menu.setApplicationMenu(Menu.buildFromTemplate(menuTemplate));
} else {
    // TODO: add support for Linux
    // Assuming Windows
    ictrl_be = spawn('ictrl_be.exe', [mainPort], {cwd: resolve(__dirname, 'ictrl_be')});

    Menu.setApplicationMenu(null);
}


// This method will be called when Electron has finished
// initialization and is ready to create browser windows.
// Some APIs can only be used after this event occurs.
app.whenReady().then(() => {
    // Create the browser window.
    let mainWindow = new BrowserWindow({
        width: 800,
        height: 600,
        show: false,
        webPreferences: {
            nativeWindowOpen: true
        }
    });

    mainWindow.setTitle('Loading... ');

    mainWindow.loadURL(`http://127.0.0.1:${mainPort}`);
    // need to reload on Mac because the first load times out very quickly
    mainWindow.webContents.on('did-fail-load', () => {
        mainWindow.reload();
    });

    mainWindow.webContents.on('did-finish-load', () => {
        mainWindow.show();
        mainWindow.maximize();
    });

    const openedWindows = {};
    if (isMac) {
        // list to keep track of all opened windows for minimization into the Dock's "Recent Applications"
        openedWindows['main'] = mainWindow;
        mainWindow.on('close', () => {
            mainWindow = null;
            delete openedWindows['main'];
        });
        mainWindow.on('show', () => {
            for (let key in openedWindows) {
                if (key !== 'main') {
                    openedWindows[key].minimize();
                }
            }
        });
    } else {
        mainWindow.setAppDetails({
            appId: 'iCtrl'
        });
    }

    mainWindow.webContents.on('new-window', (event, url) => {
        event.preventDefault();

        const newWindow = new BrowserWindow({
            width: 800,
            height: 600,
            show: false,
            webPreferences: {
                nativeWindowOpen: true
            }
        });
        newWindow.loadURL(url);

        newWindow.once('ready-to-show', () => {
            // improve recognition of each window in the taskbar
            if (isMac) {
                const newWindowKey = new Date().getTime();
                openedWindows[newWindowKey] = newWindow;
                newWindow.on('close', () => {
                    delete openedWindows[newWindowKey];
                    if (mainWindow) {
                        mainWindow.show();
                    }
                });

                newWindow.on('show', () => {
                    for (let key in openedWindows) {
                        if (openedWindows[key] !== newWindow) {
                            openedWindows[key].minimize();
                        }
                    }
                });
            } else {
                const url = newWindow.getURL();
                newWindow.setAppDetails({
                    appId: url
                });
                const split = url.split('/');
                const sessionId = split[split.length - 1];
                const feature = split[split.length - 2];
                get({
                    hostname: '127.0.0.1',
                    port: mainPort,
                    path: `/favicon/${feature}/${sessionId}`,
                }, (res) => {
                    res.on('data', (data) => {
                        const icon = nativeImage.createFromBuffer(data);
                        newWindow.setIcon(icon);
                    });
                });
            }

            newWindow.show();
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

app.on('before-quit', () => {
    // kill the backend when the app exits
    ictrl_be.kill('SIGKILL');
});

// In this file you can include the rest of your app's specific main process
// code. You can also put them in separate files and require them here.
