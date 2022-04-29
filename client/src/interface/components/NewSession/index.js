/*
 * Copyright (c) 2021-2022 iCtrl Developers
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
import Button from '@mui/material/Button';
import TextField from '@mui/material/TextField';
import {
  Alert,
  Autocomplete,
  Box,
  Dialog,
  DialogActions,
  DialogTitle,
  Popper,
  Tooltip,
  Typography,
} from '@mui/material';
import axios from 'axios';

import './index.css';
import {hostAddressList} from '../../../actions/session';
import {LoadingButton} from '@mui/lab';
import {htmlResponseToReason, openInNewWindow} from '../../../actions/utils';

export default class NewSession extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      error: null,
      loading: false,
      hostValue: '',
      passwordPrompt: null,
    };
  }

  handleSubmit() {
    const host = document.getElementById('host').value;
    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;

    if (host.length === 0) {
      this.setState({
        error: `The 'Host' field cannot be empty`,
      });
      return;
    } else if (username.length === 0) {
      this.setState({
        error: `The 'Username' field cannot be empty`,
      });
      return;
    }

    this.setState({
      error: null,
      loading: true,
    });

    axios.post('/api/session', {
      host, username, password,
    }).then(_ => {
      window.location.reload();
    }).catch(error => {
      this.setState({
        error: htmlResponseToReason(error.response.data),
        loading: false,
      });
    });
  }

  handleClose = (ev) => {
    if (ev.target && ev.target.id === 'button-save') {
      this.handleSubmit();
    } else {
      this.setState({
        error: null,
      });
      this.props.onAddNewSessionClose();
    }
  };

  handleForgotPassword = (_) => {
    const {hostValue} = this.state;

    if (hostValue.includes('eecg')) {
      this.setState({
        passwordPrompt: <div>
          <p>By default, your EECG password is your student number.</p>
          <p>To recover your password, please email the EECG Workstations
            Manager</p>
          <p>Tim Trant: tim@eecg.utoronto.ca</p>
          <p><a
              href={'mailto:tim@eecg.utoronto.ca?subject=EECG%20UG%20Password%20Reset&body=Hi%20Tim%2C%0D%0A%0D%0AI%20am%20writing%20this%20to%20request%20a%20password%20reset%20for%20my%20EECG%20UG%20account.%0D%0A%0D%0AMy%20student%20number%20is%20%3CSTUDENT_NUMBER%3E%20.%20Please%20let%20me%20know%20if%20you%20need%20any%20further%20information.%0D%0A%0D%0ARegards%2C%0D%0A%0D%0A%3CYOUR_NAME%3E'}>Email
            Example
          </a></p>
        </div>,
      });
    } else if (hostValue.includes('ecf')) {
      openInNewWindow('https://ssl.ecf.utoronto.ca/ecf/services/forgotpass');
    }
  };

  shiftFocus = (ev) => {
    // only shift the focus if the 'Enter'/'Return' key is pressed
    if (ev.key !== 'Enter') {
      return;
    }

    const id = ev.target.id;

    // all fields are required except 'password'
    if (id === 'password' && ev.target.value.length === 0) {
      return;
    }

    let nextField = null;

    if (id === 'host') {
      nextField = document.getElementById('username');
    } else if (id === 'username') {
      nextField = document.getElementById('password');
    } else if (id === 'password') {
      nextField = document.getElementById('button-save');
    } else {
      // should never reach here,
      //  or this callback is used in a wrong place
      throw Error('wrong branch');
    }

    nextField.focus();
  };

  render() {
    const {open} = this.props;
    const {error, loading, hostValue, passwordPrompt} = this.state;

    const showForgotPassword = hostValue.includes('ecf') ||
        hostValue.includes('eecg');

    return (
        <Dialog
            open={open}
            fullWidth={true}
            maxWidth={'xs'}
            aria-labelledby="new session"
        >
          <DialogTitle>Create New Session</DialogTitle>

          <div className={'new-session-content-wrapper'}>
            <Box display={'flex'}>
              <Tooltip style={{width: '150px'}}
                       title={'[Required] host name of the target SSH server'}>
                <Typography variant={'subtitle1'}>
                  Host<span style={{color: 'red'}}>*</span>
                </Typography>
              </Tooltip>
              <Autocomplete
                  id={'host'}
                  options={hostAddressList}
                  clearOnBlur={false}
                  freeSolo={true}
                  size={'small'}
                  autoComplete={true}
                  openOnFocus={true}
                  value={hostValue}
                  fullWidth={true}
                  onInputChange={(_, newValue) => {
                    this.setState({
                      hostValue: newValue,
                      passwordPrompt: null,
                    });
                  }}
                  renderInput={(params) => (
                      <TextField
                          {...params}
                          autoFocus
                          size={'small'}
                          placeholder={'example.com'}
                          variant={'standard'}
                      />
                  )}
                  PopperComponent={(props) => <Popper {...props}
                                                      placement={'top-end'}
                                                      style={{width: '200px'}}/>}
                  ListboxProps={{
                    style: {
                      maxHeight: '200px',
                      marginLeft: '-8px',
                    },
                  }}
                  onKeyDown={this.shiftFocus}
              />
            </Box>
            <Box display={'flex'}>
              <Tooltip style={{width: '150px'}}
                       title={'[Required] username for login'}>
                <Typography variant={'subtitle1'}>
                  Username<span style={{color: 'red'}}>*</span>
                </Typography>
              </Tooltip>
              <TextField id={'username'}
                         autoComplete={'new-password'}
                         fullWidth={true}
                         size={'small'}
                         placeholder={'username'}
                         variant={'standard'}
                         onKeyDown={this.shiftFocus}
              />
            </Box>
            <Box display={'flex'}>
              <Tooltip style={{width: '150px'}}
                       title={'[Optional] password for login. ' +
                           'If left empty, you will need to enter the password at the next login. '}>
                <Typography variant={'subtitle1'}>
                  Password
                </Typography>
              </Tooltip>
              <TextField id={'password'}
                         type={'password'}
                         autoComplete={'new-password'}
                         fullWidth={true}
                         size={'small'}
                         placeholder={'****'}
                         variant={'standard'}
                         onKeyDown={this.shiftFocus}
              />
            </Box>
            {Boolean(error) && <Alert severity="error">{error}</Alert>}

            {passwordPrompt && <Alert severity="info">{passwordPrompt}</Alert>}
          </div>
          <DialogActions>
            {showForgotPassword &&
                <Button onClick={this.handleForgotPassword}>
                  Forgot Password?
                </Button>
            }
            <Button variant={'outlined'} disabled={loading}
                    onClick={this.handleClose}>Close</Button>
            <LoadingButton variant={'contained'}
                           id={'button-save'}
                           loading={loading}
                           loadingIndicator={'Saving...'}
                           onClick={this.handleClose}>
              Save
            </LoadingButton>
          </DialogActions>
        </Dialog>
    );
  }
}