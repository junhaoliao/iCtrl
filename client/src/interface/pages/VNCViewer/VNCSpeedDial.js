import React from 'react';
import {
  Box,
  Button,
  Dialog,
  DialogActions,
  DialogContent,
  DialogContentText,
  DialogTitle, Grow, Slide,
  Slider,
  SpeedDial,
  SpeedDialAction,
  SpeedDialIcon,
  Stack, Zoom,
} from '@material-ui/core';
import {
  Fullscreen,
  FullscreenExit,
  Hd,
  Height,
  HighQuality,
  Keyboard,
  LensBlur,
  Refresh,
  Sd,
  VisibilityOff,
} from '@material-ui/icons';

import './index.css';
import {LoadingButton} from '@material-ui/lab';
import {focusOnKeyboard, resetVNC} from '../../../actions/vnc';
import axios from 'axios';

let webFrame = null;
if (window.require !== undefined) {
  // if using electron
  webFrame = window.require('electron').webFrame;
}

export default class VNCSpeedDial extends React.Component {
  constructor(props) {
    super(props);

    // TODO: support saving those per session
    this.state = {
      isFullscreen: Boolean(document.fullscreenElement),
      resizeSession: true,
      speedDialDirection: 'up',
      tooltipPlacement: 'left',
      qualityLevel: 6,
      compressionLevel: 2,
      resetDialogOpen: false,
      resetting: false,
      inHdMode: false,
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

  handleToggleResize = (_) => {
    const newResizeSession = !this.state.resizeSession;
    this.setState({
      resizeSession: newResizeSession,
    });
    this.props.rfb.resizeSession = newResizeSession;
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
    this.props.closeSpeedDial();

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
    if (ev.target.id !== 'reset-button') {
      this.setState({
        resetDialogOpen: false,
      });
    } else {
      this.setState({
        resetting: true,
      });
      this.props.onVNCReset();
      resetVNC(this.props.session_id);
    }
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
        if (data === 2) {
          webFrame.setZoomFactor(0.5);
          this.setState({
            inHdMode: true,
          });
        }

      });
    }

  }

  render() {
    const {
      speedDialOpen,
      onSpeedDialClose: handleSpeedDialClose,
      onSpeedDialOpen: handleSpeedDialOpen,
      onFabHide: handleFabHide,
    } = this.props;
    const {
      speedDialDirection,
      tooltipPlacement,
      qualityLevel,
      compressionLevel,
      resizeSession,
      isFullscreen,
      resetDialogOpen,
      resetting,
      inHdMode,
    } = this.state;

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
              key={'reset'}
              icon={<Refresh/>}
              tooltipTitle={<div className={'speed-dial-action-title'}>Reset
                VNC</div>}
              tooltipOpen
              tooltipPlacement={tooltipPlacement}
              onClick={this.handleResetConnection}
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
          {document.fullscreenEnabled &&
              <SpeedDialAction
                  key={'toggle-fullscreen'}
                  icon={isFullscreen ? <FullscreenExit/> : <Fullscreen/>}
                  tooltipTitle={<div className={'speed-dial-action-title'}>
                    {isFullscreen ? 'Exit' : 'Enter'} Full Screen
                  </div>}
                  tooltipOpen
                  tooltipPlacement={tooltipPlacement}
                  onClick={this.handleToggleFullscreen}
              />
          }
          <SpeedDialAction
              key={'toggle-resize'}
              icon={<Height/>}
              tooltipTitle={<Box display={'flex'} width={200}>
                <Box flexGrow={1} className={'speed-dial-action-title'}>Auto
                  Resize</Box>
                <Box>{resizeSession ?
                    <span id={'auto-resize-enabled-text'}> Enabled</span> :
                    <span id={'auto-resize-disabled-text'}> Disabled</span>
                }</Box>
              </Box>}
              tooltipOpen
              tooltipPlacement={tooltipPlacement}
              onClick={this.handleToggleResize}
          />
          {webFrame && <SpeedDialAction
              key={'hd-mode'}
              icon={inHdMode ? <Sd/> : <Hd/>}
              tooltipTitle={<div className={'speed-dial-action-title'}>
                {inHdMode ? 'Exit' : 'Enter'} HD Mode</div>}
              tooltipOpen
              tooltipPlacement={tooltipPlacement}
              onClick={this.handleHDModeToggle}
          />}
          <br/>
          <SpeedDialAction
              key={'quality'}
              icon={<HighQuality/>}
              tooltipTitle={<Stack>
                <Box display={'flex'} width={200}>
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
                <Box display={'flex'} width={200}>
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
          <Dialog
              open={resetDialogOpen}
              keepMounted
              onClose={this.handleResetDialogClose}
          >
            <DialogTitle>{'Do you wish to reset the VNC session? '}</DialogTitle>
            <DialogContent>
              <DialogContentText>
                If you broke the VNC session by mistakenly logging out in the
                VNC screen,
                or you wish to change your VNC password, you may proceed to
                reset your VNC settings.
              </DialogContentText>
            </DialogContent>
            <DialogActions>
              <Button onClick={this.handleResetDialogClose}>Cancel</Button>
              <LoadingButton
                  id={'reset-button'}
                  variant={'contained'}
                  loading={resetting}
                  loadingPosition="start"
                  startIcon={<Refresh/>}
                  onClick={this.handleResetDialogClose}
              >
                Reset
              </LoadingButton>
            </DialogActions>
          </Dialog>
        </>
    );
  }
}

