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

import React from 'react';

import {
  CircularProgress,
  IconButton,
  ListItem,
  ListItemSecondaryAction,
  ListItemText,
} from '@mui/material';
import {CheckCircleOutline, Close} from '@mui/icons-material';

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
        cancelled,
      } = fm.state.uploadProgress[uploadProgressIdx];

      const handleCancel = (_) => {
        cancelTokenSrc.cancel('Cancelled by the user.');
        fm.setState(({uploadProgress}) => ({
          uploadProgress: [
            ...uploadProgress.slice(0, uploadProgressIdx),
            {
              ...uploadProgress[uploadProgressIdx],
              cancelled: true,
            },
            ...uploadProgress.slice(uploadProgressIdx + 1),
          ],
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
                `${humanFileSize(Math.round(speed))}/s - ${humanFileSize(
                    loaded)}/${humanFileSize(totalSize)}`
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
                <CircularProgress variant={'determinate'} value={progress}
                                  size={30}/>
              </div>
          }
        </ListItemSecondaryAction>}
      </ListItem>);
    }
;

export default UploadItem;