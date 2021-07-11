/* eslint-disable react-hooks/rules-of-hooks */
import React from 'react';
import {Terminal} from 'xterm';
import 'xterm/css/xterm.css';
import {AttachAddon} from 'xterm-addon-attach';
import {FitAddon} from 'xterm-addon-fit';
import axios from 'axios';

export default class Term extends React.Component {
    constructor(props) {
        super(props);
        const {match: {params}} = this.props;
        this.session_id = params.session_id;
        this.term_id = null;
    }

    componentDidMount() {
        axios.post(`/terminal`, {
            session_id: this.session_id
        }).then(response => {
            const term = new Terminal();
            term.open(document.getElementById('terminal'));

            this.term_id = response.data;
            const socket = new WebSocket(`ws://localhost:8000/${this.term_id}`);
            const attachAddon = new AttachAddon(socket);
            term.loadAddon(attachAddon);

            term.onResize(({cols, rows}) => {
                if (this.term_id != null) {
                    axios.patch(`/terminal_resize`, {
                        session_id: this.session_id,
                        term_id: this.term_id,
                        w: cols,
                        h: rows
                    }).then(response => {
                        console.log(response);
                    }).catch(error => {
                        console.log(error);
                    });
                }
            });
            const fitAddon = new FitAddon();
            term.loadAddon(fitAddon);
            fitAddon.fit();
            window.onresize = () => {
                fitAddon.fit();
            };

        }).catch(error => {
            console.log(error);
        });
    }

    render() {
        return (
            <div id="terminal" style={{height: '100vh'}}/>
        );
    }
}