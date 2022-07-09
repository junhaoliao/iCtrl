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
import {sftp_quota} from '../../../actions/sftp';
import {Box, LinearProgress, Skeleton, Typography} from '@mui/material';
import {humanFileSize} from '../../pages/FileManager/utils';

function LinearProgressWithLabel(props) {
  return (
      <Box sx={{display: 'flex', alignItems: 'center'}}>
        <Box flexGrow={1}>
          <LinearProgress
              variant={props.loading ? 'indeterminate' : 'determinate'}
              value={props.value}
          />
        </Box>
        <Box sx={{marginLeft: 1.5}}>
          <Typography display={'flex'} variant="body2" color="text.secondary">
            {props.loading ?
                <Skeleton width={15}/> :
                `${Math.round(props.value)}`}%
          </Typography>
        </Box>
      </Box>
  );
}

export default class QuotaUsage extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      used: 0,
      usedUnit: '',
      quota: 0,
      quotaUnit: '',
    };
  }

  componentDidMount() {
    const {sessionID} = this.props;
    sftp_quota(
        sessionID,
        this,
    );
  }

  render() {
    const {
      used,
      quota,
    } = this.state;
    const loading = (quota === 0);
    const loadFailed = (quota === null);
    return (<div style={{
          width: '100%',
          visibility: loadFailed ? 'hidden' : 'visible',
        }}>
          <LinearProgressWithLabel loading={loading}
                                   value={used / quota * 100}/>
          <Typography variant="caption" display={'flex'}>
            {loading ? <Skeleton width={44}/> : `${humanFileSize(used)}`}
            {' / '}
            {loading ? <Skeleton width={44}/> : `${humanFileSize(quota)}`}
            {' Used'}
          </Typography>
        </div>
    );
  }
}