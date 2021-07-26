/* eslint-disable react-hooks/rules-of-hooks */
import React from 'react';
import {Button, Dialog, DialogActions, DialogContent, DialogTitle,} from '@material-ui/core';
import {DataGrid} from '@material-ui/data-grid';
import columns from './column';
import {session_change_host, session_ruptime} from '../../../actions/session';
import axios from 'axios';

export default class ChangeMachine extends React.Component {
    constructor(props) {
        super(props);
        this.cancelTokenSrc = axios.CancelToken.source();

        this.state = {
            selectedHost: null,
            machineList: [],
        };
    }


    handleClose = (ev) => {
        if (ev.target && ev.target.id === 'button_apply') {
            session_change_host(this.props.session_id, this.state.selectedHost, this.props.domain);
        }

        this.cancelTokenSrc.cancel();
        this.props.onChangeMenuClose();
    };

    handleSelectionModelChange = (selectionModel) => {
        this.setState({
            selectedHost: selectionModel[0]
        });
    };

    handleStateChange = ({api, state}) => {
        // select the first row once loaded
        if (state.rows.allRows.length !== 0 && state.selection.length === 0) {
            const firstHost = state.sorting.sortedRows[0];
            api.selectRow(firstHost);
        }
    };

    handleRowDoubleClick = (row) => {
        session_change_host(this.props.session_id, row.id, this.props.domain);
        this.props.onChangeMenuClose();
    };

    componentDidMount() {
        session_ruptime(this, this.cancelTokenSrc.token);
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
                        sortModel={[
                            {field: 'userNum', sort: 'asc'},
                            {field: 'load15', sort: 'asc'},
                            {field: 'load5', sort: 'asc'},
                            {field: 'load1', sort: 'asc'},
                        ]}
                        hideFooter={machineList.length <= 100}
                        onSelectionModelChange={this.handleSelectionModelChange}
                        onRowDoubleClick={this.handleRowDoubleClick}
                        onStateChange={this.handleStateChange}
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