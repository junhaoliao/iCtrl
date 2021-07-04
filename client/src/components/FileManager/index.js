import React from 'react';

import {DataGrid} from '@material-ui/data-grid';
import FolderIcon from '@material-ui/icons/Folder';
import InsertDriveFileIcon from '@material-ui/icons/InsertDriveFile';
import {duration, Grid, Paper, Snackbar} from '@material-ui/core';
import MuiAlert from '@material-ui/lab/Alert';

import CustomToolbar from './CustomToolbar';
import * as constants from './constants';
import {ShortcutIcon} from '../../icons';
import UploadToolbar from './UploadToolbar';
import UploadList from './UploadList';
import {humanFileSize} from './utils';

const dateFormatter = (params) => {
    const theDate = new Date(params.value * 1000);
    const dateOptions = {year: 'numeric', month: 'short', day: 'numeric'};
    const timeOptions = {hour: '2-digit', minute: '2-digit'};

    return `${theDate.toLocaleDateString('en-US', dateOptions)} 
                        at ${theDate.toLocaleTimeString('en-US', timeOptions)}`;
};

const permissionFormatter = (params) => {
    const mode = parseInt(params.value);
    const mode_str_arr = [
        (mode & constants.S_IFDIR) ? 'd' : '-',
        (mode & constants.S_IRUSR) ? 'r' : '-',
        (mode & constants.S_IWUSR) ? 'w' : '-',
        (mode & constants.S_IXUSR) ? 'x' : '-',
        (mode & constants.S_IRGRP) ? 'r' : '-',
        (mode & constants.S_IWGRP) ? 'w' : '-',
        (mode & constants.S_IXGRP) ? 'x' : '-',
        (mode & constants.S_IROTH) ? 'r' : '-',
        (mode & constants.S_IWOTH) ? 'w' : '-',
        (mode & constants.S_IXOTH) ? 'x' : '-'
    ];
    return mode_str_arr.join('');
};


const isDir = (mode) => {
    return (parseInt(mode) & constants.S_IFMT) === constants.S_IFDIR;
};
const isLnk = (mode) => {
    return (parseInt(mode) & constants.S_IFMT) === constants.S_IFLNK;
};


const columns = [
    {
        field: 'id', headerName: 'Name', flex: 1,
        renderCell: (params) => {
            const is_dir = isDir(params.getValue(params.value, 'mode'));
            const is_lnk = isLnk(params.getValue(params.value, 'mode'));
            return (
                <Grid container spacing={1}>
                    <Grid item style={{position: 'relative', top: 5}}>
                        {is_lnk ? <ShortcutIcon/> : (is_dir ? <FolderIcon fontSize={'small'}/> :
                            <InsertDriveFileIcon fontSize={'small'}/>)}
                    </Grid>
                    <Grid item>{params.value}</Grid>
                </Grid>

            );
        }
    },
    {
        field: 'size', headerName: 'Size', width: 90,
        valueFormatter: (params) => {
            const valueFormatted = humanFileSize(params.value).toLocaleString();
            return `${valueFormatted}`;
        }
    },
    {
        field: 'atime', headerName: 'Date Accessed', width: 188,
        valueFormatter: dateFormatter
    },
    {
        field: 'mtime', headerName: 'Date Modified', width: 188,
        valueFormatter: dateFormatter
    },
    {
        field: 'mode', headerName: 'Permission', width: 132,
        valueFormatter: permissionFormatter
    },
];

export default class FileManager extends React.Component {
    constructor(props) {
        super(props);
        const {
            match: {params},
            profiles: {sessions}
        } = props;

        this.session_id = params.session_id;
        this.username = sessions[this.session_id].username;
        this.host = sessions[this.session_id].host;

        this.showHidden = false;
        this.files = [];
        this.selected = [];
        this.clickTimeout = null;
        this.editEnter = null;
        this.editCellText = '';
        this.state = {
            alertOpen: false,
            alertMsg: null,
            cwd: '',
            cwdInput: '',
            density: 'standard',
            filesDisplaying: [],
            loading: true,
            uploadWindowCollapsed: false,
            uploadProgress: []
        };
        // FIXME: change uploadWindowOpen -> false  by default
    }

    nonHiddenFiles() {
        return this.files.filter((item) => {
            return !item.id.startsWith('.');
        });
    }

    loadDir = (path) => {
        this.setState({
            loading: true,
            alertMsg: null,
            alertOpen: false
        });

        const request = new XMLHttpRequest();
        request.addEventListener('load', (_) => {
            const resp = JSON.parse(request.response);
            if (resp.status === true) {
                this.files = resp.files;

                this.setState({
                    cwd: resp.cwd,
                    cwdInput: resp.cwd,
                    filesDisplaying: this.showHidden ? this.files : this.nonHiddenFiles(),
                    loading: false
                });
                this.forceUpdate();
            } else {
                this.setState({
                    alertMsg: resp.cwd,
                    alertOpen: true,
                    loading: false
                });
            }
        });
        request.open('GET', `/sftp_ls/${this.session_id}?path=${path}`);
        request.send();
    };

    componentDidMount() {
        document.title = `${this.username}@${this.host} - File Manager`;
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
            if (ev.field === 'id' && curr_selected.length === 1 && curr_selected.includes(id)) {
                ev.api.setCellMode(id, 'id', 'edit');
                document.addEventListener('keypress', (kp_ev) => {
                    if (kp_ev.key === 'Enter') {
                        ev.api.setCellMode(id, 'id', 'view');
                        if (this.editCellText !== '') {
                            this.handleChangeName(id, this.editCellText);
                        }

                    }
                });
                return;
            }
            ev.api.selectRow(id);
        }, 300);
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
            const a = document.createElement('a');
            a.download = '';
            a.href = `http://localhost:5000/sftp_dl/${this.session_id}?` +
                `cwd=${this.state.cwd}&` +
                `files=${JSON.stringify([name])}`;
            a.click();
        }

    };

    handleEditCellChange = (ev) => {
        this.editCellText = ev.props.value;
    };

    handleChangeName = (old_name, new_name) => {
        this.editCellText = '';
        document.removeEventListener('keypress', () => {
        });

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
        const request = new XMLHttpRequest();
        request.addEventListener('load', (_) => {
            this.loadDir(this.state.cwd);
        });
        request.open('GET', `/sftp_rename/${this.session_id}?` +
            `cwd=${this.state.cwd}&` +
            `old=${old_name}&` +
            `new=${new_name}`
        );
        request.send();
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

    render() {
        return (<div style={{height: '100vh', minWidth: 900}}>
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
                }}
                componentsProps={{
                    toolbar: {fm: this}
                }}
                onSelectionModelChange={this.handleSelectionModelChange}
            />
            <Snackbar
                open={this.state.alertOpen}
                autoHideDuration={3000}
                onClose={this.handleAlertClose}
                anchorOrigin={{vertical: 'bottom', horizontal: 'center'}}
                transitionDuration={{enter: 2 * duration.enteringScreen, exit: 2 * duration.leavingScreen,}}
            >
                <MuiAlert elevation={6} variant="filled" severity={'error'}>
                    {this.state.alertMsg}
                </MuiAlert>
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
        </div>);
    }
}


