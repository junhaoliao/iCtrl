import React from 'react';
import 'xterm/css/xterm.css';
import {Helmet, HelmetProvider} from 'react-helmet-async';
import {termConnect} from '../../../actions/term';

export default class Term extends React.Component {
    constructor(props) {
        super(props);
        const {match: {params}} = this.props;
        this.session_id = params.session_id;

        this.resize_timeout = null;
    }

    componentDidMount() {
        termConnect(this.session_id);
    }

    render() {
        const {host, username} = this.props.profiles['sessions'][this.session_id];

        return (
            <div>
                <HelmetProvider>
                    <Helmet>
                        <title>{`Terminal - ${username}@${host}`}</title>
                        <link rel="icon" href={`/favicon/terminal/${this.session_id}`}/>
                    </Helmet>
                </HelmetProvider>

                <div id="terminal" style={{position: 'absolute', top: 0, bottom: 0, left: 0, right: 0}}/>
            </div>
        );
    }
}