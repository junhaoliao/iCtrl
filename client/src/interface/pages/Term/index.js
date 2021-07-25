import React from 'react';
import {Terminal} from 'xterm';
import 'xterm/css/xterm.css';
import {AttachAddon} from 'xterm-addon-attach';
import {FitAddon} from 'xterm-addon-fit';
import {WebglAddon} from 'xterm-addon-webgl';
import axios from 'axios';
import {Helmet, HelmetProvider} from 'react-helmet-async';

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

            const addon = new WebglAddon();
            addon.onContextLoss(e => {
                addon.dispose();
            });
            term.loadAddon(addon);

            this.term_id = response.data;
            const socket = new WebSocket(`ws://127.0.0.1:8000/${this.term_id}`);
            const attachAddon = new AttachAddon(socket);
            term.loadAddon(attachAddon);

            term.onResize(({cols, rows}) => {
                if (this.term_id != null) {
                    axios.patch(`/terminal_resize`, {
                        session_id: this.session_id,
                        term_id: this.term_id,
                        w: cols,
                        h: rows
                    }).then(_ => {
                        // console.log(response);
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
        const {host, username} = this.props.profiles.sessions[this.session_id];

        return (
            <div>
                <HelmetProvider>
                    <Helmet>
                        <title>{`Terminal - ${username}@${host}`}</title>
                        <link rel="icon" href={`/favicon/term/${this.session_id}`}/>
                    </Helmet>
                </HelmetProvider>

                <div id="terminal" style={{position: 'absolute', top: 0, bottom: 0, left: 0, right: 0}}/>
            </div>
        );
    }
}