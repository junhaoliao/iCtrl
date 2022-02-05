import React from 'react';
import {
    Box,
    Button,
    Dialog,
    DialogActions,
    DialogContent,
    DialogContentText,
    DialogTitle, IconButton,
    Slider,
    SpeedDial,
    SpeedDialAction,
    SpeedDialIcon,
    Stack, Typography,
} from '@material-ui/core';
import {
    Add,
    Fullscreen,
    FullscreenExit,
    Height,
    HighQuality,
    Keyboard,
    LensBlur,
    Refresh, Remove,
    VisibilityOff, ZoomIn,
} from '@material-ui/icons';

import './index.css';
import {LoadingButton} from '@material-ui/lab';
import {focusOnKeyboard, resetVNC} from '../../../actions/vnc';

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
            zoomLevel: 100
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
    };

    handleZoomLevelChange = (operation) => {
        let zoomLevel = this.state.zoomLevel;
        if (operation === 'zoom-out'){
            zoomLevel -= 25;
        } else if (operation === 'zoom-in'){
            zoomLevel += 25;
        }
        this.props.rfb.zoomLevel = zoomLevel/100;

        this.setState({
            zoomLevel: zoomLevel,
        });
    };


    handleQualityLevelChange = (ev) => {
        const value = ev.target.value;
        this.setState({
            qualityLevel: value,
        });
        this.props.rfb.qualityLevel = value;
    };

    handleCompressionLevelChange = (ev) => {
        const value = ev.target.value;
        this.setState({
            compressionLevel: value,
        });
        this.props.rfb.compressionLevel = value;
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
            resetVNC(this.props.session_id);
        }
    };

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
            zoomLevel,
            compressionLevel,
            resizeSession,
            isFullscreen,
            resetDialogOpen,
            resetting,
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
                    tooltipTitle={`Hide`}
                    tooltipOpen
                    tooltipPlacement={tooltipPlacement}
                    onClick={handleFabHide}
                />
                <SpeedDialAction
                    key={'reset'}
                    icon={<Refresh/>}
                    tooltipTitle={'Reset'}
                    tooltipOpen
                    tooltipPlacement={tooltipPlacement}
                    onClick={this.handleResetConnection}
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
                    tooltipTitle={<div id={'auto-resize-tooltip-title'}>Auto Resize
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
                    key={'zoom'}
                    icon={<ZoomIn/>}
                    tooltipTitle={<Stack>
                        <Stack direction={"row"} sx={{width: 200}}>
                            <Typography flexGrow={1}>Zoom Level</Typography>
                            <IconButton size={'small'} onClick={()=>{this.handleZoomLevelChange('zoom-out');}}><Remove/></IconButton>
                            <Typography align={'center'}>{zoomLevel} %</Typography>
                            <IconButton size={'small'} edge={'end'} onClick={()=>{this.handleZoomLevelChange('zoom-in');}}><Add/></IconButton>
                        </Stack>
                    </Stack>}
                    tooltipOpen
                    tooltipPlacement={tooltipPlacement}
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
            </SpeedDial>
                <Dialog
                    open={resetDialogOpen}
                    keepMounted
                    onClose={this.handleResetDialogClose}
                >
                    <DialogTitle>{'Do you wish to reset the VNC session? '}</DialogTitle>
                    <DialogContent>
                        <DialogContentText>
                            If you broke the VNC session by mistakenly logging out in the VNC screen,
                            or you wish to change your VNC password, you may proceed to reset your VNC settings.
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

