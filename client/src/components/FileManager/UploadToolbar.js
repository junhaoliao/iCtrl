import React from 'react';
import {IconButton, makeStyles, Toolbar, Typography} from '@material-ui/core';

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
    const handleUploadWindowClose = (ev) => {
        fm.setState({
            uploadWindowOpen: false
        });
    };
    const handleUploadWindowCollapse = (ev) => {
        fm.setState({
            uploadWindowCollapsed: !fm.state.uploadWindowCollapsed
        });
    };

    const classes = useStyles();
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

    </Toolbar>);
};

export default UploadToolbar;