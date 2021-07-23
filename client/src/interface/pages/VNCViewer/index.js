import React from 'react';
import RFB from '@novnc/novnc/core/rfb';
import axios from 'axios';
import Loading from '../../components/Loading';
import {VNCSteps} from '../../components/Loading/steps';
import {VNCAuthentication} from '../../components/Loading/authentications';
import {ICtrlError, ICtrlStep} from '../../../actions/codes';
import {Helmet, HelmetProvider} from 'react-helmet-async';
import {Backdrop} from '@material-ui/core';
import VNCSpeedDial from './VNCSpeedDial';


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

    connect = () => {
        fetch(`/vnc`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({session_id: this.session_id})
        }).then(response => {
            if (response.status !== 200) {
                console.log('error');
                return;
            }
            const reader = response.body.getReader();
            const data = [];
            const readStream = ({value, done}) => {
                if (done) {
                    const resultArr = new Uint8Array(data.slice(data.indexOf(ICtrlStep.VNC.DONE) + 1));
                    const decodedStr = new TextDecoder().decode(resultArr);
                    const {port, passwd} = JSON.parse(decodedStr);
                    const url = `ws://192.168.2.129:${port}`;
                    // Creating a new RFB object will start a new connection
                    this.rfb = new RFB(
                        document.getElementById('screen'),
                        url,
                        {credentials: {password: passwd}});
                    this.rfb.resizeSession = true;
                    this.rfb.addEventListener('connect', () => {
                        this.setState({
                            loading: false
                        });


                        this.rfb.addEventListener('clipboard', (ev) => {
                            try {
                                navigator.clipboard.writeText(ev.detail.text).then();
                            } catch (e) {
                                // 2 cases:
                                // 1) not hosting over https on the server
                                // 2) the browser is too old to support clipboard
                                console.log(e);
                            }
                        });
                        let clipboardText = null;
                        window.onfocus = _ => {
                            try {
                                navigator.clipboard.readText().then((text) => {
                                    if (clipboardText !== text) {
                                        clipboardText = text;
                                        this.rfb.clipboardPasteFrom(text);
                                    }
                                });
                            } catch (e) {
                                // ditto
                                console.log(e);
                            }
                        };
                    });

                    return;
                }
                data.push(...value);
                if (data.includes(ICtrlStep.VNC.DONE)) {
                    // streaming the result
                    this.setState({
                        currentStep: ICtrlStep.VNC.DONE
                    });
                } else {
                    const currentStep = value.slice(-1)[0];
                    if (currentStep < 100) {
                        // not an error
                        this.setState({
                            currentStep: currentStep
                        });
                    } else {
                        if (currentStep === ICtrlError.VNC.PASSWD_MISSING) {
                            const myVNCAuthentication = Object.assign(VNCAuthentication);
                            myVNCAuthentication.submitter = (authInput) => {
                                this.setState({
                                    currentStep: 0,
                                    authentication: null
                                });
                                axios.post('/vncpasswd', {
                                    session_id: this.session_id,
                                    passwd: authInput
                                }).then(response => {
                                    console.log(response);
                                    this.connect();
                                }).catch(error => {
                                    console.log(error);
                                });

                            };
                            this.setState({
                                authentication: myVNCAuthentication
                            });
                        }


                        // stop reading the stream now that an error occurs
                        return;
                    }

                }

                reader.read().then(readStream);
            };
            reader.read().then(readStream);
        });
    };

    componentDidMount() {
        // some mobile browser doesn't have the address bar adjusted
        //  when we set the screen's height to 100vh, so we will need to
        //  overwrite this manually
        const resetHeight = () => {
            document.getElementById('screen').style.height = window.innerHeight + 'px';
        };
        window.addEventListener('resize', resetHeight);
        resetHeight();

        this.connect();
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
        const {speedDialOpen} = this.state;
        return (<div>
                <HelmetProvider>
                    <Helmet>
                        <title>{`VNC - ${username}@${host}`}</title>
                        <link rel="icon" href={`/favicon/VNC/${this.session_id}`}/>
                    </Helmet>
                </HelmetProvider>
                <Backdrop open={speedDialOpen}/>
                {this.state.showFab && !this.state.loading &&
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


                {this.state.loading &&
                <Loading
                    currentStep={this.state.currentStep}
                    steps={VNCSteps}
                    authentication={this.state.authentication}/>}
                <div style={{height: '100vh', width: '100vw', display: this.state.loading && 'none'}} id={'screen'}/>
            </div>

        );
    }

}