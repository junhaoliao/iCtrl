require('update-electron-app')();
const {handleSquirrelEvent} = require('./squirrel_event');

// this should be placed at top of main.js to handle setup events quickly
if (handleSquirrelEvent()) {
  // squirrel event handled and app will exit in 1000ms, so don't do anything else
  return;
}

// Modules to control application life and create native browser window
const {app, BrowserWindow, Menu} = require('electron');
const {spawn} = require('child_process');
const {resolve} = require('path');

const {getFreePort} = require('./utils');

const mainPort = getFreePort();

const isMac = process.platform === 'darwin';
const isLinux = process.platform === 'linux';
const isWindows = process.platform === 'win32';

/* launch the backend and disable the menu bar*/
// the backend process handle
let ictrl_be = null;
if (isMac) {
  ictrl_be = spawn('./ictrl_be', [mainPort],
      {cwd: resolve(__dirname, 'ictrl_be')});

  // need to have a 'window' role in the menu on mac
  //  to show all windows when right-clicking on the dock icon
  const menuTemplate = [
    {
      role: 'window',
      submenu: [{role: 'minimize'}, {role: 'close'}],
    }];
  Menu.setApplicationMenu(Menu.buildFromTemplate(menuTemplate));
} else if (isWindows) {
  ictrl_be = spawn('ictrl_be.exe', [mainPort],
      {cwd: resolve(__dirname, 'ictrl_be')});
  Menu.setApplicationMenu(null);
} else if (isLinux) {
  ictrl_be = spawn('./ictrl_be', [mainPort],
      {cwd: resolve(__dirname, 'ictrl_be')});
  Menu.setApplicationMenu(null);
} else {
  console.log(`OS: ${process.platform} not supported.`);
  app.exit();
}

const setupNewWindowRecognitionMac = (openedWindows, newWindow, mainWindow) => {
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
};

function setupNewWindowIcon(url, newWindow) {
  const {nativeImage} = require('electron');
  const {get} = require('http');

  const split = url.split('/');
  const sessionId = split[split.length - 1];
  const feature = split[split.length - 2];
  get({
    hostname: '127.0.0.1',
    port: mainPort,
    path: `/api/favicon/${feature}/${sessionId}`,
  }, (msg) => {
    const result = [];

    msg.on('data', (data) => {
      result.push(data);
    });

    msg.on('end', () => {
      const icon = nativeImage.createFromBuffer(Buffer.concat(result));
      newWindow.setIcon(icon);
    });
  });
}

const setupNewWindowRecognitionWindows = newWindow => {
  const url = newWindow.getURL();
  newWindow.setAppDetails({
    appId: url,
  });
  setupNewWindowIcon(url, newWindow);
};

const setupNewWindowReadyToShow = (newWindow, openedWindows, mainWindow) => {
  newWindow.once('ready-to-show', () => {
    // improve recognition of each window in the taskbar
    if (isMac) {
      setupNewWindowRecognitionMac(openedWindows, newWindow, mainWindow);
    } else if (isWindows) {
      setupNewWindowRecognitionWindows(newWindow);
    }

    newWindow.show();
    newWindow.maximize();
  });
};

// This method will be called when Electron has finished
// initialization and is ready to create browser windows.
// Some APIs can only be used after this event occurs.
const windowOptions = {
  width: 800,
  height: 600,
  show: false,
  webPreferences: {
    nativeWindowOpen: true,
  },
};
app.whenReady().then(() => {
  // Create the browser window.
  let mainWindow = new BrowserWindow(windowOptions);

  // load backend dashboard
  mainWindow.setTitle('Loading... ');
  mainWindow.loadURL(`http://127.0.0.1:${mainPort}/dashboard`).then();
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
  } else if (isWindows) {
    mainWindow.setAppDetails({
      appId: 'iCtrl',
    });
  }

  mainWindow.webContents.on('new-window', (event, url) => {
    event.preventDefault();

    const newWindow = new BrowserWindow(windowOptions);
    newWindow.loadURL(url).then();
    setupNewWindowReadyToShow(newWindow, openedWindows, mainWindow);

  });

  // Open the DevTools.
  // mainWindow.webContents.openDevTools()
});

// Quit when all windows are closed
app.on('window-all-closed', () => {
  app.quit();
});

// kill the backend when the app exits
app.on('before-quit', () => {
  ictrl_be.kill('SIGTERM');

});

// in case the above is not successful,
//  force kill the backend when the process exits
process.on('exit', () => {
  ictrl_be.kill('SIGKILL');
});
