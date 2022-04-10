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
import {Chip, IconButton} from '@mui/material';
import {KeyboardArrowDown} from '@mui/icons-material';

import './index.css';

export default class Toolbar extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      pressed: new Set(),
    };
  }

  handleChipClick = (key) => {
    const {onToolbarSendKey: sendKey} = this.props;
    const {pressed} = this.state;
    switch (key) {
      case 'Ctrl':
      case 'Alt':
      case 'Shift':
      case '⌘':
        if (!pressed.has(key)) {
          // previously not toggled
          sendKey(key, true);
          pressed.add(key);

          const cancelAll = (_) => {
            setTimeout(() => {
              for (let pressedKey of pressed) {
                sendKey(pressedKey, false);
              }
              this.setState({pressed: new Set()});
              window.removeEventListener('keydown', cancelAll, true);
            }, 0);

          };
          window.removeEventListener('keydown', cancelAll, true);
          window.addEventListener('keydown', cancelAll, true);
        } else {
          // previously toggled
          sendKey(key, false);
          pressed.delete(key);
        }
        break;
      case 'Tab':
      case 'Esc':
      case 'Delete':
        sendKey(key);
        break;
      case 'Ctrl+Alt+Delete':
        this.props.onCtrlAltDelete();
        break;
      default:
        break;
    }
    this.setState({pressed: pressed});
  };

  render() {
    const {onToolbarHide: handleToolbarHide} = this.props;
    const {pressed} = this.state;
    const keyList = [
      {label: 'Ctrl'},
      {label: 'Alt'},
      {label: 'Shift'},
      {label: '⌘'},
      {label: 'Tab'},
      {label: 'Esc'},
      {label: 'Delete'},
    ];
    if (this.props.onCtrlAltDelete) {
      keyList.push({label: 'Ctrl+Alt+Delete'});
    }
    return (
        <div id={'toolbar'}>
          {handleToolbarHide && <IconButton
              style={{marginLeft: 6}}
              color={'info'}
              onClick={handleToolbarHide}
          >
            <KeyboardArrowDown/>
          </IconButton>}
          {
            keyList.map((item) => (
                <Chip key={item.label}
                      label={item.label}
                      color="primary"
                      style={{
                        marginLeft: 12,
                      }}
                      variant={pressed.has(item.label) ? 'filled' : 'outlined'}
                      onClick={() => {
                        this.handleChipClick(item.label);
                      }}
                />))}
        </div>
    );
  }
}