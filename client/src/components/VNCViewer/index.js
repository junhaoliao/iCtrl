import React from 'react';
import RFB from '@novnc/novnc/core/rfb';
import axios from 'axios';
import Loading from '../Loading';
import {VNCSteps} from '../Loading/steps';
import {htmlResponseToReason} from '../../actions/utils';
import {VNCAuthentication} from '../Loading/authentications';


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
            currentStep: 0,
            authentication: null
        };
    }

    connect = () => {
        axios.post(`/vnc`, {
            session_id: this.session_id
        }).then(response => {
            this.setState({
                currentStep: 4
            });
            const {port, passwd} = response.data;
            const url = `ws://localhost:${port}`;
            // Creating a new RFB object will start a new connection
            const rfb = new RFB(
                document.getElementById('screen'),
                url,
                {credentials: {password: passwd}});
            rfb.resizeSession = true;
            this.setState({
                currentStep: 5
            });
            rfb.addEventListener('connect', () => {
                this.setState({
                    loading: false
                });
            });
        }).catch(error => {
            if (error.response) {
                const reason = htmlResponseToReason(error.response.data).split('\n')[1]
                if (reason==='VNC password missing'){
                    const myVNCAuthentication = Object.assign(VNCAuthentication)
                    myVNCAuthentication.submitter = (authInput)=>{
                        this.setState({
                            authentication: null,
                            currentStep: 3
                        })
                        axios.post('/vncpasswd',{
                            session_id: this.session_id,
                            passwd: authInput
                        }).then(response=>{
                            console.log(response)
                            this.connect()
                        }).catch(error=>{
                            console.log(error)
                        })

                    }
                    this.setState({
                        currentStep:2,
                        authentication: myVNCAuthentication
                    })
                }
            } else {
                // Something happened in setting up the request that triggered an Error
                console.log('Error: ' + error.message);
            }
        });
    };

    componentDidMount() {
        this.connect();
    }

    render() {
        return (<div>
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