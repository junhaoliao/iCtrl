import React from 'react';

import {CircularProgress, IconButton, ListItem, ListItemSecondaryAction, ListItemText} from '@material-ui/core';
import {CheckCircleOutline, Close} from '@material-ui/icons';

import {humanFileSize} from './utils';
import './index.css';

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

        const uploadDone = progress === 100;
        return (<ListItem button className={'upload-item'}>
            <ListItemText
                primary={<div title={filename} className={'upload-item-name'}>
                    {filename}
                </div>}
                secondary={cancelled ?
                    'Upload cancelled' :
                    `${humanFileSize(Math.round(speed))}/s - ${humanFileSize(loaded)}/${humanFileSize(totalSize)}`
                }/>
            {!cancelled && <ListItemSecondaryAction>
                {uploadDone ?
                    <CheckCircleOutline color={'success'} fontSize={'large'}/> :
                    <div>
                        <IconButton className={'upload-item-cancel-button'}
                                    onClick={handleCancel} color={'primary'}
                                    aria-label={'cancel upload'}>
                            <Close/>
                        </IconButton>
                        <CircularProgress variant={'determinate'} value={progress} size={30}/>
                    </div>
                }
            </ListItemSecondaryAction>}
        </ListItem>);
    }
;

export default UploadItem;