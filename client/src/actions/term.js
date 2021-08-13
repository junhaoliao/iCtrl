import axios from 'axios';
import {Terminal} from 'xterm';
import {WebglAddon} from 'xterm-addon-webgl';
import {AttachAddon} from 'xterm-addon-attach';
import {FitAddon} from 'xterm-addon-fit';
import {ICtrlError, ICtrlStep} from './codes';
import {SSHHostUnreachableRefresh} from '../interface/components/Loading/authentications';

const setupDOM = () => {
    const term_div = document.getElementById('terminal');

    const term = new Terminal();
    term.open(term_div);

    return {term, term_div};
};

const setupWebGL = (term) => {
    const addon = new WebglAddon();
    addon.onContextLoss(_ => {
        addon.dispose();
    });
    term.loadAddon(addon);
};

const setupWebSocket = (term, term_id, port) => {
    const socket = new WebSocket(`ws://127.0.0.1:${port}/${term_id}`);

    socket.onopen = (_) => {
        const attachAddon = new AttachAddon(socket);
        term.loadAddon(attachAddon);
    };
    socket.onclose = (ev) => {
        term.write('\r\niCtrl: WebSocket closed');
        console.log(ev);
    };

    return socket;
};

const setupCopyPaste = (term, term_div, socket) => {
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
            term_div.oncontextmenu = (ev) => {
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
};

const setupResize = (term, sessionID, term_id) => {
    let resize_timeout = null;
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
};

export const termConnect = async (TermViewer) => {
    const options = {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({session_id: TermViewer.session_id})
    };

    const response = await fetch(`/terminal`, options);
    if (response.status !== 200) {
        console.log(response.body);
        return;
    }

    const reader = response.body.getReader();
    // this will store all the data read from the stream
    const data = [];
    const readStream = ({value, done}) => {
        // if the stream reading is done (end of stream),
        //  ignore all the step codes and parse the final response as JSON
        if (done) {
            const resultArr = new Uint8Array(data.slice(data.indexOf(ICtrlStep.Term.DONE) + 1));
            const decodedStr = new TextDecoder().decode(resultArr);
            const {term_id, port} = JSON.parse(decodedStr);

            const {term, term_div} = setupDOM();
            setupWebGL(term);
            const socket = setupWebSocket(term, term_id, port);
            setupCopyPaste(term, term_div, socket);
            setupResize(term, TermViewer.session_id, term_id);

            /* need to set the state 'loading' to false so that the term div is visible and can be focused on */
            TermViewer.setState({
                loading: false
            });

            /* focus on the terminal once everything finishes loading */
            term.focus();

            return;
        } // if (done)

        // if the stream is not finished, push the values that was read into 'data'
        data.push(...value);

        // the stream is in this format:
        // STEP1 | STEP2 | ... | _DONE_ | FINAL_RESPONSE
        // from above we can see step 'DONE' serve as a divider of the step codes and the final response

        // if the step 'DONE' is present in 'data'
        if (data.includes(ICtrlStep.Term.DONE)) {
            // update the current step to 'DONE' and wait for the whole stream to be transferred
            TermViewer.setState({
                currentStep: ICtrlStep.Term.DONE
            });
        } else {
            // if the step 'DONE' is not present in 'data',
            //  the last digit in the array must still be a step code
            //  rather than part of the final response
            const currentStep = value.slice(-1)[0];
            if (currentStep < 100) {
                // not an error
                TermViewer.setState({
                    currentStep: currentStep
                });
            } else {
                TermViewer.setState({
                    currentStep: data.slice(-2)[0]
                });
                // handle the errors / server requests
                if (currentStep === ICtrlError.SSH.HOST_UNREACHABLE) {
                    TermViewer.setState({
                        authentication: SSHHostUnreachableRefresh
                    });
                } else {
                    console.log(`Term error code: ${currentStep}`);
                    console.log(data);
                }

                // stop reading the stream now that an error occurs
                return;
            }

        }

        reader.read().then(readStream);
    };
    // make the call to read the stream
    reader.read().then(readStream);
};