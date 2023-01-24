/*
 * Copyright (c) 2023 iCtrl Developers
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

import React from 'react';
import {
  Button,
  Checkbox,
  Dialog,
  DialogActions,
  DialogContent,
  DialogContentText,
  DialogTitle,
  FormControlLabel,
  Slide,
  TextField,
} from '@mui/material';
import {saveVNCCredentials} from '../../../actions/vnc';

const VNC_AUTH_INPUT_PREFIX = 'vnc-auth-input-';

class VNCAuthenticationDialog extends React.Component {
  handleAuthSubmit = () => {
    const {types, vncViewer} = this.props;

    const saveCredentials = document.getElementById(
        `${VNC_AUTH_INPUT_PREFIX}save-credentials`).checked;

    let credentials = {};
    for (let t of types) {
      credentials[t] = document.getElementById(
          `${VNC_AUTH_INPUT_PREFIX}${t}`).value;
    }

    vncViewer.rfb.sendCredentials(credentials);
    if (saveCredentials) {
      saveVNCCredentials(vncViewer.session_id, credentials);
    }

    vncViewer.setState({
      authTypes: null,
    });
  };

  handleFieldKeyDown = (ev) => {
    if (ev.key === 'Enter') {
      ev.preventDefault();
      const {types} = this.props;
      let foundField = false;

      const field = ev.target.id.replace(VNC_AUTH_INPUT_PREFIX, '');
      for (let i = 0; i < types.length - 1; i++) {
        if (field === types[i]) {
          foundField = true;
          const nextElem = document.getElementById(
              `${VNC_AUTH_INPUT_PREFIX}${types[i + 1]}`);
          nextElem.focus();
          break;
        }
      }
      if (!foundField) {
        this.handleAuthSubmit();
      }
    }
  };

  render() {
    const {types} = this.props;

    return (<Dialog open={types !== null}
                    fullWidth={true}
                    maxWidth={'sm'}
                    TransitionComponent={Slide}
                    TransitionProps={{direction: 'up'}}>
      <DialogTitle>Please enter your VNC credentials</DialogTitle>
      <DialogContent>
        <DialogContentText>
          iCtrl is unable to parse your VNC credentials.
          Please enter them below.
        </DialogContentText>
        {types &&
            types.map(
                (t, idx) => (<TextField key={`${VNC_AUTH_INPUT_PREFIX}${t}`}
                                        id={`${VNC_AUTH_INPUT_PREFIX}${t}`}
                                        label={t.charAt(0).toUpperCase() +
                                            t.slice(1)}
                                        variant={'standard'}
                                        autoComplete={'new-password'}
                                        autoFocus={idx === 0}
                                        type={t === 'password' ?
                                            'password' :
                                            'text'}
                                        fullWidth={true}
                                        onKeyDown={this.handleFieldKeyDown}
                />))}
        <FormControlLabel
            control={<Checkbox id={`${VNC_AUTH_INPUT_PREFIX}save-credentials`}
                               defaultChecked
            />}
            label={'Save Credentials'}
        />
      </DialogContent>
      <DialogActions>
        <Button onClick={this.handleAuthSubmit}>OK</Button>
      </DialogActions>
    </Dialog>);
  }
}

export default VNCAuthenticationDialog;