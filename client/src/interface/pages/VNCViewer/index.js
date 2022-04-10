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
import {Backdrop, Box, Button, Typography} from '@mui/material';

import './index.css';
import Loading from '../../components/Loading';
import {VNCSteps} from '../../components/Loading/steps';
import VNCSpeedDial from './VNCSpeedDial';
import {focusOnKeyboard, vncConnect} from '../../../actions/vnc';
import {changeFavicon} from '../../utils';
import Toolbar from '../../components/Toolbar';
import KeyTable from '@novnc/novnc/core/input/keysym';
import {isIOS} from '../../../actions/utils';
import {updateTitle} from '../../../actions/common';

export default class VNCViewer extends React.Component {
  constructor(props) {
    super(props);

    document.title = 'VNC';

    const {
      match: {params},
    } = props;

    this.session_id = params.session_id;
    this.noLoadCheck = window.location.toString().includes('no_load_check');

    this.rfb = null;
    this.lastKeyboardinput = null;
    this.shiftKeyDown = false;

    this.speedDialOpenTime = 0;

    this.state = {
      disconnected: false,
      resetting: false,
      loading: true,
      currentStep: -1,
      authentication: null,
      showFab: true,
      speedDialOpen: false,
      showToolbar: false,
      isOverloaded: false,
      quotaExceeded: false,
      fabMoving: false,
    };
  }

  keyboardInputReset = () => {
    this.keyboardElem.value = new Array(100).join('_');
    this.lastKeyboardinput = this.keyboardElem.value;
  };

  handleSpeedDialOpen = (ev) => {
    if (ev.type === 'mouseenter') {
      return;
    }

    this.speedDialOpenTime = new Date().getTime();
    this.setState({
      speedDialOpen: true,
    });
  };

  closeSpeedDial = () => {
    this.setState({
      speedDialOpen: false,
    });
  };
  handleSpeedDialClose = (ev) => {
    if (ev.type === 'mouseleave' ||
        (new Date().getTime() - this.speedDialOpenTime) < 200) {
      return;
    }

    this.closeSpeedDial();
  };

  handleFabHide = () => {
    this.setState({
      showFab: false,
      speedDialOpen: false,
    });
    this.rfb.focus();
  };

  handleToolbarSendKey = (key, down) => {
    switch (key) {
      case 'Ctrl':
        this.rfb.sendKey(KeyTable.XK_Control_L, 'ControlLeft', down);
        break;
      case 'Alt':
        this.rfb.sendKey(KeyTable.XK_Alt_L, 'AltLeft', down);
        break;
      case 'Shift':
        this.rfb.sendKey(KeyTable.XK_Shift_L, 'ShiftLeft', down);
        this.shiftKeyDown = down;
        break;
      case '⌘':
        this.rfb.sendKey(KeyTable.XK_Super_L, 'MetaLeft', down);
        break;
      case 'Tab':
        this.rfb.sendKey(KeyTable.XK_Tab, 'Tab');
        break;
      case 'Esc':
        this.rfb.sendKey(KeyTable.XK_Escape, 'Escape');
        break;
      case 'Delete':
        this.rfb.sendKey(KeyTable.XK_Delete, 'Delete');
        break;
      default:
        console.log('Unexpected key pressed.');
    }
    focusOnKeyboard();
  };

  handleToolbarOpen = () => {
    if (!isIOS()) {
      this.rfb.focusOnClick = false;
    }

    this.setState({
      showToolbar: true,
    });
  };

  handleToolbarHide = () => {
    this.rfb.focusOnClick = true;

    this.setState({
      showToolbar: false,
    });

    // on iOS: disable on screen keyboard
    const canvas = document.getElementById(
        'screen').lastElementChild.firstElementChild;
    canvas.setAttribute('contenteditable', 'false');

    // on Android browsers: once the screen receive focus, the virtual keyboard will disappear
    this.rfb.focus();
  };

  reloadPage = () => {
    window.location.reload();
  };

  handleVNCReset = () => {
    this.setState({
      resetting: true,
    });
  };

  componentDidMount() {
    updateTitle(this.session_id, 'VNC');

    changeFavicon(`/api/favicon/vnc/${this.session_id}`);
    vncConnect(this).then();
  }

  render() {
    const {
      authentication,
      currentStep,
      disconnected,
      resetting,
      loading,
      speedDialOpen,
      showFab,
      showToolbar,
      isOverloaded,
      quotaExceeded,
      fabMoving,
    } = this.state;

    if (!resetting && disconnected) {
      return <Box height={'100vh'}
                  display={'flex'}
                  flexDirection={'column'}
                  justifyContent={'center'}>
        <Typography variant={'h6'} align={'center'}>
          The VNC connection has been disconnected. Do you wish to reconnect?
        </Typography>
        <br/>
        <Button
            onClick={this.reloadPage}
            style={{width: '8em', alignSelf: 'center'}}
            size={'small'}
            variant={'outlined'}>
          Reconnect
        </Button>
      </Box>;
    }

    return (<div>
          <Backdrop id={'speed-dial-backdrop'} open={speedDialOpen}/>
          {showFab && !loading &&
              <VNCSpeedDial
                  session_id={this.session_id}
                  rfb={this.rfb}
                  speedDialOpen={speedDialOpen && !fabMoving}
                  onVNCReset={this.handleVNCReset}
                  onSpeedDialClose={this.handleSpeedDialClose}
                  onSpeedDialOpen={this.handleSpeedDialOpen}
                  closeSpeedDial={this.closeSpeedDial}
                  onToolbarOpen={this.handleToolbarOpen}
                  onFabMoveStart={() => {
                    this.setState({
                      fabMoving: true,
                    });
                  }}
                  onFabMoveEnd={() => {
                    this.setState({
                      fabMoving: false,
                    });
                  }}
                  onFabHide={this.handleFabHide}/>
          }

          {loading &&
              <Loading
                  sessionId={this.session_id}
                  currentStep={currentStep}
                  steps={VNCSteps}
                  authentication={authentication}
                  isOverloaded={isOverloaded}
                  quotaExceeded={quotaExceeded}
              />
          }

          <div style={{display: loading && 'none'}} id={'screen'}
               className={showToolbar ? 'screen-with-toolbar' : ''}>
                    <textarea id={'textarea'} autoCapitalize="off"
                              autoComplete="off" spellCheck="false"
                              tabIndex="-1"
                    />
          </div>

          {showToolbar &&
              <Toolbar onToolbarSendKey={this.handleToolbarSendKey}
                       onCtrlAltDelete={() => {
                         this.rfb.sendCtrlAltDel();
                       }}
                       onToolbarHide={this.handleToolbarHide}/>}
        </div>
    );
  }
}