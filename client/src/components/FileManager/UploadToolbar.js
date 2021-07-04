import React, {useState} from 'react';
import {
    Button,
    Dialog,
    DialogActions,
    DialogContent,
    DialogContentText,
    DialogTitle,
    IconButton,
    Toolbar,
    Typography
} from '@material-ui/core';
import {makeStyles} from '@material-ui/styles';

import CloseIcon from '@material-ui/icons/Close';
import {ExpandLess, ExpandMore} from '@material-ui/icons';
// TODO: change the background style below
const useStyles = makeStyles((theme) => ({
    root: {
        background: 'linear-gradient(45deg, #FE6B8B 30%, #FF8E53 90%)',
        color: 'white',
        flexGrow: 1
    },
    title: {
        flexGrow: 1
    }
}));


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
            uploadProgress: []
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
                uploadProgress: []
            });
        } else {
            setCancelAllPromptOpen(true);
        }
    };
    const handleUploadWindowCollapse = (ev) => {
        fm.setState({
            uploadWindowCollapsed: !fm.state.uploadWindowCollapsed
        });
    };

    const classes = useStyles();
    const pluralUpload = fm.state.uploadProgress.length > 1;
    return (<Toolbar {...props} className={classes.root} style={{width: 300}}>
        <Typography className={classes.title} variant={'h6'}>
            File Upload
        </Typography>
        <IconButton onClick={handleUploadWindowCollapse} aria-label="collapse upload window">
            {fm.state.uploadWindowCollapsed ? <ExpandLess/> : <ExpandMore/>}
        </IconButton>
        <IconButton onClick={handleUploadWindowClose} aria-label="close upload window">
            <CloseIcon/>
        </IconButton>
        <Dialog
            open={cancelAllPromptOpen}
            keepMounted
            onClose={handleCancelAllPrompt}
            aria-describedby="cancel all upload alert"
            fullWidth={true}
            maxWidth={'sm'}
        >
            <DialogTitle>{`Cancel ${pluralUpload ? 'all uploads' : 'upload'}?`}</DialogTitle>
            <DialogContent>
                <DialogContentText id="cancel all upload description">
                    Your {pluralUpload ? 'uploads are' : 'upload is'} not complete. <br/>
                    Would you like to cancel {pluralUpload ? 'all ongoing uploads' : 'the upload'}?
                </DialogContentText>
            </DialogContent>
            <DialogActions>
                <Button variant={'contained'} onClick={handleCancelAllPrompt}>Continue
                    Upload{pluralUpload ? 's' : ''}</Button>
                <Button id={'button_cancel'} onClick={handleCancelAllPrompt}>Cancel
                    Upload{pluralUpload ? 's' : ''}</Button>
            </DialogActions>
        </Dialog>
    </Toolbar>);
};

export default UploadToolbar;