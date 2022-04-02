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
} from '@material-ui/core';
import {DataGrid} from '@material-ui/data-grid';
import columns from './column';
import axios from 'axios';
import {file_cleaner_rm} from '../../../actions/sftp';
import {LoadingButton} from '@material-ui/lab';
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