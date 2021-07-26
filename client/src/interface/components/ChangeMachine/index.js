/* eslint-disable react-hooks/rules-of-hooks */
import React from 'react';
import {
    Button,
    Dialog,
    DialogActions,
    DialogContent,
    DialogTitle,
} from '@material-ui/core';
import {DataGrid} from '@material-ui/data-grid';
import columns from './column'
import { sftp_ruptime, sftp_changehost } from '../../../actions/sftp';

export default class ChangeMachine extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            machineList: [],
            machineNum: -1,
            sessionId: '',
        };
    }

    handleSubmit() {
        if (this.state.machineNum !== -1) {
            sftp_changehost(this.state.sessionId, this.state.machineNum)
        }
    };

    handleClose = (ev) => {
        if (ev.target && ev.target.id === 'button_apply') {
            this.handleSubmit();
        }

        this.props.db.setState({
            changeMachineOpen: false
        });
    };

    handleSave() {
        this.handleClose();
    }

    handleRowClick = (ev) => {
        this.setState({machineNum: ev.row.id})
    }

    update_machine_list(_sessionId) {
        this.setState({sessionId: _sessionId})
        sftp_ruptime(_sessionId, this);
    }

    render() {
        const {open} = this.props;
        return (
            <Dialog
                open={open}
                fullWidth={true}
                maxWidth={"md"}
                aria-labelledby="change machine"
            >
                <DialogTitle>Change Machine</DialogTitle>
                <DialogContent style={{ height: "380px" }}>
                    <DataGrid
                        rows={this.state.machineList}
                        columns={columns}
                        pageSize={100}
                        loading={this.state.machineList.length ? false : true}
                        onRowClick={this.handleRowClick}
                        rowsPerPageOptions={[]}
                        sortModel={[
                            {
                                field: 'userNum',
                                sort: 'asc',
                            },
                            {
                                field: 'load15',
                                sort: 'asc',
                            }
                        ]}
                        hideFooter
                    />
                </DialogContent>
                <DialogActions>
                    <Button onClick={this.handleClose}>Close</Button>
                    <Button variant={'contained'}
                            id={'button_apply'}
                            onClick={this.handleClose}>
                        Apply
                    </Button>
                    </DialogActions>
            </Dialog>
        );
    }
}