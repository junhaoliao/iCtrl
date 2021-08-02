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

        this.resize_timeout = null;
    }

    componentDidMount() {
        axios.post(`/terminal`, {
            session_id: this.session_id
        }).then(response => {
            const term_div = document.getElementById('terminal');
            const term = new Terminal();
            term.open(term_div);

            const addon = new WebglAddon();
            addon.onContextLoss(_ => {
                addon.dispose();
            });
            term.loadAddon(addon);

            this.term_id = response.data['term_id'];
            const socket = new WebSocket(`ws://127.0.0.1:${response.data['port']}/${this.term_id}`);
            const attachAddon = new AttachAddon(socket);
            term.loadAddon(attachAddon);

            try {
                navigator.clipboard.readText().then(_ => {
                    term_div.onauxclick = ev => {
                        if (ev.button === 2) {
                            const selection = term.getSelection();
                            if (selection === '') {
                                navigator.clipboard.readText().then(text => {
                                    socket.send(text);
                                });
                            } else {
                                navigator.clipboard.writeText(selection).then();
                                term.clearSelection();
                            }
                        }
                    };
                    term_div.oncontextmenu = ev => {
                        ev.preventDefault();
                    };
                }).catch(error => {
                    // clipboard permission not given
                    console.log(error);
                });
            } catch (e) {
                console.log('clipboard not permitted / supported');
            }

            // setup the resize behaviours
            term.onResize(({cols, rows}) => {
                if (this.term_id != null) {
                    // add a 500 ms delay to prevent requesting terminal resize too frequently,
                    //  thus saving network bandwidth among the client, the server, and the target
                    clearTimeout(this.resize_timeout);
                    this.resize_timeout = setTimeout(() => {
                        axios.patch(`/terminal_resize`, {
                            session_id: this.session_id,
                            term_id: this.term_id,
                            w: cols,
                            h: rows
                        }).then(_ => {
                            term.scrollToBottom();
                        }).catch(error => {
                            console.log(error);
                        });
                    }, 500);
                }
            });
            const fitAddon = new FitAddon();
            term.loadAddon(fitAddon);
            fitAddon.fit();
            window.onresize = () => {
                fitAddon.fit();
            };

            // focus on the terminal once everything finishes loading
            term.focus()
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
                        <link rel="icon" href={`/favicon/terminal/${this.session_id}`}/>
                    </Helmet>
                </HelmetProvider>

                <div id="terminal" style={{position: 'absolute', top: 0, bottom: 0, left: 0, right: 0}}/>
            </div>
        );
    }
}