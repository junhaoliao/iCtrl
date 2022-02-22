require('update-electron-app')();
const {handleSquirrelEvent} = require('./squirrel_event');

// this should be placed at top of main.js to handle setup events quickly
if (handleSquirrelEvent()) {
  // squirrel event handled and app will exit in 1000ms, so don't do anything
  // else
  return;
}

// Modules to control application life and create native browser window
const {app, BrowserWindow, Menu} = require('electron');
const {spawn} = require('child_process');
const {resolve} = require('path');

const gotTheLock = app.requestSingleInstanceLock();
if (!gotTheLock) {
  console.log('Found another instance running. Exiting...');

  app.quit();
  process.exit();
}

const {getFreePort, humanFileSize} = require('./utils');
const ProgressBar = require('./ProgressBar');
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

const setupNewWindowIcon = (url, newWindow) => {
  const {nativeImage} = require('electron');
  const {get} = require('http');

  const url_split = url.split('/');
  const sessionId = url_split[url_split.length - 1];
  const feature = url_split[url_split.length - 2];
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
let mainWindow = null;

const createDashboardWindow = () => {
  // Create the dashboard window.
  mainWindow = new BrowserWindow(windowOptions);

  // load dashboard
  mainWindow.setTitle('Loading... ');
  mainWindow.loadURL(`http://127.0.0.1:${mainPort}/dashboard`);
  // need to reload on Mac because the first load times out very quickly
  mainWindow.webContents.on('did-fail-load', () => {
    mainWindow.reload();
  });
  mainWindow.webContents.on('did-finish-load', () => {
    mainWindow.show();
    mainWindow.maximize();
  });

  if (isWindows) {
    mainWindow.setAppDetails({
      appId: 'iCtrl',
    });
  }

  mainWindow.webContents.on('new-window', (event, url) => {
    event.preventDefault();

    const newWindow = new BrowserWindow(windowOptions);
    newWindow.loadURL(url);

    if (isWindows) {
      setupNewWindowIcon(url, newWindow);
    }
    newWindow.show();
    newWindow.maximize();

    newWindow.webContents.session.on('will-download',
        (event, item, webContents) => {
          const totalBytes = item.getTotalBytes();
          const fileName = item.getFilename();
          const indeterminate = totalBytes === 0;
          const progressBar = indeterminate ? new ProgressBar({
                indeterminate: true,
                text: `Downloading ${fileName}`,
              },
              `Downloading ${fileName}`,

          ) : new ProgressBar({
                indeterminate: false,
                text: `Downloading ${fileName}`,
                maximum: totalBytes,
              },
              `Downloading ${fileName}`,

          );

          let poppedAtLeastOnce = false;
          item.on('updated', (event, state) => {
            if (state === 'progressing') {
              const receivedBytes = item.getReceivedBytes();
              const totalBytes = item.getTotalBytes();
              const completedSaveDialog = item.getSavePath() !== '';

              const receivedBytesString = humanFileSize(receivedBytes);
              const totalBytesString = humanFileSize(totalBytes);

              progressBar.value = receivedBytes;
              progressBar.maximum = totalBytes;
              progressBar.detail = `${receivedBytesString} / ${totalBytesString} downloaded`;
              if (!poppedAtLeastOnce && completedSaveDialog) {
                progressBar.show();
                poppedAtLeastOnce = true;
              }
            }
          });
          item.once('done', (event, state) => {
            progressBar.close();
          });
        });
  });

  mainWindow.on('close', () => {
    mainWindow = null;
  });
};

app.whenReady().then(() => {
  createDashboardWindow();
  // Open the DevTools.
  // mainWindow.webContents.openDevTools()
});

// Show dashboard in this instance if the user tries to launch another instance
// The other instance will exit if it finds an already running instance: see
//  app.requestSingleInstanceLock() above
app.on('second-instance',
    (event, commandLine, workingDirectory, additionalData) => {
      if (mainWindow === null) {
        createDashboardWindow();
      }
      mainWindow.show();
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
