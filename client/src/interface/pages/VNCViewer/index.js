import React from 'react';
import {Backdrop} from '@material-ui/core';

import './index.css';
import Loading from '../../components/Loading';
import {VNCSteps} from '../../components/Loading/steps';
import VNCSpeedDial from './VNCSpeedDial';
import {vncConnect} from '../../../actions/vnc';
import {changeFavicon} from '../../utils';
import Toolbar from '../../components/Toolbar';
import KeyTable from '@novnc/novnc/core/input/keysym';


export default class VNCViewer extends React.Component {
    constructor(props) {
        super(props);
        const {
            match: {params},
            profiles: {sessions}
        } = props;

        this.session_id = params.session_id;
        this.username = sessions[this.session_id].username;
        this.host = sessions[this.session_id].host;

        this.rfb = null;
        this.lastKeyboardinput = null;

        this.fabMoved = false;
        this.speedDialOpenTime = 0;

        this.state = {
            loading: true,
            currentStep: -1,
            authentication: null,
            showFab: true,
            speedDialOpen: false,
            showToolbar: false
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

        // prevent the speed dial from opening when using a mouse
        if (this.fabMoved) {
            this.fabMoved = false;
            return;
        }

        this.speedDialOpenTime = new Date().getTime();
        this.setState({
            speedDialOpen: true
        });
    };

    closeSpeedDial = () => {
        this.setState({
            speedDialOpen: false
        });
    };

    handleSpeedDialClose = (ev) => {
        if (ev.type === 'mouseleave' || (new Date().getTime() - this.speedDialOpenTime) < 200) {
            return;
        }

        this.closeSpeedDial();
    };

    handleFabHide = () => {
        this.setState({
            showFab: false,
            speedDialOpen: false
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
        this.keyboardElem.focus();
    };

    handleToolbarOpen = () => {
        this.rfb.focusOnClick = false;
        this.setState({
            showToolbar: true
        });
    };
    handleToolbarHide = () => {
        this.rfb.focusOnClick = true;
        this.setState({
            showToolbar: false
        });
        this.rfb.focus();
    };

    componentDidMount() {
        const {host, username} = this.props.profiles['sessions'][this.session_id];
        document.title = `VNC - ${username}@${host}`;

        changeFavicon(`/favicon/vnc/${this.session_id}`);
        vncConnect(this).then();
    }

    render() {

        const {authentication, currentStep, loading, speedDialOpen, showFab, showToolbar} = this.state;
        return (<div>
                <Backdrop id={'speed-dial-backdrop'} open={speedDialOpen}/>
                {showFab && !loading &&
                <VNCSpeedDial
                    session_id={this.session_id}
                    rfb={this.rfb}
                    speedDialOpen={speedDialOpen}
                    onSpeedDialClose={this.handleSpeedDialClose}
                    onSpeedDialOpen={this.handleSpeedDialOpen}
                    closeSpeedDial={this.closeSpeedDial}
                    onToolbarOpen={this.handleToolbarOpen}
                    onFabMove={() => {
                        this.fabMoved = true;
                    }}
                    onFabHide={this.handleFabHide}/>
                }

                {loading &&
                <Loading
                    currentStep={currentStep}
                    steps={VNCSteps}
                    authentication={authentication}/>}

                <div style={{display: loading && 'none'}} id={'screen'}
                     className={showToolbar ? 'screen-with-toolbar' : ''}>
                    <textarea id={'textarea'} autoCapitalize="off"
                              autoComplete="off" spellCheck="false" tabIndex="-1"
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