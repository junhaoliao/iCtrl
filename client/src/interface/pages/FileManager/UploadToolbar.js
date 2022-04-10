import React, {useState} from 'react';
import {
  Button,
  Dialog,
  DialogActions,
  DialogContent,
  DialogContentText,
  DialogTitle,
  IconButton,
  Typography,
} from '@mui/material';
import {Close, ExpandLess, ExpandMore} from '@mui/icons-material';

const UploadToolbar = (props) => {
  const {fm} = props;
  const [cancelAllPromptOpen, setCancelAllPromptOpen] = useState(false);

  const handleCancelAllPrompt = (ev) => {
    if (ev.target.id !== 'button_cancel') {
      setCancelAllPromptOpen(false);
      return;
    }
    fm.state.uploadProgress.forEach((item) => {
      item.cancelTokenSrc.cancel();
    });
    fm.setState({
      uploadProgress: [],
    });
  };

  const handleUploadWindowClose = (ev) => {
    const shouldPrompt = fm.state.uploadProgress.some(item => {
      if (item.cancelled) {
        return false;
      } else {
        return item.progress !== 100;
      }
    });
    if (!shouldPrompt) {
      fm.setState({
        uploadProgress: [],
      });
    } else {
      setCancelAllPromptOpen(true);
    }
  };
  const handleUploadWindowCollapse = (ev) => {
    fm.setState({
      uploadWindowCollapsed: !fm.state.uploadWindowCollapsed,
    });
  };

  const pluralUpload = fm.state.uploadProgress.length > 1;
  return (
      <>
        <div style={{
          display: 'flex',
          height: '50px',
          background: '#1976d2',
          color: 'white',
          alignItems: 'center',
        }}>
          <Typography style={{flex: 1, marginLeft: '18px'}} variant={'h6'}>
            File Upload
          </Typography>
          <IconButton sx={{color: 'white'}} onClick={handleUploadWindowCollapse}
                      aria-label="collapse upload window">
            {fm.state.uploadWindowCollapsed ? <ExpandLess/> : <ExpandMore/>}
          </IconButton>
          <IconButton sx={{color: 'white', marginRight: '12px'}}
                      onClick={handleUploadWindowClose}
                      aria-label="close upload window">
            <Close/>
          </IconButton>
        </div>
        <Dialog
            open={cancelAllPromptOpen}
            keepMounted
            onClose={handleCancelAllPrompt}
            aria-describedby="cancel all upload alert"
            fullWidth={true}
            maxWidth={'sm'}
        >
          <DialogTitle>{`Cancel ${pluralUpload ?
              'all uploads' :
              'upload'}?`}</DialogTitle>
          <DialogContent>
            <DialogContentText id="cancel all upload description">
              Your {pluralUpload ? 'uploads are' : 'upload is'} not
              complete. <br/>
              Would you like to cancel {pluralUpload ?
                'all ongoing uploads' :
                'the upload'}?
            </DialogContentText>
          </DialogContent>
          <DialogActions>
            <Button variant={'contained'} onClick={handleCancelAllPrompt}>Continue
              Upload{pluralUpload ? 's' : ''}</Button>
            <Button id={'button_cancel'} onClick={handleCancelAllPrompt}>Cancel
              Upload{pluralUpload ? 's' : ''}</Button>
          </DialogActions>
        </Dialog>
      </>);
};

export default UploadToolbar;