import React from 'react';
import {Box, Slider, SpeedDial, SpeedDialAction, SpeedDialIcon, Stack} from '@material-ui/core';
import {Fullscreen, FullscreenExit, Height, HighQuality, Keyboard, LensBlur, VisibilityOff} from '@material-ui/icons';
import {iOS} from '../../../actions/utils';

import './index.css';

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
            compressionLevel: 2
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
        this.props.closeSpeedDial();
        const fab = document.getElementById('fab');
        const width = 56;

        // prevent the speed dial from opening when using a mouse
        if (ev.touches === undefined) {
            this.props.onFabMove();
        }

        const pointX = ev.touches ? ev.touches[0].clientX : ev.clientX;
        const pointY = ev.touches ? ev.touches[0].clientY : ev.clientY;

        // adjust the tooltip placement according to the mouse point
        // we should only update the state if placement is different from the state
        //  to avoid unnecessary re-render
        if (pointX < window.innerWidth / 2) {
            if (this.state.tooltipPlacement === 'left') {
                this.setState({
                    tooltipPlacement: 'right'
                });
            }
        } else {
            if (this.state.tooltipPlacement === 'right') {
                this.setState({
                    tooltipPlacement: 'left'
                });
            }
        }

        if (pointY < window.innerHeight / 2) {
            if (this.state.speedDialDirection === 'up') {
                this.setState({
                    speedDialDirection: 'down'
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
                    speedDialDirection: 'up'
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
    };


    handleQualityLevelChange = (ev) => {
        const value = ev.target.value;
        this.setState({
            qualityLevel: value
        });
        this.props.rfb.qualityLevel = value;
    };

    handleCompressionLevelChange = (ev) => {
        const value = ev.target.value;
        this.setState({
            compressionLevel: value
        });
        this.props.rfb.compressionLevel = value;
    };

    handleToggleResize = (_) => {
        const newResizeSession = !this.state.resizeSession;
        this.setState({
            resizeSession: newResizeSession
        });
        this.props.rfb.resizeSession = newResizeSession;
    };

    handleToggleFullscreen = (_) => {
        if (Boolean(document.fullscreenElement)) {
            document.exitFullscreen().then();
            this.setState({
                isFullscreen: false
            });
        } else {
            document.body.requestFullscreen().then();
            this.setState({
                isFullscreen: true
            });
        }
    };

    handleKeyboardOpen = (ev) => {
        this.props.closeSpeedDial();
        if (iOS()) {
            const canvas = document.getElementById('screen').lastElementChild.firstElementChild;
            canvas.setAttribute('contenteditable', 'true');
            canvas.focus();
            canvas.setAttribute('contenteditable', 'false');
        } else {
            const textarea = document.getElementById('textarea');
            textarea.focus();
        }
    };

    render() {
        const {
            speedDialOpen,
            onSpeedDialClose: handleSpeedDialClose,
            onSpeedDialOpen: handleSpeedDialOpen,
            onFabHide: handleFabHide
        } = this.props;
        const {
            speedDialDirection,
            tooltipPlacement,
            qualityLevel,
            compressionLevel,
            resizeSession,
            isFullscreen
        } = this.state;

        return (<SpeedDial
            id={'fab'}
            className={'no_select'}
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
                tooltipTitle={`Hide`}
                tooltipOpen
                tooltipPlacement={tooltipPlacement}
                onClick={handleFabHide}
            />
            <SpeedDialAction
                key={'open-keyboard'}
                icon={<Keyboard/>}
                tooltipTitle={'Keyboard'}
                tooltipOpen
                tooltipPlacement={tooltipPlacement}
                onClick={this.handleKeyboardOpen}
            />
            {document.fullscreenEnabled &&
            <SpeedDialAction
                key={'toggle-fullscreen'}
                icon={isFullscreen ? <FullscreenExit/> : <Fullscreen/>}
                tooltipTitle={<div style={{width: isFullscreen ? 108 : 119}}>
                    {isFullscreen ? 'Exit' : 'Enter'} Fullscreen
                </div>}
                tooltipOpen
                tooltipPlacement={tooltipPlacement}
                onClick={this.handleToggleFullscreen}
            />
            }
            <SpeedDialAction
                key={'toggle-resize'}
                icon={<Height/>}
                tooltipTitle={<div id={'auto-resize-tooltip-title'}>Auto Resize:
                    {resizeSession ?
                        <div id={'auto-resize-enabled-text'}>Enabled</div> :
                        <div id={'auto-resize-disabled-text'}>Disabled</div>
                    }
                </div>}
                tooltipOpen
                tooltipPlacement={tooltipPlacement}
                onClick={this.handleToggleResize}
            />
            <br/>
            <SpeedDialAction
                key={'quality'}
                icon={<HighQuality/>}
                tooltipTitle={<Stack>
                    <Box display={'flex'}>
                        <Box flexGrow={1}>Quality</Box>
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
                        sx={{width: 200}}
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
                    <Box display={'flex'}>
                        <Box flexGrow={1}>Compression</Box>
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
                        sx={{width: 200}}
                    />
                </Stack>}
                tooltipOpen
                tooltipPlacement={tooltipPlacement}
            />
        </SpeedDial>);
    }
}

