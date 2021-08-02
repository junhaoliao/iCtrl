import {ICtrlError, ICtrlStep} from './codes';
import RFB from '@novnc/novnc/core/rfb';
import KeyTable from '@novnc/novnc/core/input/keysym';
import keysyms from '@novnc/novnc/core/input/keysymdef';
import {VNCAuthentication} from '../interface/components/Loading/authentications';
import axios from 'axios';

export const vncConnect = async (vncViewer) => {
    const options = {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({session_id: vncViewer.session_id})
    };
    const response = await fetch(`/vnc`, options);
    if (response.status !== 200) {
        console.log(response.body);
        return;
    }

    // the steps will be streamed as the server establishes the connection to the target
    //  so we will need a ReadableStream Reader to get the current step, and the final response
    //  which contains the port to be used and the VNC password
    const reader = response.body.getReader();
    // this will store all the data read from the stream
    const data = [];
    const readStream = ({value, done}) => {
        // if the stream reading is done (end of stream),
        //  ignore all the step codes and parse the final response as JSON
        if (done) {
            const resultArr = new Uint8Array(data.slice(data.indexOf(ICtrlStep.VNC.DONE) + 1));
            const decodedStr = new TextDecoder().decode(resultArr);
            const {port, passwd} = JSON.parse(decodedStr);

            // Creating a new RFB object will start a new connection
            const url = `ws://127.0.0.1:${port}`;
            vncViewer.rfb = new RFB(
                document.getElementById('screen'),
                url,
                {credentials: {password: passwd}});

            /* Setup the VNC default options */
            // Reference: https://github.com/novnc/noVNC/blob/master/docs/API.md

            // resizeSession:
            // Is a boolean indicating if a request to resize the remote session should be sent
            //  whenever the container changes dimensions. Disabled by default.
            vncViewer.rfb.resizeSession = true;

            // when the VNC session is successfully established
            vncViewer.rfb.addEventListener('connect', () => {
                // hide the Loading element
                vncViewer.setState({
                    loading: false
                });

                /* Setup touch keyboard */
                // Reference: https://github.com/novnc/noVNC/blob/master/app/ui.js
                vncViewer.keyboardElem = document.getElementById('textarea');
                vncViewer.keyboardInputReset();

                vncViewer.keyboardElem.addEventListener('input', (event) => {
                    const newValue = event.target.value;
                    const oldValue = vncViewer.lastKeyboardinput;

                    let newLen;
                    try {
                        // Try to check caret position since whitespace at the end
                        // will not be considered by value.length in some browsers
                        newLen = Math.max(event.target.selectionStart, newValue.length);
                    } catch (err) {
                        // selectionStart is undefined in Google Chrome
                        newLen = newValue.length;
                    }
                    const oldLen = oldValue.length;

                    let inputs = newLen - oldLen;
                    let backspaces = inputs < 0 ? -inputs : 0;

                    // Compare the old string with the new to account for
                    // text-corrections or other input that modify existing text
                    for (let i = 0; i < Math.min(oldLen, newLen); i++) {
                        if (newValue.charAt(i) !== oldValue.charAt(i)) {
                            inputs = newLen - i;
                            backspaces = oldLen - i;
                            break;
                        }
                    }

                    // Send the key events
                    for (let i = 0; i < backspaces; i++) {
                        vncViewer.rfb.sendKey(KeyTable.XK_BackSpace, 'Backspace');
                    }
                    for (let i = newLen - inputs; i < newLen; i++) {
                        const key = newValue.charCodeAt(i);
                        if (key === 10) {
                            vncViewer.rfb.sendKey(KeyTable.XK_Return);
                        } else {
                            vncViewer.rfb.sendKey(keysyms.lookup(key));
                        }
                    }

                    // Control the text content length in the keyboardinput element
                    if (newLen > 2 * 100) {
                        vncViewer.keyboardInputReset();
                    } else if (newLen < 1) {
                        // There always have to be some text in the keyboardinput
                        // element with which backspace can interact.
                        vncViewer.keyboardInputReset();
                        // This sometimes causes the keyboard to disappear for a second
                        // but it is required for the android keyboard to recognize that
                        // text has been added to the field
                        event.target.blur();
                        // This has to be ran outside of the input handler in order to work
                        setTimeout(event.target.focus.bind(event.target), 0);
                    } else {
                        vncViewer.lastKeyboardinput = newValue;
                    }
                });

                // prevent the default behaviour of the 'submit' event
                vncViewer.keyboardElem.addEventListener('submit', () => false);

                /* Setup bi-directional clipboard forwarding */
                // TODO: keep an eye on the official support discussed on https://github.com/novnc/noVNC/pull/1562
                // remote -> local
                vncViewer.rfb.addEventListener('clipboard', (ev) => {
                    try {
                        navigator.clipboard.writeText(ev.detail.text).then();
                    } catch (e) {
                        // 3 cases of navigator.clipboard failure:
                        // 1) not hosting over https on the server
                        // 2) TODO: show a tutorial to approve clipboard permission if this is the case
                        //    the user didn't approve clipboard permission
                        // 3) the browser is too old to support clipboard
                        console.log(e);
                    }
                });

                // local -> remote
                // whenever the window gets focus (the user just switched from another tab/window),
                let clipboardText = null;
                window.onfocus = _ => {
                    try {
                        // compare the clipboard text with the previous one
                        // if they differ, submit the local clipbboard text to the remote
                        navigator.clipboard.readText().then((text) => {
                            if (clipboardText !== text) {
                                clipboardText = text;
                                vncViewer.rfb.clipboardPasteFrom(text);
                            }
                        });
                    } catch (e) {
                        // see above: 3 cases of navigator.clipboard failure
                        console.log(e);
                    }
                };
            });

            return;
        } // if (done)

        // if the steam is not finished, push the values that was read into 'data'
        data.push(...value);

        // the steam is in this format:
        // STEP1 | STEP2 | ... | _DONE_ | FINAL_RESPONSE
        // from above we can see step 'DONE' serve as a divider of the step codes and the final response

        // if the step 'DONE' is present in 'data'
        if (data.includes(ICtrlStep.VNC.DONE)) {
            // update the current step to 'DONE' and wait for the whole stream to be transferred
            vncViewer.setState({
                currentStep: ICtrlStep.VNC.DONE
            });
        } else {
            // if the step 'DONE' is not present in 'data',
            //  the last digit in the array must still be a step code
            //  rather than part of the final response
            const currentStep = value.slice(-1)[0];
            if (currentStep < 100) {
                // not an error
                vncViewer.setState({
                    currentStep: currentStep
                });
            } else {
                // handle the errors / server requests
                if (currentStep === ICtrlError.VNC.PASSWD_MISSING) {
                    // make a copy of the VNCAuthentication model
                    const myVNCAuthentication = Object.assign(VNCAuthentication);
                    myVNCAuthentication.submitter = (authInput) => {
                        vncViewer.setState({
                            currentStep: 0,
                            authentication: null
                        });
                        axios.post('/vncpasswd', {
                            session_id: vncViewer.session_id,
                            passwd: authInput
                        }).then(response => {
                            console.log(response);
                            vncViewer.connect();
                        }).catch(error => {
                            console.log(error);
                        });
                    };
                    vncViewer.setState({
                        authentication: myVNCAuthentication
                    });
                }

                // stop reading the stream now that an error occurs
                return;
            }

        }

        reader.read().then(readStream);
    };

    // make the call to read the steam
    reader.read().then(readStream);
};