import React from 'react';

import {Helmet, HelmetProvider} from 'react-helmet-async';
import {Backdrop} from '@material-ui/core';

import './index.css';
import Loading from '../../components/Loading';
import {VNCSteps} from '../../components/Loading/steps';
import VNCSpeedDial from './VNCSpeedDial';
import {vncConnect} from '../../../actions/vnc';

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
            speedDialOpen: false
        };
    }

    keyboardInputReset = () => {
        this.keyboardElem.value = new Array(100).join('_');
        this.lastKeyboardinput = this.keyboardElem.value;
    };

    componentDidMount() {
        vncConnect(this).then();
    }

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
    };

    render() {
        const {host, username} = this.props.profiles['sessions'][this.session_id];
        const {authentication, currentStep, loading, speedDialOpen, showFab} = this.state;
        return (<div>
                <HelmetProvider>
                    <Helmet>
                        <title>{`VNC - ${username}@${host}`}</title>
                        <link rel="icon" href={`/favicon/VNC/${this.session_id}`}/>
                    </Helmet>
                </HelmetProvider>

                <Backdrop id={'speed-dial-backdrop'} open={speedDialOpen}/>
                {showFab && !loading &&
                <VNCSpeedDial
                    rfb={this.rfb}
                    speedDialOpen={speedDialOpen}
                    onSpeedDialClose={this.handleSpeedDialClose}
                    onSpeedDialOpen={this.handleSpeedDialOpen}
                    closeSpeedDial={this.closeSpeedDial}
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
                <div style={{display: loading && 'none'}} id={'screen'}>
                    <textarea id={'textarea'} autoCapitalize="off"
                              autoComplete="off" spellCheck="false" tabIndex="-1"
                    />
                </div>
            </div>
        );
    }
}