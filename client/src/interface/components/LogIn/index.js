import React from 'react';
import {AppBar, Collapse, InputAdornment, Tab, Tabs, TextField} from '@material-ui/core';
import {Alert, LoadingButton} from '@material-ui/lab';
import {htmlResponseToReason} from '../../../actions/utils';
import axios from 'axios';
import {TransitionGroup} from 'react-transition-group';

import './index.css';
import {AccountBox, Check, Email, Password} from '@material-ui/icons';

const status = ['login', 'signup'];

export default class LogIn extends React.Component {
  constructor(props) {
    super(props);

    this.state = {
      currentTabIndex: 0,
      loading: false,
      errorElem: null,
    };
  }

  handleTabChange = (_, newValue) => {
    this.setState({currentTabIndex: newValue, errorElem: null});
  };

  handleResendActivation = () => {
    const resendButton = document.getElementById('resend-button');
    resendButton.setAttribute('disabled', 'true');

    const username = document.getElementById('username').value;

    axios.post('/api/resend_activation', {
      username: username,
    }).then(response => {
      this.setState({
        resendRequesting: false,
        errorElem: <Alert severity="info">
          Please check your email inbox to activate your account.
        </Alert>,
      });
    }).catch(error => {
      this.setState({
        resendRequesting: false, errorElem: <Alert severity="error">
          {htmlResponseToReason(error.response.data, true)}
        </Alert>,
      });
    });
  };

  handleRecoverUsername = () => {
    // FIXME: implement this
    //  should send an email to inform the user of her/his username
    alert('not implemented');
  };

  handleLogIn = () => {
    this.setState({
      loading: true,
      errorElem: null,
    });

    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;

    axios.post('/api/login', {
      username, password,
    }).then(_ => {
      window.location = '/dashboard';
    }).catch(error => {
      this.setState({
        loading: false,
      });
      const resp = htmlResponseToReason(error.response.data, true);
      if (resp === 'ACCOUNT_WRONG_USERNAME') {
        this.setState({
          errorElem: <Alert severity="error">
            Sorry we can't find your account. <br/>
            Please check your username or <button onClick={() => {
            this.handleTabChange(null, 1);
          }}>
            register
          </button> a new account.
          </Alert>,
        });
      } else if (resp === 'ACCOUNT_NOT_ACTIVATED') {
        this.setState({
          errorElem: <Alert severity="warning">
            Your account has not been activated yet.<br/>
            Please check your email inbox or <button
              id={'resend-button'}
              onClick={this.handleResendActivation}
          >
            resend
          </button> the
            activation email.
          </Alert>,
        });
      } else {
        this.setState({
          errorElem: resp,
        });
      }
    });
  };

  handleSignUp = () => {
    this.setState({loading: true, errorElem: null});

    const username = document.getElementById('username').value;
    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;
    const confirmPassword = document.getElementById('confirm-password').value;

    if (password !== confirmPassword) {
      this.setState({
        loading: false,
        errorElem: <Alert severity="error">
          "Password" and "Confirm Password" don't match.
        </Alert>,
      });
      return;
    }

    axios.post('/api/register', {
      username, password, email,
    }).then(response => {
      this.setState({
        loading: false,
        errorElem: <Alert severity="info">
          If your email address is valid, an activation link has been sent. Please check your email inbox or junk box.
        </Alert>,
      });
    }).catch(error => {
      this.setState({loading: false});

      const resp = htmlResponseToReason(error.response.data, true);
      if (resp === 'ACCOUNT_DUPLICATE_USERNAME') {
        this.setState({
          errorElem: <Alert severity="warning">
            The entered username already exists. Do you want to <button onClick={() => {
            this.handleTabChange(null, 0);
          }}>login</button> instead?
          </Alert>,
        });
      } else if (resp === 'ACCOUNT_DUPLICATE_EMAIL') {
        this.setState({

          errorElem: <Alert severity="warning">
            The entered email already exists. Do you want to <button onClick={this.handleRecoverUsername}>
            recover
          </button> your username?
          </Alert>,
        });
      } else {
        this.setState({

          errorElem: <Alert severity="error">
            {resp}
          </Alert>,
        });
      }
    });
  };

  render() {
    const {currentTabIndex, loading, errorElem} = this.state;
    const currentStatus = status[currentTabIndex];

    return (
        <div>
          <AppBar position="static" color="">
            <Tabs
                value={currentTabIndex}
                onChange={this.handleTabChange}
                indicatorColor="primary"
                textColor="primary"
                variant="fullWidth"
                aria-label="full width login signup tabs"
            >
              <Tab label="Log In"/>
              <Tab label="Sign Up"/>
            </Tabs>
          </AppBar>
          <TransitionGroup id={'login-container'}>
            <TextField
                required={true}
                fullWidth={true}
                variant={'standard'}
                id={'username'}
                label={'Username'}
                autoComplete={'username'}
                InputProps={{
                  startAdornment: (
                      <InputAdornment position="start">
                        <AccountBox/>
                      </InputAdornment>
                  ),
                }}
            />
            {currentStatus === 'signup' && <Collapse><TextField
                required={true}
                fullWidth={true}
                variant={'standard'}
                id="email"
                label="Email"
                autoComplete={'email'}
                InputProps={{
                  startAdornment: (
                      <InputAdornment position="start">
                        <Email/>
                      </InputAdornment>
                  ),
                }}
            /></Collapse>}
            <TextField
                required={true}
                fullWidth={true}
                variant={'standard'}
                id={'password'}
                label={'Password'}
                type={'password'}
                autoComplete={currentStatus === 'login' ? 'current-password' : 'new-password'}
                InputProps={{
                  startAdornment: (
                      <InputAdornment position="start">
                        <Password/>
                      </InputAdornment>
                  ),
                }}
            />
            {currentStatus === 'signup' && <Collapse><TextField
                required={true}
                fullWidth={true}
                variant={'standard'}
                id="confirm-password"
                label="Confirm Password"
                type={'password'}
                autoComplete={'new-password'}
                InputProps={{
                  startAdornment: (
                      <InputAdornment position="start">
                        <Check/>
                      </InputAdornment>
                  ),
                }}
            /></Collapse>}
            {errorElem && <Collapse>{errorElem}
            </Collapse>}
            {
              currentStatus === 'login' ? <LoadingButton
                  variant={'contained'}
                  loading={loading}
                  loadingIndicator={'Logging in...'}
                  onClick={this.handleLogIn}
                  fullWidth
                  color={'info'}
                  size={'large'}
              >
                Log In
              </LoadingButton> : <LoadingButton
                  variant={'contained'}
                  loading={loading}
                  loadingIndicator={'Signing up...'}
                  onClick={this.handleSignUp}
                  fullWidth
                  color={'info'}
                  size={'large'}
              >
                Sign Up
              </LoadingButton>
            }
          </TransitionGroup>
        </div>
    );
  }
}