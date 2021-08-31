import React from 'react';
import {AppBar, Box, Tab, Tabs, TextField,} from '@material-ui/core';
import SwipeableViews from 'react-swipeable-views';
import {LoadingButton} from '@material-ui/lab';
import {htmlResponseToReason} from '../../../actions/utils';
import axios from 'axios';

import './index.css';

export default class LogIn extends React.Component {
    constructor(props) {
        super(props);

        this.state = {
            value: 0,
            index: 0,
            loading: false,
            username: '',
            email: '',
            password: '',
            logInTab: true,
        };
    }

    handleTabClick = (tab) => {
        switch (tab) {
            case 'logIn':
                console.log('logIn');
                document.getElementById('signUp').classList.remove('Mui-selected');
                document.getElementById('logIn').classList.add('Mui-selected');
                break;
            case 'signUp':
                document.getElementById('logIn').classList.remove('Mui-selected');
                document.getElementById('signUp').classList.add('Mui-selected');

                console.log('signUp', document.getElementsByClassName('MuiTabs-indicat'));
                break;
            default:
                console.log('nothing');
                break;
        }
    };

    handleChange = (event, newValue) => {
        // console.log(newValue)
        this.setState({value: newValue});
    };

    a11yProps = (index) => {
        return {
            id: `full-width-tab-${index}`,
            'aria-controls': `full-width-tabpanel-${index}`,
        };
    };

    handleLogInTab = () => {
        // Click on LogIn tab
        // If clicking the tab when currently on it, cannot get the value of sign in box
        const {logInTab} = this.state;
        if (logInTab === false) {
            const username = document.getElementById('sign-up-user').value;
            username !== this.state.username && this.setState({username});

            const email = document.getElementById('sign-up-email').value;
            email !== this.state.email && this.setState({email});

            const password = document.getElementById('sign-up-password').value;
            password !== this.state.password && this.setState({password});

            this.setState({logInTab: true});
        }

    };

    handleSignUpTab = () => {
        // Click on SignUp tab
        const {logInTab} = this.state;
        if (logInTab === true) {
            const username = document.getElementById('log-in-user').value;
            username !== this.state.username && this.setState({username});

            const password = document.getElementById('log-in-password').value;
            password !== this.state.password && this.setState({password});

            this.setState({logInTab: false});
        }

    };

    handleButtonClick = (ev) => {
        if (ev.target && ev.target.id === 'button-log-in') {
            // Click on LogIn button
            const username = document.getElementById('log-in-user').value || '';
            const password = document.getElementById('log-in-password').value || '';
            console.log(username, password);
            axios.post('/api/login', {
                username, password
            }).then(response => {
                window.location = '/dashboard';
            })
                .catch(error => {
                    this.setState({
                        error: htmlResponseToReason(error.response.data),
                        loading: false,
                    });
                });
        } else if (ev.target && ev.target.id === 'button-sign-up') {
            // Click on SignUp button
            const username = document.getElementById('sign-up-user').value || '';
            const email = document.getElementById('sign-up-email').value || '';
            const password = document.getElementById('sign-up-password').value || '';
            console.log(username, email, password);
            axios.post('/api/register', {
                username, password, email
            }).then(response => {
                window.location = '/';
            }).catch(error => {
                this.setState({
                    error: htmlResponseToReason(error.response.data),
                    loading: false,
                });
            });
        }
    };

    render() {
        const {value, loading, username, email, password} = this.state;

        return (
            <div className="log-in-wrapper">
                <AppBar position="static" color="default">
                    <Tabs
                        value={value}
                        onChange={this.handleChange}
                        indicatorColor="primary"
                        textColor="primary"
                        variant="fullWidth"
                        aria-label="full width tabs example"
                    >
                        <Tab label="Log In" {...this.a11yProps(0)} onClick={() => this.handleLogInTab()}/>
                        <Tab label="Sign Up" {...this.a11yProps(1)} onClick={() => this.handleSignUpTab()}/>
                    </Tabs>
                </AppBar>
                <SwipeableViews
                    axis="x-reverse"
                    index={value}
                >
                    <div
                        role="tabpanel"
                        hidden={value !== 0}
                        id={`full-width-tabpanel-0`}
                        aria-labelledby={`full-width-tab-0`}
                    >
                        {value === 0 && (
                            <Box p={2}>
                                <div className="log-in-box">
                                    <div className="input-wrapper">
                                        <TextField
                                            required
                                            id="log-in-user"
                                            label="Username / Email"
                                            defaultValue={username || ''}
                                            variant="outlined"
                                            fullWidth={true}

                                        />
                                    </div>
                                    <div className="input-wrapper">
                                        <TextField
                                            required
                                            id="log-in-password"
                                            label="Password"
                                            defaultValue={password || ''}
                                            variant="outlined"
                                            type="password"
                                            fullWidth={true}
                                        />
                                    </div>
                                    <LoadingButton variant={'contained'}
                                                   id={'button-log-in'}
                                                   loading={loading}
                                                   loadingIndicator={'Saving...'}
                                                   onClick={(e) => this.handleButtonClick(e)}
                                                   className="submit-button">
                                        Log In
                                    </LoadingButton>
                                </div>
                            </Box>
                        )}
                    </div>
                    <div
                        role="tabpanel"
                        hidden={value !== 1}
                        id={`full-width-tabpanel-1`}
                        aria-labelledby={`full-width-tab-1`}
                    >
                        {value === 1 && (
                            <Box p={2}>
                                <div className="sign-up-box">
                                    <div className="input-wrapper">
                                        <TextField
                                            required
                                            id="sign-up-user"
                                            label="Username"
                                            defaultValue={username || ''}
                                            variant="outlined"
                                            fullWidth={true}
                                        />
                                    </div>
                                    <div className="input-wrapper">
                                        <TextField
                                            required
                                            id="sign-up-email"
                                            label="Email"
                                            defaultValue={email || ''}
                                            variant="outlined"
                                            fullWidth={true}
                                        />
                                    </div>
                                    <div className="input-wrapper">
                                        <TextField
                                            required
                                            id="sign-up-password"
                                            label="Password"
                                            defaultValue={password || ''}
                                            variant="outlined"
                                            type="password"
                                            fullWidth={true}
                                        />
                                    </div>
                                    <LoadingButton variant={'contained'}
                                                   id={'button-sign-up'}
                                                   loading={loading}
                                                   loadingIndicator={'Saving...'}
                                                   onClick={(e) => this.handleButtonClick(e)}
                                                   className="submit-button">
                                        Sign Up
                                    </LoadingButton>
                                </div>
                            </Box>
                        )}
                    </div>
                </SwipeableViews>
            </div>
        );
    }
}