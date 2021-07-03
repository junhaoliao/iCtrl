import {Box, CircularProgress, IconButton, makeStyles, Typography} from '@material-ui/core';
import CloseIcon from '@material-ui/icons/Close';
import React from 'react';
import CheckCircleOutlineIcon from '@material-ui/icons/CheckCircleOutline';

const useStyles = makeStyles((theme) => ({
    root: {
        background: 'white',
        '&:hover': {
            background: '#f5f5f5',
        }
    },
    filename: {
        marginLeft: 8,
        marginTop: 8
    },
    iconButton: {
        position: 'relative',
        width: 32,
        height: 32,
        top: -7,
        left: 20,
        zIndex: 1,
        '& $icon': {
            visibility: 'hidden'
        },
        '&:hover': {
            '& $icon': {
                visibility: 'visible'
            }
        }
    },
    icon: {
        width: 16,
        height: 16,
    },
    checkIcon: {
        position: 'relative',
        width: 28,
        height: 28,
        left: -12,
        top: 5,
        color: 'green'
    },
    circularProgress: {
        position: 'relative',
        left: -12,
        top: 5
    }
}));

const UploadItem = (props) => {
    const {filename, progress} = props;
    const classes = useStyles();
    return (<Box className={classes.root} display={'flex'}>
        <Box className={classes.filename} flexGrow={1}>
            <Typography variant={'subtitle1'}>
                {filename}
            </Typography>
        </Box>
        <Box>
            {progress === 100 ?
                <CheckCircleOutlineIcon className={classes.checkIcon}/> :
                <IconButton className={classes.iconButton} color={'primary'} aria-label={'cancel upload'}>
                    <CloseIcon className={classes.icon}/></IconButton>}
            {progress !== 100 &&
            <CircularProgress className={classes.circularProgress} variant={'determinate'} value={progress} size={32}/>}
        </Box>
    </Box>);
};

export default UploadItem;