/*
 * Copyright (c) 2021-2023 iCtrl Developers
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy
 *  of this software and associated documentation files (the "Software"), to
 *  deal in the Software without restriction, including without limitation the
 *  rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
 *  sell copies of the Software, and to permit persons to whom the Software is
 *  furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included in
 *  all copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 *  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 *  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 *  AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 *  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
 *  FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
 *  IN THE SOFTWARE.
 */

import {ICtrlError, ICtrlStep} from './codes';
import RFB from '@novnc/novnc/lib/rfb';
import KeyTable from '@novnc/novnc/lib/input/keysym';
import keysyms from '@novnc/novnc/lib/input/keysymdef';
import {
  SSHAuthenticationWrong,
  SSHHostUnreachableRefresh,
  VNCAuthentication,
} from '../interface/components/Loading/authentications';
import axios from 'axios';
import {htmlResponseToReason, isIOS} from './utils';

const setupDOM = (port, credentials) => {
  /* Creating a new RFB object and start a new connection */
  const url = `wss://${process.env.REACT_APP_DOMAIN_NAME ||
  '127.0.0.1'}:${port}`;
  const rfb = credentials ?
      new RFB(
          document.getElementById('screen'),
          url,
          {credentials: credentials}) :
      new RFB(
          document.getElementById('screen'),
          url)
  ;

  /* Set up the VNC default options */
  // Reference: https://github.com/novnc/noVNC/blob/master/docs/API.md

  // in case the session doesn't support auto resize
  rfb.scaleViewport = true;

  // resizeSession:
  // Is a boolean indicating if a request to resize the remote session should
  // be sent whenever the container changes dimensions. Disabled by default.
  rfb.resizeSession = true;

  return rfb;
};

const setupCredentialsHandlers = (vncViewer) => {
  vncViewer.rfb.addEventListener('securityfailure ', (ev) => {
    console.log(ev);
  });

  vncViewer.rfb.addEventListener('serververification', (_) => {
    // FIXME: this can be unsafe
    // Timeout needed to run this in the next loop
    //  or Promise resolving function in the noVNC library will not be set
    setTimeout(() => {
      vncViewer.rfb.approveServer();
    }, 0);
  });

  vncViewer.rfb.addEventListener('credentialsrequired', (ev) => {
    if (ev.detail.types.length === 1 && ev.detail.types.includes('password')) {
      // if only password is needed, use integrated UI to prompt for it
      const myVNCAuthentication = Object.assign(VNCAuthentication);
      myVNCAuthentication.label = 'Please enter your VNC password';
      myVNCAuthentication.description = 'iCtrl is unable to parse your VNC ' +
          'password. If you know the VNC password, please enter it below. ';
      myVNCAuthentication.enableSave = true;
      myVNCAuthentication.submitter = (authInput, save) => {
        const credentials = {};
        credentials['password'] = authInput;
        vncViewer.rfb.sendCredentials(credentials);
        if (save) {
          // TODO: to make this block to ensure successful savings
          saveVNCCredentials(vncViewer.session_id, credentials);
        }
      };
      vncViewer.setState({
        currentStep: ICtrlStep.VNC.PARSE_PASSWD,
        authentication: myVNCAuthentication,
      });
    } else {
      // too many authentication types needed, use dialog window
      vncViewer.setState({
        authTypes: ev.detail.types,
      });
    }

  });

  vncViewer.rfb.addEventListener('securityfailure', (ev) => {
    alert(`[Code ${ev.detail.status}]
${ev.detail.reason}
Or any saved credentials are no longer matching.
Click OK to reload`);
    window.location.search += '&load-credentials=false';
  });

};

const setupForwardBackwardKeys = (rfb) => {
  window.addEventListener('auxclick', (ev) => {
    if (ev.button === 3) {
      rfb.sendKey(KeyTable.XK_Alt_L, 'AltLeft', true);
      rfb.sendKey(KeyTable.XK_Left, 'ArrowLeft');
      rfb.sendKey(KeyTable.XK_Alt_L, 'AltLeft', false);
    } else if (ev.button === 4) {
      rfb.sendKey(KeyTable.XK_Alt_L, 'AltLeft', true);
      rfb.sendKey(KeyTable.XK_Right, 'ArrowRight');
      rfb.sendKey(KeyTable.XK_Alt_L, 'AltLeft', false);
    }
  });
};

const setupOnScreenKeyboard = (vncViewer) => {
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
      let key = newValue.charCodeAt(i);
      if (key === 10) {
        key = KeyTable.XK_Return;
      } else if (vncViewer.shiftKeyDown && (key >= 0x61) && (key <= 0x7a)) {
        key = key - 0x20;
      } else {
        key = keysyms.lookup(key);
      }
      vncViewer.rfb.sendKey(key);
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
};

const setupClipboard = (rfb) => {
  /* Setup bi-directional clipboard forwarding */
  // TODO: keep an eye on the official support discussed on
  // https://github.com/novnc/noVNC/pull/1562 remote -> local
  rfb.addEventListener('clipboard', (ev) => {
    try {
      navigator.clipboard.writeText(ev.detail.text).then();
    } catch (e) {
      // 3 cases of navigator.clipboard failure:
      // 1) not hosting over https on the server
      // 2) TODO: show a tutorial to approve clipboard permission if this is
      // the case the user didn't approve clipboard permission 3) the browser
      // is too old to support clipboard
      console.log(e);
    }
  });

  // local -> remote
  // whenever the window gets focus (the user just switched from another
  // tab/window),
  let clipboardText = null;
  window.onfocus = _ => {
    try {
      // compare the clipboard text with the previous one
      // if they differ, submit the local clipbboard text to the remote
      navigator.clipboard.readText().then((text) => {
        if (clipboardText !== text) {
          clipboardText = text;
          rfb.clipboardPasteFrom(text);
        }
      });
    } catch (e) {
      // see above: 3 cases of navigator.clipboard failure
      console.log(e);
    }
  };
};

export const vncConnect = async (vncViewer) => {
  const options = {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      sessionID: vncViewer.session_id,
      loadCheck: vncViewer.loadCheck,
      loadCredentials: vncViewer.loadCredentials,
    }),
  };
  if (!vncViewer.loadCredentials) {
    // remove once read
    window.history.replaceState(null, null, window.location.pathname);
  }

  const response = await fetch(`/api/vnc`, options);
  if (response.status !== 200) {
    console.log(response.body);
    return;
  }

  // the steps will be streamed as the server establishes the connection to the
  // target so we will need a ReadableStream Reader to get the current step,
  // and the final response which contains the port to be used and the VNC
  // password
  const reader = response.body.getReader();
  // this will store all the data read from the stream
  const data = [];
  const readStream = ({value, done}) => {
    // if the stream reading is done (end of stream),
    //  ignore all the step codes and parse the final response as JSON
    if (done) {
      const resultArr = new Uint8Array(
          data.slice(data.indexOf(ICtrlStep.VNC.DONE) + 1));
      const decodedStr = new TextDecoder().decode(resultArr);
      const {port, credentials} = JSON.parse(decodedStr);

      vncViewer.rfb = setupDOM(port, credentials);

      setupCredentialsHandlers(vncViewer);

      // when the VNC session is successfully established
      vncViewer.rfb.addEventListener('connect', () => {
        setupForwardBackwardKeys(vncViewer.rfb);
        setupOnScreenKeyboard(vncViewer);
        setupClipboard(vncViewer.rfb);

        // hide the Loading element
        vncViewer.setState({
          loading: false,
        });
      });

      vncViewer.rfb.addEventListener('disconnect', () => {
        vncViewer.setState({
          disconnected: true,
        });
      });

      return;
    } // if (done)

    // if the stream is not finished, push the values that was read into 'data'
    data.push(...value);

    // the stream is in this format:
    // STEP1 | STEP2 | ... | _DONE_ | FINAL_RESPONSE
    // from above we can see step 'DONE' serve as a divider of the step codes
    // and the final response

    // if the step 'DONE' is present in 'data'
    if (data.includes(ICtrlStep.VNC.DONE)) {
      // update the current step to 'DONE' and wait for the whole stream to be
      // transferred
      vncViewer.setState({
        currentStep: ICtrlStep.VNC.DONE,
      });
    } else {
      // if the step 'DONE' is not present in 'data',
      //  the last digit in the array must still be a step code
      //  rather than part of the final response
      const currentStep = value.slice(-1)[0];
      if (currentStep < 100) {
        // not an error
        vncViewer.setState({
          currentStep: currentStep,
        });
      } else {
        vncViewer.setState({
          currentStep: data.slice(-2)[0],
        });
        // handle the errors / server requests
        if (currentStep === ICtrlError.SSH.HOST_UNREACHABLE) {
          vncViewer.setState({
            authentication: SSHHostUnreachableRefresh,
          });
        } else if (currentStep === ICtrlError.SSH.AUTH_WRONG) {
          vncViewer.setState({
            authentication: SSHAuthenticationWrong,
          });
        } else if (currentStep === ICtrlError.VNC.PASSWD_MISSING) {
          // make a copy of the VNCAuthentication model
          const myVNCAuthentication = Object.assign(VNCAuthentication);
          myVNCAuthentication.submitter = (authInput) => {
            axios.post('/api/vncpasswd', {
              session_id: vncViewer.session_id,
              passwd: authInput,
            }).then(_ => {
              window.location.reload();
            }).catch(error => {
              console.log(error);
              if (error.response) {
                const reason = htmlResponseToReason(error.response.data, true);
                if (reason.includes('quota')) {
                  vncViewer.setState({
                    quotaExceeded: true,
                  });
                }
              }
            });
          };
          vncViewer.setState({
            authentication: myVNCAuthentication,
          });
        } else if (currentStep === ICtrlError.SSH.OVER_LOADED) {
          vncViewer.setState({
            isOverloaded: true,
          });
        } else if (currentStep === ICtrlError.VNC.QUOTA_EXCEEDED) {
          vncViewer.setState({
            quotaExceeded: true,
          });
        } else {
          console.log(`VNC error code: ${currentStep}`);
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

export const focusOnKeyboard = () => {
  if (isIOS()) {
    const canvas = document.getElementById(
        'screen').lastElementChild.firstElementChild;
    canvas.setAttribute('contenteditable', 'true');
    canvas.focus();
  } else {
    const textarea = document.getElementById('textarea');
    textarea.focus();
  }
};

export const resetVNC = (sessionID) => {
  axios.post('/api/vnc_reset', {
    session_id: sessionID,
  }).then((_) => {
    window.location.reload();
  }).catch(error => {
    // try to handle this gracefully as the error could be
    //  some .nfsxxx... files not being deleted correctly
    console.log(error);
    window.location.reload();
  });
};

export const saveVNCCredentials = (sessionID, credentials) => {
  axios.put('/api/vnc_credentials', {
    session_id: sessionID,
    credentials: credentials,
  }).catch((error) => {
    alert(error);
  });
};