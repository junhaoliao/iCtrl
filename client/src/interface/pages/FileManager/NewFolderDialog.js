import React from 'react';
import {
  Button,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  TextField,
} from '@mui/material';
import axios from 'axios';
import {htmlResponseToReason} from '../../../actions/utils';
import {LoadingButton} from '@mui/lab';

export default class NewFolderDialog extends React.Component {
  constructor(props) {
    super(props);

    this.state = {
      cancelTokenSrc: null,
      newFolderNameError: '',
    };
  }

  handleFocus = (ev) => {
    ev.target.select();
  };

  handleClose = (ev) => {
    this.setState({
      newFolderNameError: '',
    });
    if (ev.target.id !== 'create-button') {
      if (this.state.cancelTokenSrc) {
        this.state.cancelTokenSrc.cancel('canceled by the user');
      }
      this.props.onClose();
    } else {
      const newFolderName = document.getElementById('new-folder-name').value;
      if (newFolderName === '') {
        this.setState({
          newFolderNameError: 'Folder name cannot be empty',
        });
        return;
      }

      const cancelTokenSrc = axios.CancelToken.source();
      this.setState({
        cancelTokenSrc: cancelTokenSrc,
      });
      axios.put(`/api/sftp_mkdir/${this.props.sessionId}`, {
        cwd: this.props.cwd,
        name: newFolderName,
      }, {
        cancelToken: cancelTokenSrc.token,
      }).then(_ => {
        this.setState({
          cancelTokenSrc: null,
        });
        this.props.onClose();
      }).catch(error => {
        this.setState({
          cancelTokenSrc: null,
        });
        if (error.response) {
          this.setState({
            newFolderNameError: htmlResponseToReason(error.response.data),
          });
        } else {
          if (error.message === 'canceled by the user') {
            return;
          }
          // Something happened in setting up the request that triggered an Error
          this.setState({
            newFolderNameError: error.message,
          });
        }
      });
    }

  };

  render() {
    const {open} = this.props;
    const {cancelTokenSrc, newFolderNameError} = this.state;

    return (<Dialog open={open}
                    fullWidth
                    maxWidth={'xs'}>
      <DialogTitle>Create New Folder</DialogTitle>
      <DialogContent>
        <TextField
            id="new-folder-name"
            autoFocus
            onFocus={this.handleFocus}
            defaultValue={'Untitled folder'}
            disabled={Boolean(cancelTokenSrc)}
            error={newFolderNameError !== ''}
            helperText={newFolderNameError}
            fullWidth
            size={'small'}
            variant="outlined"/>
      </DialogContent>
      <DialogActions onClick={this.handleClose}>
        <Button color={'inherit'}>Cancel</Button>
        <LoadingButton loading={Boolean(cancelTokenSrc)} id={'create-button'}
                       variant={'contained'}>Create</LoadingButton>
      </DialogActions>
    </Dialog>);
  }
}