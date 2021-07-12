import React from 'react';

import {Alert, duration, Paper, Snackbar} from '@material-ui/core';
import {DataGrid} from '@material-ui/data-grid';

import CustomToolbar from './CustomToolbar';
import UploadToolbar from './UploadToolbar';
import UploadList from './UploadList';
import columns from './columns';
import {sftp_dl, sftp_ls, sftp_rename} from '../../../actions/sftp';
import {isDir} from './utils';


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

                document.body.onkeydown = (kd_ev) => {
                    if (kd_ev.key === 'Enter') {
                        ev.api.setCellMode(id, 'id', 'view');
                        if (this.editCellText !== '') {
                            this.handleChangeName(id, this.editCellText);
                        }
                    }
                };
                return;
            }
            ev.api.selectRow(id);
        }, 200);
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
                        field: 'mode',
                        sort: 'asc',
                    },
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
        </div>);
    }
}


