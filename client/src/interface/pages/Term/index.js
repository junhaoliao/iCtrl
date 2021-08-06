import React from 'react';
import 'xterm/css/xterm.css';
import {termConnect} from '../../../actions/term';
// import Loading from '../../components/Loading';
// import {VNCSteps} from '../../components/Loading/steps';
import {changeFavicon} from '../../utils';

export default class Term extends React.Component {
    constructor(props) {
        super(props);
        const {match: {params}} = this.props;
        this.session_id = params.session_id;

        this.resize_timeout = null;
        // this.state = {
        //     loading: false,
        //     currentStep: -1,
        //     authentication: null
        // };
    }

    componentDidMount() {
        const {host, username} = this.props.profiles['sessions'][this.session_id];
        document.title = `Terminal - ${username}@${host}`;

        changeFavicon(`/favicon/terminal/${this.session_id}`);

        termConnect(this);
    }

    render() {
        // const {authentication, currentStep, loading} = this.state;

        return (
            <div>
                {/*{loading &&*/}
                {/*<Loading*/}
                {/*    currentStep={currentStep}*/}
                {/*    steps={VNCSteps}*/}
                {/*    authentication={authentication}/>}*/}

                <div id="terminal" style={{position: 'absolute', top: 0, bottom: 0, left: 0, right: 0}}/>
            </div>
        );
    }
}