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

import axios from 'axios';
import domtoimage from 'dom-to-image';
import {getAvatarName} from './session';
import {ipcRenderer} from './ipc';

const ICON_SCALE_LEVEL = 5;

export const updateTitleAndIcon = (component) => {
  axios.get('/api/session', {
    params: {
      id: component.session_id,
    },
  }).then(response => {
    const {host, username, nickname} = response.data;
    document.title = `${component.feature} - ${username}@${host}`;

    component.setState({
      sessionNickname: (nickname && nickname !== '') ?
          nickname :
          getAvatarName(host),
    });

    // timeout needed to ensure nickname text has been scaled properly
    setTimeout(() => {
      domtoimage.toPng(document.getElementById('offscreen-favicon'),
          {
            width: 40 * ICON_SCALE_LEVEL,
            height: 40 * ICON_SCALE_LEVEL,
            style: {
              position: null,
              left: '0px',
              transform: `scale(${ICON_SCALE_LEVEL})`,
              transformOrigin: 'top left',
            },
          }).
          then((dataURL) => {
            const link = document.getElementById('favicon');
            link.href = dataURL;
            link.type = 'image/png';

            ipcRenderer.send('set-icon', dataURL);
          });
    }, 100);
  });
};