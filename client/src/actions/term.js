import axios from 'axios';
import {Terminal} from 'xterm';
import {WebglAddon} from 'xterm-addon-webgl';
import {AttachAddon} from 'xterm-addon-attach';
import {FitAddon} from 'xterm-addon-fit';


export const termConnect = (sessionID) => {
    axios.post(`/terminal`, {
            session_id: sessionID
        }).then((response)=>{
/* setup DOM */
        const term_div = document.getElementById('terminal');
        const term = new Terminal();
        term.open(term_div);

        /* setup WebGL */
        const addon = new WebglAddon();
        addon.onContextLoss(_ => {
            addon.dispose();
        });
        term.loadAddon(addon);

        /* setup WebSocket */
        const {port, term_id} = response.data
        const socket = new WebSocket(`ws://127.0.0.1:${port}/${term_id}`);
        socket.onopen = (_) => {
            const attachAddon = new AttachAddon(socket);
            term.loadAddon(attachAddon);
        }
        socket.onclose = (ev) => {
            term.write('\r\niCtrl: WebSocket closed')
            console.log(ev)
        }

        /* setup right-click to copy/paste */
        try {
            navigator.clipboard.readText().then(_ => {
                term_div.onauxclick = (ev) => {
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
                    // prevent the context menu from opening
                    ev.preventDefault();
                };
            }).catch(error => {
                // clipboard permission not given
                console.log(error);
            });
        } catch (e) {
            console.log('clipboard not permitted / supported');
        }

        /* setup the resize behaviours */
        let resize_timeout = null
        term.onResize(({cols, rows}) => {
            // add a 500 ms delay to prevent requesting terminal resize too frequently,
            //  thus saving network bandwidth among the client, the server, and the target
            clearTimeout(resize_timeout);
            resize_timeout = setTimeout(() => {
                axios.patch(`/terminal_resize`, {
                    session_id: sessionID,
                    term_id: term_id,
                    w: cols,
                    h: rows
                }).then(_ => {
                    term.scrollToBottom();
                }).catch(error => {
                    console.log(error);
                });
            }, 500);
        });
        const fitAddon = new FitAddon();
        term.loadAddon(fitAddon);
        fitAddon.fit();
        window.onresize = () => {
            fitAddon.fit();
        };

        /* focus on the terminal once everything finishes loading */
        term.focus()
    }).catch((error)=>{
        // POST "/terminal" error
        console.log(error)
    })
}