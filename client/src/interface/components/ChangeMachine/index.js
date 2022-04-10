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

/* eslint-disable react-hooks/rules-of-hooks */
import React from 'react';
import {
  Box,
  Button,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  TextField,
  Typography,
} from '@mui/material';
import {DataGrid} from '@mui/x-data-grid';
import columns from './column';
import {session_change_host, session_ruptime} from '../../../actions/session';
import axios from 'axios';

export default class ChangeMachine extends React.Component {
  constructor(props) {
    super(props);
    this.cancelTokenSrc = axios.CancelToken.source();

    this.state = {
      selectionModel: [],
      machineList: [],
      sortModel: [
        {field: 'userNum', sort: 'asc'},
        {field: 'load15', sort: 'asc'},
        {field: 'load5', sort: 'asc'},
        {field: 'load1', sort: 'asc'},
      ],
    };
  }

  handleClose = (ev) => {
    if (ev.target && ev.target.id === 'button_apply') {
      session_change_host(this.props.session_id, this.state.selectionModel[0],
          this.props.domain);
    }

    this.cancelTokenSrc.cancel();
    this.props.onChangeMenuClose();
  };

  handleSelectionModelChange = (selectionModel) => {
    this.setState({
      selectionModel,
    });
  };

  handleStateChange = (state) => {
    // select the first row once loaded
    if (state.rows.totalRowCount !== 0 && state.selection.length === 0) {
      const firstHost = state.sorting.sortedRows[0];
      this.setState({selectionModel: [firstHost]});
    }
  };

  handleRowDoubleClick = (row) => {
    session_change_host(this.props.session_id, row.id, this.props.domain);
    this.props.onChangeMenuClose();
  };

  handleSortModelChange = (newModel, _) => {
    this.setState({
      sortModel: newModel,
    });
  };

  componentDidMount() {
    session_ruptime(this, this.cancelTokenSrc.token);
  }

  render() {
    const {machineList, sortModel, selectionModel} = this.state;

    return (
        <Dialog
            open={true}
            fullWidth={true}
            maxWidth={'md'}
            aria-labelledby="change machine"
        >
          <DialogTitle>Change Machine</DialogTitle>
          <DialogContent style={{height: '430px'}}>
            <Box marginBottom={'10px'} display={'flex'} alignItems={'center'}>
              <Typography variant={'body1'}
                          marginRight={'8px'}>Command:</Typography>
              <TextField size={'small'} fullWidth={true} spellCheck={false}
                         value={'ruptime -aur'}/>
            </Box>
            <DataGrid
                style={{height: '380px'}}
                rows={machineList}
                columns={columns}
                pageSize={100}
                rowsPerPageOptions={[]}
                loading={!machineList.length}
                sortModel={sortModel}
                selectionModel={selectionModel}
                hideFooter={machineList.length <= 100}
                hideFooterSelectedRowCount={true}
                onSortModelChange={this.handleSortModelChange}
                onSelectionModelChange={this.handleSelectionModelChange}
                onRowDoubleClick={this.handleRowDoubleClick}
                onStateChange={this.handleStateChange}
                disableColumnMenu={true}
            />
          </DialogContent>
          <DialogActions>
            <Button onClick={this.handleClose}>Close</Button>
            <Button id={'button_apply'}
                    variant={'contained'}
                    disabled={selectionModel.length === 0}
                    onClick={this.handleClose}>
              Apply
            </Button>
          </DialogActions>
        </Dialog>
    );
  }
}