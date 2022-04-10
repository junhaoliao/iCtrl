/*
 * Copyright (c) 2022 iCtrl Developers
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
import axios from 'axios';
import {file_cleaner_rm} from '../../../actions/sftp';
import {LoadingButton} from '@mui/lab';
import QuotaUsage from '../QuotaUsage';

export default class FileCleaner extends React.Component {
  constructor(props) {
    super(props);
    this.cancelTokenSrc = axios.CancelToken.source();

    // quickly calculate the file sizes
    // this.fileListDict = {};

    this.state = {
      confirmDialogOpen: false,
      deleting: false,
      fileList: [],
      selectedFiles: [],
      // selectedFilesTotalSize: 0,
      sortModel: [
        {field: 'size', sort: 'desc'},
      ],
    };
  }

  handleClose = (ev) => {
    if (ev.target && ev.target.id === 'button-delete') {
      this.setState({
        confirmDialogOpen: true,
      });
    } else {
      this.props.onClose();
    }
  };

  handleSelectionModelChange = (selectionModel) => {
    // let selectedFilesTotalSize = 0;
    // for (const f of selectionModel){
    //   selectedFilesTotalSize += this.fileListDict[f];
    // }

    this.setState({
      // selectedFilesTotalSize,
      selectedFiles: selectionModel,
    });
  };

  handleSortModelChange = (newModel, _) => {
    this.setState({
      sortModel: newModel,
    });
  };

  handleConfirmClose = (ev) => {
    if (ev.target && ev.target.id === 'button-confirm') {
      file_cleaner_rm(this.props.sessionID, this.state.selectedFiles,
          this.cancelTokenSrc.token);
      this.setState({
        deleting: true,
      });
    } else {
      this.setState({
        confirmDialogOpen: false,
      });
      this.cancelTokenSrc.cancel();
    }
  };

  componentDidMount() {
    const {sessionID} = this.props;
    axios.post('/api/exec_blocking', {
      session_id: sessionID,
      cmd: 'du -a',
      large: true,
    }, {
      cancelToken: this.cancelToken,
    }).then(res => {
      // this.fileListDict = {};
      const fileList = [];
      // parse response data (str) into json format
      const lines = res.data.split('\n\n');
      for (const l of lines) {
        const [size, fileName] = l.split('\t');
        if (fileName && fileName !== '.') {
          const sizeInBytes = parseInt(size) * 1024;
          fileList.push({
            size: sizeInBytes,
            id: fileName,
          });
          // this.fileListDict[fileName] = sizeInBytes;
        }
      }
      this.setState({
        fileList,
      });
    }).catch(error => {
      console.log(error);
    });
  }

  render() {
    const {sessionID} = this.props;
    const {
      confirmDialogOpen,
      deleting,
      fileList,
      selectedFiles,
      // selectedFilesTotalSize,
      sortModel,
    } = this.state;

    return (
        <>
          <Dialog
              open={true}
              fullWidth={true}
              maxWidth={'md'}
              aria-labelledby="file cleaner"
          >
            <DialogTitle>
              <Box display={'flex'} alignItems={'center'}>
                <div style={{flex: 1}}>File Cleaner</div>
                <div style={{width: '200px'}}>
                  <QuotaUsage sessionID={sessionID}/>
                </div>
              </Box>
            </DialogTitle>
            <DialogContent style={{height: '430px'}}>
              <Box marginBottom={'10px'} display={'flex'} alignItems={'center'}>
                <Typography variant={'body1'}
                            marginRight={'8px'}>Command:</Typography>
                <TextField size={'small'} fullWidth={true} spellCheck={false}
                           value={'du -ah | sort -h'}/>
              </Box>
              <DataGrid
                  style={{height: '380px'}}
                  rows={fileList}
                  columns={columns}
                  loading={fileList.length === 0}
                  sortModel={sortModel}
                  checkboxSelection={true}
                  onSortModelChange={this.handleSortModelChange}
                  onSelectionModelChange={this.handleSelectionModelChange}
                  disableColumnMenu={true}
                  // localeText={{
                  //   footerRowSelected: count => `${count} row${(count>1)?'s':''} selected: ${humanFileSize(selectedFilesTotalSize)}`
                  // }}
              />
            </DialogContent>
            <DialogActions>
              <Button onClick={this.handleClose}>Close</Button>
              <Button id={'button-delete'}
                      variant={'contained'}
                      disabled={selectedFiles.length === 0}
                      onClick={this.handleClose}>
                Delete
              </Button>
            </DialogActions>
          </Dialog>
          <Dialog
              open={confirmDialogOpen}
              fullWidth={true}
              maxWidth={'sm'}
          >
            <DialogTitle>
              Confirm Delete
            </DialogTitle>
            <DialogContent style={{height: '200px'}}>
              <Typography variant={'body1'}><b>Do you wish to delete the
                following {selectedFiles.length} file{selectedFiles.length >
                    1 && 's'}?</b></Typography>
              {selectedFiles.map((f) => (<p>
                {f}
              </p>))}
            </DialogContent>
            <DialogActions>
              <Button onClick={this.handleConfirmClose}>Close</Button>
              <LoadingButton
                  loading={deleting}
                  id={'button-confirm'}
                  variant={'contained'}
                  onClick={this.handleConfirmClose}>
                Delete
              </LoadingButton>
            </DialogActions>
          </Dialog>
        </>

    );
  }
}