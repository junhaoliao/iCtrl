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

import React from 'react';
import {
  Alert,
  AppBar,
  Checkbox,
  Collapse,
  FormControlLabel,
  InputAdornment,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Tab,
  Tabs,
  TextField,
  Typography,
} from '@mui/material';
import {LoadingButton} from '@mui/lab';
import {htmlResponseToReason} from '../../../actions/utils';
import axios from 'axios';
import {TransitionGroup} from 'react-transition-group';
import './index.css';
import {
  AccountBox,
  Check,
  Email,
  HighlightOff,
  Key,
} from '@mui/icons-material';

import {
  hasLowerCase,
  hasNumeral,
  hasSpecialSymbols,
  hasUpperCase,
  special_symbols,
} from './utils';
import LocalStorage from '../../../actions/LocalStorage';

const status = ['login', 'signup'];

export default class LogIn extends React.Component {
  constructor(props) {
    super(props);

    this.state = {
      currentTabIndex: 0,
      loading: false,
      errorElem: null,
      passwordErrorList: [],
      usernameValid: false,
      emailValid: false,
      passwordValid: false,
      confirmPasswordValid: false,
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
    }).then(_ => {
      this.setState({
        resendRequesting: false,
        errorElem: <Alert severity="info">
          Please check your email inbox or <a target="_blank" rel="noreferrer"
                                              href={'https://outlook.office.com/mail/junkemail'}>Junk
          Email</a> to activate your account.
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
    alert('Please contact support@ictrl.ca');
  };

  handleRecoverPassword = () => {
    // FIXME: implement this
    //  should send a link for password recovery
    alert('Please contact support@ictrl.ca');
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
      LocalStorage.setLastUsername(username);
      window.location = '/dashboard';
    }).catch(error => {
      this.setState({
        loading: false,
      });
      const resp = htmlResponseToReason(error.response.data, true);
      if (resp === 'ACCOUNT_WRONG_PASSWORD') {
        this.setState({
          errorElem: <Alert severity="error">
            Wrong password. <br/>
            Please try again or click <button
              onClick={this.handleRecoverPassword}>
            Forgot password
          </button> to reset it.
          </Alert>,
        });
      } else if (resp === 'ACCOUNT_WRONG_USERNAME') {
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
            Please check your email inbox or <a target="_blank" rel="noreferrer"
                                                href={'https://outlook.office.com/mail/junkemail'}>Junk
            Email</a>,
            or you may <button
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
          errorElem: <Alert severity="error">
            {resp}
          </Alert>,
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
    }).then(_ => {
      this.setState({
        loading: false,
        errorElem: <Alert severity="info">
          If your email address is valid, an activation link has been sent.
          Please check your email inbox or <a target="_blank" rel="noreferrer"
                                              href={'https://outlook.office.com/mail/junkemail'}>Junk
          Email</a>.
        </Alert>,
      });
    }).catch(error => {
      this.setState({loading: false});

      const resp = htmlResponseToReason(error.response.data, true);
      if (resp === 'ACCOUNT_DUPLICATE_USERNAME') {
        this.setState({
          errorElem: <Alert severity="warning">
            The entered username already exists. Do you want to <button
              onClick={() => {
                this.handleTabChange(null, 0);
              }}>login</button> instead?
          </Alert>,
        });
      } else if (resp === 'ACCOUNT_DUPLICATE_EMAIL') {
        this.setState({

          errorElem: <Alert severity="warning">
            The entered email already exists. Do you want to <button
              onClick={this.handleRecoverUsername}>
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

  handlePasswordInputChange = (ev) => {
    const password = ev.target.value;
    const passwordErrorList = [];

    const checks = [
      {
        pass: password.length >= 6,
        prompt: 'Password length should be at least 6 characters',
      },
      {
        pass: password.length <= 32,
        prompt: 'Password length should not exceed 32 characters',
      },
      {
        pass: hasNumeral(password),
        prompt: 'Password should have at least one numeral',
      },
      {
        pass: hasUpperCase(password),
        prompt: 'Password should have at least one uppercase letter',
      },
      {
        pass: hasLowerCase(password),
        prompt: 'Password should have at least one lowercase letter',
      },
      {
        pass: hasSpecialSymbols(password),
        prompt: `Password should have at least one of the symbols: ${special_symbols.join(
            '')}`,
      },
    ];
    checks.forEach(({pass, prompt}) => {
      if (!pass) {
        passwordErrorList.push(prompt);
      }
    });

    this.setState({
      passwordErrorList: passwordErrorList,
      passwordValid: ev.target.value.length > 0 && passwordErrorList.length ===
          0,
    });
  };

  handleConfirmPasswordInputChange = (ev) => {
    const password = document.getElementById('password').value;
    const confirmPassword = ev.target.value;
    let {passwordErrorList} = this.state;
    const prompt = `Passwords don't match`;

    if (password !== confirmPassword) {
      if (!passwordErrorList.includes(prompt)) {
        passwordErrorList = [...passwordErrorList, prompt];
      }
    } else {
      passwordErrorList = passwordErrorList.filter(e => e !== prompt);
    }
    this.setState({
      passwordErrorList: passwordErrorList,
      confirmPasswordValid: ev.target.value.length > 0 &&
          passwordErrorList.length === 0,
    });
  };

  handleFieldKeyDown = (ev) => {
    if (ev.key !== 'Enter') {
      return false;
    }

    const currentStatus = status[this.state.currentTabIndex];
    const isLogin = 'login' === currentStatus;

    const currentField = ev.target.id;
    if (currentField === 'username') {
      document.getElementById(isLogin ? 'password' : 'email').focus();
    } else if (currentField === 'email') {
      document.getElementById('password').focus();
    } else if (currentField === 'password') {
      if (isLogin) {
        document.getElementById('submit-button').click();
      } else { // sign up
        document.getElementById('confirm-password').focus();
      }
    } else if (currentField === 'confirm-password') {
      document.getElementById('submit-button').click();
    } else {
      console.error(currentField, 'should not be attached this handler');
    }
  };

  render() {
    const {
      currentTabIndex,
      loading,
      errorElem,
      passwordErrorList,
      usernameValid,
      emailValid,
      passwordValid,
      confirmPasswordValid,
    } = this.state;
    const currentStatus = status[currentTabIndex];
    const canSignUp = usernameValid && emailValid && passwordValid &&
        confirmPasswordValid;

    return (
        <>
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
                defaultValue={LocalStorage.getLastUsername()}
                autoComplete={'username'}
                onChange={(ev) => {
                  this.setState({usernameValid: ev.target.value.length > 0});
                }}
                onKeyDown={this.handleFieldKeyDown}
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
                onChange={(ev) => {
                  this.setState({emailValid: ev.target.value.length > 0});
                }}
                onKeyDown={this.handleFieldKeyDown}
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
                onChange={this.handlePasswordInputChange}
                onKeyDown={this.handleFieldKeyDown}
                autoComplete={currentStatus === 'login' ?
                    'current-password' :
                    'new-password'}
                InputProps={{
                  startAdornment: (
                      <InputAdornment position="start">
                        <Key/>
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
                onChange={this.handleConfirmPasswordInputChange}
                onKeyDown={this.handleFieldKeyDown}
                InputProps={{
                  startAdornment: (
                      <InputAdornment position="start">
                        <Check/>
                      </InputAdornment>
                  ),
                }}
            />
            </Collapse>}
            {currentStatus === 'signup' && <Collapse>
              <FormControlLabel
                  control={<Checkbox checked={true}/>}
                  label={<Typography variant={'body2'}>
                    By creating an account, you agree to iCtrl's&nbsp;
                    <a href={'https://github.com/junhaoliao/iCtrl/blob/main/LICENSE.md'}
                       rel={'noreferrer'} target={'_blank'}>
                      Terms and Conditions
                    </a>
                  </Typography>}
              />
            </Collapse>}
            {currentStatus === 'signup' && passwordErrorList.length > 0 &&
                <Collapse>
                  <Alert icon={false} severity="warning">
                    <List>
                      <TransitionGroup>
                        {passwordErrorList.map((item, _) => (
                            <Collapse key={item}>
                              <ListItem>
                                <ListItemIcon>
                                  <HighlightOff
                                      style={{color: 'rgb(102, 60, 0)'}}/>
                                </ListItemIcon>
                                <ListItemText
                                    primary={<div style={{
                                      fontWeight: 600,
                                      fontSize: 14,
                                    }}>{item}</div>}/>
                              </ListItem>
                            </Collapse>
                        ))}
                      </TransitionGroup>
                    </List>
                  </Alert>
                </Collapse>
            }
            {errorElem && <Collapse>
              {errorElem}
            </Collapse>
            }
            <LoadingButton
                id={'submit-button'}
                variant={'contained'}
                loading={loading}
                loadingIndicator={'Logging in...'}
                onClick={currentStatus === 'login' ?
                    this.handleLogIn :
                    this.handleSignUp}
                fullWidth
                color={'info'}
                size={'large'}
                disabled={currentStatus === 'login' ? false : !canSignUp}
            >
              {currentStatus === 'login' ? 'Log In' : 'Sign up'}
            </LoadingButton>
          </TransitionGroup>
          {/*<AdComponent*/}
          {/*    data-ad-client={'ca-pub-9503782531617816'}*/}
          {/*    data-ad-slot={'6122871243'}*/}
          {/*/>*/}

        </>
    );
  }
}