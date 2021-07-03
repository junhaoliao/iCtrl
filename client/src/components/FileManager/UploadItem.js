import {Box, CircularProgress, IconButton, Typography} from '@material-ui/core';
import CloseIcon from '@material-ui/icons/Close';
import React from 'react';
import CheckCircleOutlineIcon from '@material-ui/icons/CheckCircleOutline';
import {makeStyles} from '@material-ui/styles';
import {humanFileSize} from './utils';


const useStyles = makeStyles((theme) => ({
    root: {
        background: 'white',
        '&:hover': {
            background: '#f5f5f5',
            '& $closeIcon': {
                display: 'block'
            }
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
        top: -4,
        left: 20,
        zIndex: 1,
        '& $closeIcon': {
            display: 'none'
        }
    },
    closeIcon: {
        width: 16,
        height: 16,
    },
    checkIcon: {
        position: 'relative',
        fontSize: '36px!important',
        left: -10,
        top: 8,
        color: 'green'
    },
    circularProgress: {
        position: 'relative',
        left: -12,
        top: 8
    }
}));

const UploadItem = (props) => {
    const {fm, uploadProgressIdx} = props;
    const {
        filename,
        progress,
        speed,
        loaded,
        totalSize,
        cancelTokenSrc,
        cancelled
    } = fm.state.uploadProgress[uploadProgressIdx];
    const classes = useStyles();

    const handleCancel = (_) => {
        cancelTokenSrc.cancel('Cancelled by the user.');
        fm.setState(({uploadProgress}) => ({
            uploadProgress: [
                ...uploadProgress.slice(0, uploadProgressIdx),
                {
                    ...uploadProgress[uploadProgressIdx],
                    cancelled: true
                },
                ...uploadProgress.slice(uploadProgressIdx + 1)
            ]
        }));
    };

    return (<Box className={classes.root} display={'flex'}>
        <Box className={classes.filename} flexGrow={1}>
            <Typography variant={'subtitle1'}>
                {filename}
            </Typography>
            <Typography variant={'subtitle2'} style={{color: 'grey'}}>
                {cancelled ?
                    'Upload cancelled' :
                    `${humanFileSize(Math.round(speed))}/s - ${humanFileSize(loaded)}/${humanFileSize(totalSize)}`
                }
            </Typography>
        </Box>
        {!cancelled && <Box>
            {progress === 100 ?
                <CheckCircleOutlineIcon className={classes.checkIcon}/> :
                <IconButton onClick={handleCancel} className={classes.iconButton} color={'primary'}
                            aria-label={'cancel upload'}>
                    <CloseIcon className={classes.closeIcon}/></IconButton>}
            {progress !== 100 &&
            <CircularProgress className={classes.circularProgress} variant={'determinate'} value={progress} size={32}/>}
        </Box>}
    </Box>);
};

export default UploadItem;