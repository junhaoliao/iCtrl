/*
 * Copyright (c) 2021-2022 iCtrl Developers
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy
 *  of this software and associated documentation files (the "Software"), to
 *  deal in the Software without restriction, including without limitation the
 *  rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
 *  sell copies of the Software, and to permit persons to whom the Software is
 *  furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included in
 *  all copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 *  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 *  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 *  AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 *  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
 *  FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
 *  IN THE SOFTWARE.
 */

import React from 'react';

import {
  Alert,
  Divider,
  Drawer,
  duration,
  Hidden,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Menu,
  MenuItem,
  Paper,
  Snackbar,
  Stack,
  SwipeableDrawer,
  Typography,
} from '@mui/material';
import {DataGrid} from '@mui/x-data-grid';

import CustomToolbar from './CustomToolbar';
import UploadToolbar from './UploadToolbar';
import UploadList from './UploadList';
import ChangePermission from '../../components/ChangePermission';
import columns from './columns';
import QuotaUsage from '../../components/QuotaUsage';
import {sftp_dl, sftp_ls, sftp_rename, sftp_ul} from '../../../actions/sftp';
import {isDir, isLnk} from './utils';
import {
  Add,
  Assignment,
  CloudDownload,
  Computer,
  CreateNewFolder,
  DeleteSweep,
  DesktopMac,
  DriveFolderUpload,
  FileUpload,
  Home,
  MusicNote,
  PhotoLibrary,
  UploadFile,
} from '@mui/icons-material';
import Button from '@mui/material/Button';
import NewFolderDialog from './NewFolderDialog';
import {updateTitleAndIcon} from '../../../actions/common';
import FileCleaner from '../../components/FileCleaner';
import BackgroundLetterAvatar from '../../components/BackgroundLetterAvatar';
import {COLOR_FILE_MANAGER} from '../../constants';

const drawerWidth = 200;

export default class FileManager extends React.Component {
  constructor(props) {
    super(props);

    this.feature = document.title = 'File Manager';

    this.changePermission = React.createRef();
    const {
      match: {params},
    } = props;

    this.session_id = params.session_id;

    this.clickTimeout = null;
    this.editEnter = null;
    this.state = {
      sessionNickname: '',
      alertOpen: false,
      alertMsg: null,
      changePermissionOpen: false,
      cwd: '',
      cwdInput: '',
      density: 'standard',
      files: [],
      fileCleanerOpen: false,
      loading: true,
      newMenuAnchorEl: null,
      newFolderDialogOpen: false,
      uploadWindowCollapsed: false,
      uploadProgress: [],
      showHidden: false,
      dragging: false,
      selectionModel: [],
      sortModel: [
        {
          field: 'id',
          sort: 'asc',
        }],
      editRowsModel: {},
      sideBarOpen: true,
    };
  }

  getNonHiddenFiles = (files) => {
    return files.filter((item) => {
      return !item.id.startsWith('.');
    });
  };

  loadDir = (path) => {
    this.setState({
      cwd: path,
      cwdInput: path,
    });
    sftp_ls(this, path);
  };

  handleSideBarOpen = () => {
    this.setState({sideBarOpen: true});
  };

  handleSideBarClose = () => {
    this.setState({sideBarOpen: false});
  };

  handleSelectionModelChange = (selectionModel) => {
    this.setState({
      selectionModel,
    });
  };

  clearSelection = () => {
    clearTimeout(this.clickTimeout);
    this.setState({
      selectionModel: [],
    });
  };

  handleCellClick = (params) => {
    const isMobile = document.body.clientWidth < 768;
    const {id, field} = params;
    const mode = params.row.mode;

    if (field === '__check__') {
      return;
    }

    if (isMobile) {
      this.enterSelection(id, mode);
    } else {
      const {selectionModel} = this.state;
      this.clearSelection();
      this.clickTimeout = setTimeout(() => {
        this.setState({id: id, mode: mode});
        if (field === 'id' && selectionModel.length === 1 &&
            selectionModel.includes(id)) {
          this.setState({
            editRowsModel: {
              [id]:
                  {
                    id: {
                      value: params.value,
                    },
                  },
            },
          });

          return;
        } else if (field === 'mode' && selectionModel.length === 1 &&
            selectionModel.includes(id)) {
          this.handleChangePermission(id, mode);
        }
        this.handleSelectionModelChange([id]);
      }, 500);
    }
  };

  handleChangePermission = (name, mode) => {
    if (mode === undefined) {
      const {files} = this.state;
      for (const item of files) {
        if (item.id === name) {
          mode = item.mode;
          break;
        }
      }
    }

    this.changePermission.current.updateRef(
        this.state.cwd,
        name,
        mode,
        this.session_id,
    );
    this.setState({changePermissionOpen: true});
  };

  enterSelection = (name, mode) => {
    const {cwd} = this.state;
    this.clearSelection();
    setTimeout(() => {
      this.setState({
        editRowsModel: {},
      });
    }, 0);
    if (isDir(mode) || isLnk(mode)) {
      // avoid two '/'s when loading at root
      this.loadDir(`${cwd === '/' ? '' : cwd}/${name}`);
    } else {
      sftp_dl(this.session_id, cwd, [name]);
    }
  };

  handleCellDoubleClick = (params) => {
    const name = params.row.id;
    const mode = params.row.mode;
    const {editRowsModel} = this.state;

    if (params.field === '__check__' || name in editRowsModel) {
      return;
    }

    this.enterSelection(name, mode);
  };

  handleCellEditCommit = (ev) => {
    this.handleChangeName(ev.id, ev.value);
  };

  handleEditRowsModelChange = (editRowsModel) => {
    this.setState({
      editRowsModel,
    });
  };

  handleChangeName = (oldName, newName) => {
    const {cwd} = this.state;

    // no name change
    if (oldName === newName) {
      return;
    }

    // given name empty
    if (newName === '') {
      this.showAlert('File name cannot be empty.');
      this.loadDir(cwd);
      return;
    }

    // check whether there is already a file or directory with the same name
    const duplicate_check = this.state.files.filter((row) => {
      return row.id === newName;
    });
    if (duplicate_check.length !== 0) {
      this.showAlert('File name duplicated!');
      return;
    }

    // do a POST to change the name
    this.setState({
      loading: true,
    });

    sftp_rename(this, this.session_id, this.state.cwd, oldName, newName);
  };

  handleAlertClose = (ev) => {
    // not triggered by the auto-hide timer
    // FIXME: it seems the timers are not cancelled even if any new alert opens.
    //  may use a counter to tell whether the alert should be hidden
    if (ev != null) {
      return;
    }

    this.setState({
      alertOpen: false,
      alertMsg: null,
    });
  };

  showAlert = (msg) => {
    this.setState({
      alertMsg: msg,
      alertOpen: true,
    });
  };

  handleNewFolderDialogOpen = (_) => {
    this.handleNewMenuClose();
    this.setState({newFolderDialogOpen: true});
  };
  handleNewFolderDialogClose = () => {
    this.setState({newFolderDialogOpen: false});
    this.loadDir(this.state.cwd);
  };

  handleNewMenuOpen = (_) => {
    this.setState({newMenuAnchorEl: document.getElementById('new-button')});
  };

  handleNewMenuClose = (_) => {
    this.setState({newMenuAnchorEl: null});
  };

  handleUpload = (isDirectory) => {
    this.handleNewMenuClose();
    const u = document.createElement('input');
    u.type = 'file';
    u.webkitdirectory = isDirectory;
    u.multiple = true;
    const clickFunc = (_) => {
      for (let i = 0; i < u.files.length; i++) {
        sftp_ul(this, this.session_id, this.state.cwd, u.files[i], isDirectory);

        // always scroll the latest item into the view
        const upload_paper = document.getElementById('upload_paper');
        upload_paper.scrollTop = upload_paper.scrollHeight;
      }
      u.removeEventListener('change', clickFunc);
    };
    u.addEventListener('change', clickFunc);
    u.click();
  };

  handleSortModelChange = (model) => {
    this.setState({sortModel: model});
  };

  handleDragEnter = (ev) => {
    ev.preventDefault();
    this.setState({
      dragging: true,
    });
  };

  handleDragLeave = (ev) => {
    ev.preventDefault();
    this.setState({
      dragging: false,
    });
  };

  handleDragOver = (ev) => {
    ev.preventDefault();
  };

  handleDragDrop = (ev) => {
    ev.preventDefault();
    this.setState({
      dragging: false,
    });
    const file = ev.dataTransfer.files[0];
    if (file !== undefined) {
      const {cwd} = this.state;
      const {isDirectory} = ev.dataTransfer.items[0].webkitGetAsEntry();
      sftp_ul(this, this.session_id, cwd, file, isDirectory);
    }
  };

  handleFileCleanerOpen = () => {
    this.setState({
      fileCleanerOpen: true,
    });
  };
  handleFileCleanerClose = () => {
    this.setState({
      fileCleanerOpen: false,
    });
  };

  componentDidMount() {
    updateTitleAndIcon(this);

    this.loadDir('');
  }

  render() {
    const {
      sessionNickname,
      sortModel,
      selectionModel,
      editRowsModel,
      files,
      showHidden,
      loading,
      sideBarOpen,
      dragging,
      fileCleanerOpen,
    } = this.state;
    const filesToShow = loading ?
        [] :
        (showHidden ? files : this.getNonHiddenFiles(files));

    const drawerChildren = <>
      <Button
          disabled={loading}
          id={'new-button'}
          onClick={this.handleNewMenuOpen}
          color={'primary'}
          style={{
            marginTop: 5,
            height: 40,
            marginLeft: 16,
            marginRight: 16,
            marginBottom: 8,
          }}
          variant={'contained'}
          startIcon={<Add/>}>
        <Typography variant={'subtitle1'}
                    fontWeight={'bolder'}>New</Typography>
      </Button>
      <Divider/>
      <List style={{width: drawerWidth}}>
        {[
          [<Home/>, 'Home', ''],
          [<DesktopMac/>, 'Desktop', 'Desktop'],
          [<Assignment/>, 'Documents', 'Documents'],
          [<CloudDownload/>, 'Downloads', 'Downloads'],
          [<MusicNote/>, 'Music', 'Music'],
          [<PhotoLibrary/>, 'Pictures', 'Pictures'],
          [<Computer/>, 'Root', '/'],
        ].map((item, _) => (
            <ListItem
                button
                disabled={loading}
                onClick={() => {
                  this.loadDir(item[2]);
                }}
                key={item[1]}>
              <ListItemIcon>
                {item[0]}
              </ListItemIcon>
              <ListItemText
                  primary={item[1]}/>
            </ListItem>
        ))}
        <Divider/>
        <ListItem button onClick={this.handleFileCleanerOpen}>
          <ListItemIcon>
            {<DeleteSweep/>}
          </ListItemIcon>
          <ListItemText
              primary={'File Cleaner'}/>
        </ListItem>
        <ListItem>
          <QuotaUsage sessionID={this.session_id}/>
        </ListItem>
      </List>
    </>;

    return (
        <div style={{overflowY: 'hidden'}}>
          <Hidden smUp>
            <SwipeableDrawer
                open={sideBarOpen}
                onOpen={this.handleSideBarOpen}
                onClose={this.handleSideBarClose}
                anchor={'left'}
                disableSwipeToOpen={true}
            >
              {drawerChildren}
            </SwipeableDrawer>
          </Hidden>
          <Hidden smDown>
            <Drawer
                open={true}
                anchor={'left'}
                variant={'permanent'}
            >
              {drawerChildren}
            </Drawer>
          </Hidden>
          <div
              onDragEnter={this.handleDragEnter}
              onDragLeave={this.handleDragLeave}
              onDragOver={this.handleDragOver}
              onDrop={this.handleDragDrop}
              style={{
                marginLeft: sideBarOpen ? `${drawerWidth}px` : null,
                height: '100vh',
              }}>
            {dragging ?
                <Stack style={{
                  height: '100%',
                  width: '100%',
                  justifyContent: 'center',
                  alignItems: 'center',
                  pointerEvents: 'none',
                }}>
                  <FileUpload style={{color: 'grey', fontSize: 100}}/>
                  <Typography variant={'h5'} style={{color: 'grey'}}>
                    Drop to upload
                  </Typography>
                </Stack>
                :
                <DataGrid
                    rows={filesToShow}
                    density={this.state.density}
                    columns={columns}
                    checkboxSelection
                    disableSelectionOnClick
                    disableColumnMenu
                    rowsPerPageOptions={[100]}
                    loading={this.state.loading}
                    onCellClick={this.handleCellClick}
                    onCellDoubleClick={this.handleCellDoubleClick}
                    onCellEditCommit={this.handleCellEditCommit}
                    editRowsModel={editRowsModel}
                    onEditRowsModelChange={this.handleEditRowsModelChange}
                    selectionModel={selectionModel}
                    sortModel={sortModel}
                    onSortModelChange={this.handleSortModelChange}
                    components={{
                      Toolbar: CustomToolbar,
                      NoRowsOverlay: (_ => (
                          <div style={{textAlign: 'center'}}>Empty
                            Directory</div>
                      )),
                    }}
                    componentsProps={{
                      toolbar: {fm: this},
                    }}
                    onSelectionModelChange={this.handleSelectionModelChange}
                />
            }
          </div>
          <Snackbar
              open={this.state.alertOpen}
              autoHideDuration={5000}
              onClose={this.handleAlertClose}
              anchorOrigin={{vertical: 'bottom', horizontal: 'center'}}
              transitionDuration={{
                enter: 2 * duration.enteringScreen,
                exit: 2 * duration.leavingScreen,
              }}
          >
            <Alert elevation={6} variant="filled" severity={'error'}>
              {this.state.alertMsg}
            </Alert>
          </Snackbar>
          <Snackbar
              open={this.state.uploadProgress.length !== 0}
              anchorOrigin={{vertical: 'bottom', horizontal: 'right'}}
          >
            <div style={{
              position: 'fixed',
              bottom: 55,
              right: 15,
              width: '300px',
            }}>
              <UploadToolbar fm={this}/>
              {!this.state.uploadWindowCollapsed &&
                  <Paper id="upload_paper"
                         style={{maxHeight: '180px', overflowY: 'auto'}}
                         variant="outlined"
                         square>
                    <UploadList fm={this}/>
                  </Paper>}
            </div>
          </Snackbar>
          <ChangePermission
              open={this.state.changePermissionOpen}
              fm={this}
              ref={this.changePermission}
          />
          <Menu
              open={Boolean(this.state.newMenuAnchorEl)}
              anchorEl={this.state.newMenuAnchorEl}
              onClose={this.handleNewMenuClose}
              transitionDuration={100}
          >
            <MenuItem key={'new-menu-folder'} style={{width: drawerWidth - 32}}
                      onClick={this.handleNewFolderDialogOpen}>
              <ListItemIcon>
                <CreateNewFolder/>
              </ListItemIcon>
              <ListItemText>Folder</ListItemText>
            </MenuItem>
            <Divider/>
            <MenuItem key={'new-menu-file-upload'} onClick={() => {
              this.handleUpload(false);
            }}>
              <ListItemIcon>
                <UploadFile/>
              </ListItemIcon>
              <ListItemText>File Upload</ListItemText>
            </MenuItem>
            <MenuItem key={'new-menu-folder-upload'} onClick={() => {
              this.handleUpload(true);
            }}>
              <ListItemIcon>
                <DriveFolderUpload/>
              </ListItemIcon>
              <ListItemText>Folder Upload</ListItemText>
            </MenuItem>
          </Menu>
          <NewFolderDialog
              open={this.state.newFolderDialogOpen}
              onClose={this.handleNewFolderDialogClose}
              sessionId={this.session_id}
              cwd={this.state.cwd}
          />
          {fileCleanerOpen && <FileCleaner
              sessionID={this.session_id}
              onClose={this.handleFileCleanerClose}/>}
          <div style={{position: 'absolute', top: 0, left: '-100px'}}
               id={'offscreen-favicon'}>
            <BackgroundLetterAvatar
                name={sessionNickname}
                badgeContent={<div style={{
                  width: '20px',
                  height: '20px',
                  backgroundColor: COLOR_FILE_MANAGER,
                }}
                />}
            />
          </div>
        </div>
    );
  }
}


