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
import {COLOR_FILE_MANAGER} from '../../constants';

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

  const handleUploadWindowClose = () => {
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
  const handleUploadWindowCollapse = () => {
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
          background: COLOR_FILE_MANAGER,
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