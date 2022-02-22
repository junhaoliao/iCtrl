const {BrowserWindow, ipcMain} = require('electron');

module.exports = class ProgressBar {
  _options = {
    indeterminate: true,
    text: 'In progress',
    detail: '‎',
    value: 0,
    maximum: 0,
  };

  constructor(options, title, parent) {
    if (title){
      this._title = title;
    }
    for (const o in options) {
      this._options[o] = options[o];
    }

    this.window = new BrowserWindow({
      width: 500,
      height: 200,
      resizable: false,
      maximizable: false,
      fullscreenable: false,
      parent: parent,
      modal: true,
      webPreferences: {
        nativeWindowOpen: true,
        nodeIntegration: true,
        contextIsolation: false,
      },
    });
    this.resizeWindowListener = (event, arg) => {
      if (event.sender.id === this.window.webContents.id){
        this.window.setSize(500, arg);
      }
    }
    ipcMain.on('resize-window', this.resizeWindowListener);
    this.window.loadURL(`file://${__dirname}/progress_page/index.html`);
    // this.window.loadURL(`http://localhost:3000`);

    this.window.webContents.on('did-finish-load', () => {
      this.window.setTitle(this._title);
      for (const o in this._options) {
        this.window.webContents.send(o, this._options[o]);
      }
    });
  }

  _title = 'In progress';

  get title() {
    return this._title;
  }

  set title(newValue) {
    this._title = newValue;
    this.window.setTitle(newValue);
  }

  get text() {
    return this._options.text;
  }

  set text(newValue) {
    this._options.text = newValue;
    this.window.webContents.send('text', newValue);
  }

  get detail() {
    return this._options.detail;
  }

  set detail(newValue) {
    this._options.detail = newValue;
    this.window.webContents.send('detail', newValue);
  }

  get value() {
    return this._options.value;
  }

  set value(newValue) {
    this._options.value = newValue;
    this.window.webContents.send('value', newValue);
  }

  get maximum() {
    return this._options.maximum;
  }

  set maximum(newValue) {
    this._options.maximum = newValue;
    this.window.webContents.send('maximum', newValue);
  }

  get indeterminate() {
    return this._options.indeterminate;
  }

  set indeterminate(newValue) {
    this._options.indeterminate = newValue;
    this.window.webContents.send('indeterminate', newValue);
  }

  close = () => {
    this.window.close();
    this.window = null;
    ipcMain.removeListener('resize-window', this.resizeWindowListener)
  };

  show = ()=>{
    this.window.show();
  }
};
