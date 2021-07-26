/* eslint-disable react-hooks/rules-of-hooks */
import React from 'react';
import {Button, Dialog, DialogActions, DialogContent, DialogTitle,} from '@material-ui/core';
import {DataGrid} from '@material-ui/data-grid';
import columns from './column';
import {session_change_host, session_ruptime} from '../../../actions/session';

export default class ChangeMachine extends React.Component {
    constructor(props) {
        super(props);


        this.state = {
            selectedHost: null,
            machineList: [],
        };
    }

    handleSubmit() {
        session_change_host(this.props.session_id, this.state.selectedHost, this.props.domain);
    };

    handleClose = (ev) => {
        if (ev.target && ev.target.id === 'button_apply') {
            this.handleSubmit();
        }

        this.props.onChangeMenuClose();
    };

    handleSave() {
        this.handleClose();
    }

    handleRowClick = (ev) => {
        this.setState({
            selectedHost: ev.row.id
        });
    };

    componentDidMount() {
        session_ruptime(this.props.session_id, this);
    }

    render() {
        const {machineList} = this.state;

        return (
            <Dialog
                open={true}
                fullWidth={true}
                maxWidth={'md'}
                aria-labelledby="change machine"
            >
                <DialogTitle>Change Machine</DialogTitle>
                <DialogContent style={{height: '380px'}}>
                    <DataGrid
                        rows={machineList}
                        columns={columns}
                        pageSize={100}
                        rowsPerPageOptions={[]}
                        loading={!machineList.length}
                        onRowClick={this.handleRowClick}
                        sortModel={[
                            {field: 'userNum', sort: 'asc'},
                            {field: 'load15', sort: 'asc'},
                            {field: 'load5', sort: 'asc'},
                            {field: 'load1', sort: 'asc'},
                        ]}
                        hideFooter={machineList.length <= 100}
                    />
                </DialogContent>
                <DialogActions>
                    <Button onClick={this.handleClose}>Close</Button>
                    <Button id={'button_apply'}
                            variant={'contained'}
                            disabled={!Boolean(this.state.selectedHost)}
                            onClick={this.handleClose}>
                        Apply
                    </Button>
                </DialogActions>
            </Dialog>
        );
    }
}