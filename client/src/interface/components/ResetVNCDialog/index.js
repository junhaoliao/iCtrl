import React from 'react';
import {
  Button,
  Dialog,
  DialogActions,
  DialogContent,
  DialogContentText,
  DialogTitle,
} from '@mui/material';
import {LoadingButton} from '@mui/lab';
import {Refresh} from '@mui/icons-material';
import {resetVNC} from '../../../actions/vnc';

export default class ResetVNCDialog extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      resetting: false,
    };
  }

  handleClose = (ev) => {
    const {
      onClose: handleResetDialogClose,
      onReset: handleVNCReset,
      sessionID,
    } = this.props;
    if (ev.target.id === 'reset-cancel-button') {
      handleResetDialogClose();
    } else {
      this.setState({
        resetting: true,
      });

      if (handleVNCReset !== undefined) {
        handleVNCReset();
      }

      resetVNC(sessionID);
    }
  };

  render() {
    const {open} = this.props;
    const {resetting} = this.state;

    return <Dialog
        open={open}
        onClose={this.handleClose}
    >
      <DialogTitle>{'Do you wish to reset the VNC session? '}</DialogTitle>
      <DialogContent>
        <DialogContentText>
          If you broke the VNC session by mistakenly logging out in the
          VNC screen,
          or you wish to change your VNC password, you may proceed to
          reset your VNC settings.
        </DialogContentText>
      </DialogContent>
      <DialogActions>
        <Button id={'reset-cancel-button'}
                disabled={resetting}
                onClick={this.handleClose}>Cancel</Button>
        <LoadingButton
            variant={'contained'}
            loading={resetting}
            loadingPosition="start"
            startIcon={<Refresh/>}
            onClick={this.handleClose}
        >
          Reset
        </LoadingButton>
      </DialogActions>
    </Dialog>;
  }
}