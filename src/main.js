require('update-electron-app')()
const profiler_start = Date.now()

// Modules to control application life and create native browser window
const {app, BrowserWindow, ipcMain} = require('electron')


// const path = require('path')

function createWindow() {
    // Create the browser window.
    const mainWindow = new BrowserWindow({
        width: 1440,
        height: 768,
        minWidth: 100,
        titleBarStyle: 'hidden',
        trafficLightPosition: {x: 16, y: 28},
        frame: false,
        show: false, 
        webPreferences: {
            // preload: path.join(__dirname, 'preload.js'),
            nodeIntegration: true,
            nodeIntegrationInWorker: true,
            contextIsolation: false,
            // devTools: false
        }
    })
    mainWindow.maximize()


    // Open the DevTools.
    // mainWindow.webContents.openDevTools()

    ipcMain.on("profiler_sync_ack", () => {
        if (process.platform === "darwin"){
            app.dock.bounce()
        }
        mainWindow.show()

        console.log("Load Time:", Date.now() - profiler_start, "s")
    })

    // and load the index.html of the app.
    // mainWindow.loadFile('debugger.html')
    mainWindow.loadFile('src/index.html').then(() => {
        ipcMain.on("close", () => {
            mainWindow.close()
        })
        ipcMain.on("min", () => {
            mainWindow.minimize()
        })
        ipcMain.on("max", () => {
            if (mainWindow.isMaximized()) {
                mainWindow.restore()
            } else {
                mainWindow.maximize()
            }
        })
    })

    // ipcMain.on("fullscreen", ()=>{
    //     mainWindow.setFullScreen(!mainWindow.fullScreen)
    // })
    // ipcMain.on("restore", ()=>{
    //     mainWindow.restore()
    // })

}

// This method will be called when Electron has finished
// initialization and is ready to create browser windows.
// Some APIs can only be used after this event occurs.
app.whenReady().then(() => {
    createWindow()

    // app.on('activate', function () {
    //   // On macOS it's common to re-create a window in the app when the
    //   // dock icon is clicked and there are no other windows open.
    //   if (BrowserWindow.getAllWindows().length === 0) createWindow()
    // })
})

// Quit when all windows are closed, except on macOS. There, it's common
// for applications and their menu bar to stay active until the user quits
// explicitly with Cmd + Q.
app.on('window-all-closed', function () {
    app.quit()
})

// In this file you can include the rest of your app's specific main process
// code. You can also put them in separate files and require them here.
