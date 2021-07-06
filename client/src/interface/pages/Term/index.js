/* eslint-disable react-hooks/rules-of-hooks */
import React from 'react';
import { Terminal } from 'xterm';
import 'xterm/css/xterm.css';
import { AttachAddon } from 'xterm-addon-attach';
import { FitAddon } from 'xterm-addon-fit';

export default class Term extends React.Component {
    constructor(props) {
        super(props);
        const {match: {params}} = this.props;
        this.session_id = params.session_id;
    }
    
    componentDidMount() {
        const request = new XMLHttpRequest();
        request.addEventListener('load', (ev) => {
            const term_id = request.response;
            const term = new Terminal();
            term.open(document.getElementById('terminal'));
            const socket = new WebSocket(`ws://localhost:8000/${term_id}`);
            const attachAddon = new AttachAddon(socket);
            const fitAddon = new FitAddon();
            term.loadAddon(fitAddon);
            term.loadAddon(attachAddon);
            fitAddon.fit();
            window.onresize = () => {
                // console.log('resizing')
                fitAddon.fit();
            }
        });
        const formData = new FormData();
        formData.append('session_id', this.session_id);
        request.open('POST', '/terminal');
        request.send(formData);
    }

    render() {
        ***REMOVED***
        return (
            <div id="terminal" style={{ height: '100vh' }}></div>
        )
    }
}