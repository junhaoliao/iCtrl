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
  Autocomplete,
  Box,
  Button,
  Dialog,
  DialogActions,
  DialogContent,
  DialogContentText,
  DialogTitle,
  Slider,
  SpeedDial,
  SpeedDialAction,
  SpeedDialIcon,
  Stack,
  TextField,
} from '@mui/material';
import {
  AspectRatio,
  FitScreen,
  Fullscreen,
  FullscreenExit,
  Hd,
  HighQuality,
  Keyboard,
  LensBlur,
  MusicNote,
  MusicOff,
  Refresh,
  Sd,
  VisibilityOff,
} from '@mui/icons-material';

import './index.css';
import {focusOnKeyboard} from '../../../actions/vnc';
import axios from 'axios';
import {launch_audio} from '../../../actions/audio';
import RFB from '@novnc/novnc/core/rfb';
import {IOSSwitch} from '../../components/IOSSwitch';
import ResetVNCDialog from '../../components/ResetVNCDialog';

const speedDialTooltipWidth = 180;

let webFrame = null;
if (window.require !== undefined) {
  // if using electron
  webFrame = window.require('electron').webFrame;
}

export default class VNCSpeedDial extends React.Component {
  constructor(props) {
    super(props);

    this.audioSocket = null;
    this.sizeBeforeScale = null;
    // TODO: support saving those per session
    this.state = {
      isFullscreen: Boolean(document.fullscreenElement),
      resizeSession: true,
      enableAudio: false,
      speedDialDirection: 'up',
      tooltipPlacement: 'left',
      qualityLevel: 6,
      compressionLevel: 2,
      resetDialogOpen: false,
      inHdMode: false,
      scaleDialogOpen: false,
    };
  }

  handleFabMouseDown = (_) => {
    window.addEventListener('mousemove', this.handleFabMove, true);
    window.addEventListener('mouseup', this.handleFabMouseUp, true);
  };

  handleFabTouchStart = (_) => {
    window.addEventListener('touchmove', this.handleFabMove, true);
    window.addEventListener('touchend', this.handleFabTouchEnd, true);
  };

  handleFabMouseUp = (_) => {
    window.removeEventListener('mousemove', this.handleFabMove, true);
    window.removeEventListener('mouseup', this.handleFabMouseUp, true);
  };

  handleFabTouchEnd = (_) => {
    window.removeEventListener('touchmove', this.handleFabMove, true);
    window.removeEventListener('touchend', this.handleFabMouseUp, true);
  };

  handleFabMove = (ev) => {
    this.props.onFabMoveStart();

    const fab = document.getElementById('fab');
    const width = 56;

    const pointX = ev.touches ? ev.touches[0].clientX : ev.clientX;
    const pointY = ev.touches ? ev.touches[0].clientY : ev.clientY;

    // adjust the tooltip placement according to the mouse point
    // we should only update the state if placement is different from the state
    //  to avoid unnecessary re-render
    if (pointX < window.innerWidth / 2) {
      if (this.state.tooltipPlacement === 'left') {
        this.setState({
          tooltipPlacement: 'right',
        });
      }
    } else {
      if (this.state.tooltipPlacement === 'right') {
        this.setState({
          tooltipPlacement: 'left',
        });
      }
    }

    if (pointY < window.innerHeight / 2) {
      if (this.state.speedDialDirection === 'up') {
        this.setState({
          speedDialDirection: 'down',
        });
      }
      let newTop = pointY - width / 2;
      let newLeft = pointX - width / 2;

      if (newTop < 0) {
        newTop = 0;
      }
      if (newLeft < 0) {
        newLeft = 0;
      }
      if (newLeft > window.innerWidth - width) {
        newLeft = window.innerWidth - width;
      }
      fab.style.top = newTop + 'px';
      fab.style.left = newLeft + 'px';
      fab.style.bottom = 'unset';
      fab.style.right = 'unset';
    } else {
      if (this.state.speedDialDirection === 'down') {
        this.setState({
          speedDialDirection: 'up',
        });
      }
      let newBottom = window.innerHeight - pointY - width / 2;
      let newRight = window.innerWidth - pointX - width / 2;

      if (newRight > window.innerWidth - width) {
        newRight = window.innerWidth - width;
      }
      if (newBottom < 0) {
        newBottom = 0;
      }
      if (newRight < 0) {
        newRight = 0;
      }
      fab.style.top = 'unset';
      fab.style.left = 'unset';
      fab.style.bottom = newBottom + 'px';
      fab.style.right = newRight + 'px';
    }
    this.props.onFabMoveEnd();
  };

  handleQualityLevelChange = (event, newValue) => {
    this.setState({
      qualityLevel: newValue,
    });
    this.props.rfb.qualityLevel = newValue;
  };

  handleCompressionLevelChange = (event, newValue) => {
    this.setState({
      compressionLevel: newValue,
    });
    this.props.rfb.compressionLevel = newValue;
  };

  handleToggleAudio = (_) => {
    if (this.state.enableAudio === null) {
      return;
    }

    const enableAudio = !this.state.enableAudio;

    if (enableAudio) {
      this.setState({
        enableAudio: null,
      });
      const {session_id} = this.props;
      launch_audio(this, session_id);
    } else if (this.audioSocket !== null) {
      this.audioSocket.close();
      this.setState({
        enableAudio: false,
      });
    }
  };

  handleToggleResize = (_) => {
    const {rfb} = this.props;

    const newResizeSession = !this.state.resizeSession;
    this.setState({
      resizeSession: newResizeSession,
    });

    if (newResizeSession) {
      rfb.resizeSession = true;
    } else {
      rfb.resizeSession = false;

      // on Android, virtual keyboard popups change the size of the client
      //  store the size before the virtual keyboard pops up for scale prompt
      this.sizeBeforeScale = rfb._screenSize();

      this.setState({
        scaleDialogOpen: true,
      });
    }
  };

  handleSetScale = () => {
    this.setState({
      scaleDialogOpen: false,
    });
    const {rfb} = this.props;

    const scaleFactorValue = document.getElementById('scale-factor').value;
    const scale = 1 / parseFloat(scaleFactorValue);
    RFB.messages.setDesktopSize(rfb._sock,
        Math.floor(this.sizeBeforeScale.w * scale),
        Math.floor(this.sizeBeforeScale.h * scale), rfb._screenID,
        rfb._screenFlags);

    setTimeout(() => {
      this.props.closeSpeedDial();
    }, 50);
  };

  handleToggleFullscreen = (_) => {
    if (Boolean(document.fullscreenElement)) {
      document.exitFullscreen().then();
      this.setState({
        isFullscreen: false,
      });
    } else {
      document.body.requestFullscreen().then();
      this.setState({
        isFullscreen: true,
      });
    }
  };

  handleKeyboardOpen = (_) => {
    this.props.onToolbarOpen();
    this.props.closeSpeedDial();
    focusOnKeyboard();
  };

  handleHDModeToggle = (_) => {
    const {session_id} = this.props;
    const {inHdMode} = this.state;
    axios.post('/api/exec_blocking', {
      session_id: session_id,
      cmd: `gsettings set org.mate.interface window-scaling-factor ${inHdMode ?
          0 :
          2}`,
    }).then((response) => {
      webFrame.setZoomFactor(inHdMode ? 1 : 0.5);
      this.setState({
        inHdMode: !inHdMode,
      });
    });
  };

  handleResetConnection = (_) => {
    this.props.closeSpeedDial();
    this.setState({
      resetDialogOpen: true,
    });
  };

  handleResetDialogClose = (ev) => {
    this.setState({
      resetDialogOpen: false,
    });
  };

  componentDidMount() {
    if (webFrame !== null) {
      // only check zoom factor in electron
      const {session_id} = this.props;

      axios.post('/api/exec_blocking', {
        session_id: session_id,
        cmd: 'gsettings get org.mate.interface window-scaling-factor',
      }).then((response) => {
        const {data} = response;
        if (data >= 2) {
          webFrame.setZoomFactor(1 / data);
          this.setState({
            inHdMode: true,
          });
        }
      });
    }

    document.onfullscreenchange = (ev) => {
      this.setState({
        isFullscreen: Boolean(document.fullscreenElement)
      })
    }
  }

  render() {
    const {
      speedDialOpen,
      onSpeedDialClose: handleSpeedDialClose,
      onSpeedDialOpen: handleSpeedDialOpen,
      onFabHide: handleFabHide,
      session_id,
    } = this.props;
    const {
      speedDialDirection,
      tooltipPlacement,
      qualityLevel,
      compressionLevel,
      resizeSession,
      isFullscreen,
      resetDialogOpen,
      inHdMode,
      enableAudio,
      scaleDialogOpen,
    } = this.state;

    const audioConnecting = (enableAudio === null);

    return (
        <><SpeedDial
            id={'fab'}
            icon={<SpeedDialIcon/>}
            open={speedDialOpen}
            direction={speedDialDirection}
            onClose={handleSpeedDialClose}
            onOpen={handleSpeedDialOpen}
            FabProps={{
              size: 'small',
              onMouseDown: this.handleFabMouseDown,
              onTouchStart: this.handleFabTouchStart,
            }}
            ariaLabel={'speed dial more'}
            transitionDuration={1000}
        >
          <SpeedDialAction
              key={'hide'}
              icon={<VisibilityOff/>}
              tooltipTitle={<div
                  className={'speed-dial-action-title'}>Hide</div>}
              tooltipOpen
              tooltipPlacement={tooltipPlacement}
              onClick={handleFabHide}
          />
          <SpeedDialAction
              key={'open-keyboard'}
              icon={<Keyboard/>}
              tooltipTitle={<div
                  className={'speed-dial-action-title'}>Keyboard</div>}
              tooltipOpen
              tooltipPlacement={tooltipPlacement}
              onClick={this.handleKeyboardOpen}
          />
          <SpeedDialAction
              key={'reset'}
              icon={<Refresh/>}
              tooltipTitle={<div className={'speed-dial-action-title'}>Reset
                VNC</div>}
              tooltipOpen
              tooltipPlacement={tooltipPlacement}
              onClick={this.handleResetConnection}
          />
          {webFrame && <SpeedDialAction
              key={'hd-mode'}
              icon={inHdMode ? <Hd/> : <Sd/>}
              tooltipTitle={<Box display={'flex'} width={speedDialTooltipWidth}>
                <Box flexGrow={1} className={'speed-dial-action-title'}>HD
                  Mode</Box>
                <Box>{inHdMode ?
                    <span className={'enabled-text'}> Enabled</span> :
                    <span className={'disabled-text'}> Disabled</span>
                }</Box>
              </Box>}
              tooltipOpen
              tooltipPlacement={tooltipPlacement}
              onClick={this.handleHDModeToggle}
          />}
          {document.fullscreenEnabled && <SpeedDialAction
              key={'toggle-fullscreen'}
              icon={isFullscreen ? <Fullscreen/> : <FullscreenExit/>}
              tooltipTitle={<Box display={'flex'} width={speedDialTooltipWidth}>
                <Box flexGrow={1} className={'speed-dial-action-title'}>Full
                  Screen</Box>
                <IOSSwitch checked={isFullscreen}
                           onChange={this.handleToggleFullscreen}/>
              </Box>}
              tooltipOpen
              tooltipPlacement={tooltipPlacement}
              onClick={this.handleToggleFullscreen}
          />}
          <SpeedDialAction
              key={'toggle-audio'}
              icon={enableAudio ? <MusicNote/> : <MusicOff/>}
              tooltipTitle={<Box display={'flex'} width={speedDialTooltipWidth}>
                <Box flexGrow={1}
                     className={'speed-dial-action-title'}>Audio</Box>
                <IOSSwitch checked={enableAudio}
                           disabled={audioConnecting}
                           onChange={this.handleToggleAudio}/>
              </Box>}
              tooltipOpen
              tooltipPlacement={tooltipPlacement}
              onClick={this.handleToggleAudio}
          />
          <SpeedDialAction
              key={'toggle-resize'}
              icon={resizeSession ? <FitScreen/> : <AspectRatio/>}
              tooltipTitle={<Box display={'flex'} width={speedDialTooltipWidth}>
                <Box flexGrow={1} className={'speed-dial-action-title'}>Auto
                  Resize</Box>
                <IOSSwitch checked={resizeSession}
                           onChange={this.handleToggleResize}/>
              </Box>}
              tooltipOpen
              tooltipPlacement={tooltipPlacement}
              onClick={this.handleToggleResize}
          />
          <br/>
          <SpeedDialAction
              key={'quality'}
              icon={<HighQuality/>}
              tooltipTitle={<Stack>
                <Box display={'flex'} width={speedDialTooltipWidth}>
                  <Box flexGrow={1}
                       className={'speed-dial-action-title'}>Quality</Box>
                  <Box>{qualityLevel}</Box>
                </Box>
                <Slider
                    aria-label="quality level"
                    valueLabelDisplay="off"
                    value={qualityLevel}
                    step={1}
                    min={0}
                    max={9}
                    onChange={this.handleQualityLevelChange}
                />
              </Stack>}
              tooltipOpen
              tooltipPlacement={tooltipPlacement}
          />
          <br/>
          <SpeedDialAction
              key={'compression'}
              icon={<LensBlur/>}
              tooltipTitle={<Stack>
                <Box display={'flex'} width={speedDialTooltipWidth}>
                  <Box flexGrow={1}
                       className={'speed-dial-action-title'}>Compression</Box>
                  <Box>{compressionLevel}</Box>
                </Box>
                <Slider
                    aria-label="compression level"
                    valueLabelDisplay="off"
                    step={1}
                    value={compressionLevel}
                    min={0}
                    max={9}
                    onChange={this.handleCompressionLevelChange}
                />
              </Stack>}
              tooltipOpen
              tooltipPlacement={tooltipPlacement}
          />
        </SpeedDial>

          <ResetVNCDialog open={resetDialogOpen}
                          sessionID={session_id}
                          onClose={this.handleResetDialogClose}
                          onReset={this.props.onVNCReset}/>

          <Dialog open={scaleDialogOpen}>
            <DialogTitle>Scale Factor</DialogTitle>
            <DialogContent>
              <DialogContentText>
                Please enter a scale factor from 0.5 to 2, and we will try out
                best to apply that. You may enter 1 if you don't want to sacle.
              </DialogContentText>
              <br/>
              <Autocomplete id={'scale-factor'} options={['0.5', '1', '2']}
                            defaultValue={'1'}
                            freeSolo={true}
                            renderInput={(params) =>
                                <TextField variant={'standard'} {...params}
                                           label="Scale Factor"/>}/>
            </DialogContent>
            <DialogActions>
              <Button variant={'contained'} autoFocus={true}
                      onClick={this.handleSetScale}>Confirm</Button>
            </DialogActions>
          </Dialog>
        </>
    );
  }
}

