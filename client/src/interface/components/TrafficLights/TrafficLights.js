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

import './index.css';
import {Tooltip} from '@mui/material';
import {ipcRenderer} from '../../../actions/ipc';

export default class TrafficLights extends React.Component {
  handleClick = (ev) => {
    const action = ev.target.innerText;
    switch (action) {
      case '−':
        ipcRenderer.send('win-min');
        break;
      case '+':
        ipcRenderer.send('win-max');
        break;
      default:
        ipcRenderer.send('win-close');
        break;
    }
  };

  render() {
    return <>
      <div id={'traffic-lights-container'}>
        <Tooltip title={'Minimize'}>
          <div className={'win-button'} id={'win-min-button'}
               onClick={this.handleClick}>
            <div className={'win-text'} id={'win-min-text'}>−</div>
          </div>
        </Tooltip>

        <Tooltip title={'Restore'}>
          <div className={'win-button'} id={'win-max-button'}
               onClick={this.handleClick}>
            <div className={'win-text'} id={'win-max-text'}>+</div>
          </div>
        </Tooltip>

        <Tooltip title={'Close'}>
          <div className={'win-button'} id={'win-close-button'}
               onClick={this.handleClick}>
            <div className={'win-text'} id={'win-close-text'}>×</div>
          </div>
        </Tooltip>
      </div>

      <Tooltip title={'Close'}>
        <div id={'win-close-corner'}
             style={{
               width: '45px',
               height: '42px',
               position: 'fixed',
               right: 0,
               top: 0,
             }}
             onClick={this.handleClick}
        />
      </Tooltip>
    </>;
  }
}