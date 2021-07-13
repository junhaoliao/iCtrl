import React from 'react';
import RFB from '@novnc/novnc/core/rfb';
import axios from 'axios';
import Loading from '../../components/Loading';
import {VNCSteps} from '../../components/Loading/steps';
import {VNCAuthentication} from '../../components/Loading/authentications';
import {ICtrlError, ICtrlStep} from '../../../actions/codes';
import {Helmet} from 'react-helmet';


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

        this.state = {
            loading: true,
            currentStep: -1,
            authentication: null
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
                    const url = `ws://localhost:${port}`;
                    // Creating a new RFB object will start a new connection
                    const rfb = new RFB(
                        document.getElementById('screen'),
                        url,
                        {credentials: {password: passwd}});
                    rfb.resizeSession = true;
                    rfb.addEventListener('connect', () => {
                        this.setState({
                            loading: false
                        });
                    });
                    rfb.addEventListener('clipboard', (ev) => {
                        navigator.clipboard.writeText(ev.detail.text).then();
                    });
                    let clipboardText = null;
                    window.onfocus = ev => {
                        navigator.clipboard.readText().then((text) => {
                            if (clipboardText !== text) {
                                clipboardText = text;
                                rfb.clipboardPasteFrom(text);
                            }
                        });
                    };
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
        this.connect();
    }

    render() {
        const {host, username} = this.props.profiles.sessions[this.session_id];

        return (<div>
                <Helmet>
                    <title>{`VNC - ${username}@${host}`}</title>
                    <link rel="icon" href={`/favicon/VNC/${this.session_id}`} />
                </Helmet>
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