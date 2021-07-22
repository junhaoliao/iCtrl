import React from 'react';

import {
    Alert,
    Divider,
    Drawer,
    duration,
    List,
    ListItem,
    ListItemIcon,
    ListItemText,
    Menu,
    MenuItem,
    Paper,
    Snackbar,
    Typography
} from '@material-ui/core';
import {DataGrid} from '@material-ui/data-grid';

import CustomToolbar from './CustomToolbar';
import UploadToolbar from './UploadToolbar';
import UploadList from './UploadList';
import ChangePermission from '../../components/ChangePermission';
import columns from './columns';
import MemoryUsage from '../../components/MemoryUsage';
import {sftp_dl, sftp_ls, sftp_rename, sftp_ul} from '../../../actions/sftp';
import {isDir} from './utils';
import {Helmet, HelmetProvider} from 'react-helmet-async';
import {
    Add,
    Assignment,
    CloudDownload,
    Computer,
    CreateNewFolder,
    DesktopMac,
    DriveFolderUpload,
    FilterDrama,
    Home,
    MusicNote,
    PhotoLibrary,
    UploadFile
} from '@material-ui/icons';
import Button from '@material-ui/core/Button';
import NewFolderDialog from './NewFolderDialog';

const drawerWidth = 200;

export default class FileManager extends React.Component {
    constructor(props) {
        super(props);
        this.changePermission = React.createRef();
        const {
            match: {params}
        } = props;

        this.session_id = params.session_id;

        this.showHidden = false;
        this.files = [];
        this.selected = [];
        this.clickTimeout = null;
        this.editEnter = null;
        this.editCellText = '';
        this.state = {
            alertOpen: false,
            alertMsg: null,
            changePermissionOpen: false,
            cwd: '',
            cwdInput: '',
            density: 'standard',
            filesDisplaying: [],
            loading: true,
            newMenuAnchorEl: null,
            newFolderDialogOpen: false,
            uploadWindowCollapsed: false,
            uploadProgress: []
        };
    }

    nonHiddenFiles = () => {
        return this.files.filter((item) => {
            return !item.id.startsWith('.');
        });
    };

    loadDir = (path) => {
        sftp_ls(this, path);
    };

    componentDidMount() {
        this.loadDir('');
    }

    handleSelectionModelChange = (ev) => {
        this.selected = ev.selectionModel;
    };

    clearSelection = (api) => {
        clearTimeout(this.clickTimeout);
        api.selectRows([], true, true);
    };

    handleCellClick = (ev) => {
        this.api = ev.api;
        const curr_selected = this.selected;

        // if (ev.row.id in ev.api.getSelectedRows().keys()){
        //     console.log('hi')
        // }
        this.clearSelection(ev.api);
        this.clickTimeout = setTimeout(() => {
            const id = ev.row.id;
            this.setState({id: ev.row.id, mode: ev.row.mode});
            if (ev.field === 'id' && curr_selected.length === 1 && curr_selected.includes(id)) {
                ev.api.setCellMode(id, 'id', 'edit');

                document.body.onkeydown = (kd_ev) => {
                    if (kd_ev.key === 'Enter') {
                        ev.api.setCellMode(id, 'id', 'view');
                        if (this.editCellText !== '') {
                            this.handleChangeName(id, this.editCellText);
                        }
                    }
                };
                return;
            } else if (ev.field === 'mode' && curr_selected.length === 1 && curr_selected.includes(id)) {
                this.handleChangePermission(ev.row.id, ev.row.mode);
            }
            ev.api.selectRow(id);
        }, 200);
    };

    handleChangePermission = (name, mode) => {
        this.changePermission.current.update_id_mode(this.state.cwd, name, mode, this.session_id);
        this.setState({changePermissionOpen: true});
    };

    handleRowDoubleClick = (ev) => {
        const name = ev.row.id;
        if (ev.api.getCellMode(name, 'id') === 'edit') {
            return;
        }

        this.clearSelection(ev.api);
        const mode = ev.row.mode;

        const ir_dir = isDir(mode);
        if (ir_dir) {
            this.loadDir(`${this.state.cwd}/${name}`);
        } else {
            sftp_dl(this.session_id, this.state.cwd, [name]);
        }

    };

    handleEditCellChange = (ev) => {
        this.editCellText = ev.props.value;
    };

    handleChangeName = (old_name, new_name) => {
        this.editCellText = '';

        // no name change
        if (old_name === new_name) {
            return;
        }

        // given name empty
        if (new_name === '') {
            this.showAlert('File name cannot be empty.');
            this.loadDir(this.state.cwd);
            return;
        }

        // check whether there is already a file or directory with the same name
        const duplicate_check = this.files.filter((row) => {
            return row.id === new_name;
        });
        if (duplicate_check.length !== 0) {
            this.showAlert('File name duplicated!');
            return;
        }

        // remove the old row and do a POST to change the name
        this.setState({
            filesDisplaying: this.state.filesDisplaying.filter((row) => {
                return row.id !== old_name;
            })
        });

        sftp_rename(this, this.session_id, this.state.cwd, old_name, new_name);
    };

    handleEditCellChangeCommitted = (ev) => {
        const old_name = ev.id;
        const new_name = ev.props.value;
        this.handleChangeName(old_name, new_name);
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
            alertMsg: null
        });
    };

    showAlert = (msg) => {
        this.setState({
            alertMsg: msg,
            alertOpen: true
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

    render() {
        const {host, username} = this.props.profiles.sessions[this.session_id];
        return (
            <div style={{overflowY: 'hidden'}}>
                <HelmetProvider>
                    <Helmet>
                        <title>{`File Manager - ${username}@${host}`}</title>
                        <link rel="icon" href={`/favicon/fm/${this.session_id}`}/>
                    </Helmet>
                </HelmetProvider>
                <Drawer open variant={'persistent'} anchor={'left'}>
                    <Button
                        id={'new-button'}
                        onClick={this.handleNewMenuOpen}
                        color={'primary'}
                        style={{marginTop: 5, height: 40, marginLeft: 16, marginRight: 16, marginBottom: 8}}
                        variant={'contained'}
                        startIcon={<Add/>}>
                        <Typography variant={'subtitle1'} fontWeight={'bolder'}>New</Typography>
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
                        ].map((item, index) => (
                            <ListItem
                                button
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
                        <ListItem>
                            <ListItemIcon>
                                <FilterDrama/>
                            </ListItemIcon>
                            <ListItemText primary="Storage"/>
                        </ListItem>
                        <ListItem>
                            <MemoryUsage fm={this}/>
                        </ListItem>
                    </List>
                </Drawer>
                <div style={{marginLeft: `${drawerWidth}px`, height: '100vh'}}>
                    <DataGrid
                        rows={this.state.filesDisplaying}
                        density={this.state.density}
                        columns={columns}
                        checkboxSelection
                        disableSelectionOnClick
                        disableColumnMenu
                        rowsPerPageOptions={[]}
                        loading={this.state.loading}
                        onCellClick={this.handleCellClick}
                        onRowDoubleClick={this.handleRowDoubleClick}
                        onEditCellChange={this.handleEditCellChange}
                        onEditCellChangeCommitted={this.handleEditCellChangeCommitted}
                        sortModel={[
                            {
                                field: 'id',
                                sort: 'asc',
                            }]}
                        components={{
                            Toolbar: CustomToolbar,
                            NoRowsOverlay: (_ => (
                                <div style={{margin: 'auto'}}>Empty Directory</div>
                            ))
                        }}
                        componentsProps={{
                            toolbar: {fm: this}
                        }}
                        onSelectionModelChange={this.handleSelectionModelChange}
                    />
                </div>
                <Snackbar
                    open={this.state.alertOpen}
                    autoHideDuration={5000}
                    onClose={this.handleAlertClose}
                    anchorOrigin={{vertical: 'bottom', horizontal: 'center'}}
                    transitionDuration={{enter: 2 * duration.enteringScreen, exit: 2 * duration.leavingScreen,}}
                >
                    <Alert elevation={6} variant="filled" severity={'error'}>
                        {this.state.alertMsg}
                    </Alert>
                </Snackbar>
                <Snackbar
                    open={this.state.uploadProgress.length !== 0}
                    anchorOrigin={{vertical: 'bottom', horizontal: 'right'}}
                >
                    <div style={{position: 'fixed', bottom: 55, right: 15}}>
                        <UploadToolbar fm={this}/>
                        {!this.state.uploadWindowCollapsed &&
                        <Paper id="upload_paper"
                               style={{maxHeight: 180, overflowY: 'auto'}}
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
            </div>
        );
    }
}


