import React, {Children} from 'react';
import {AppBar, Box, Tab, Tabs, TextField, Typography,} from '@material-ui/core';
import SwipeableViews from 'react-swipeable-views';
import {LoadingButton} from '@material-ui/lab';
import {htmlResponseToReason} from '../../../actions/utils';
import axios from 'axios';

import './index.css';

const TabPanel = (props) => {
    const {children, currentIndex, index} = props;

    return (
        <div
            role="tabpanel"
            hidden={currentIndex !== index}
            id={`tabpanel-${index}`}
        >
            {currentIndex === index && (
                <Box sx={{p: 5}}>
                    {React.Children.map(children, child => (
                        React.cloneElement(child, {style: {...child.props.style, marginBottom: '45px'}})
                    ))}
                </Box>
            )}
        </div>
    );
}

export default class LogIn extends React.Component {
    constructor(props) {
        super(props);

        this.state = {
            curIdx: 0,
            loading: false
        };
    }

    handleTabChange = (_, newValue) => {
        this.setState({curIdx: newValue});
    };

    handleChangeIndex = (newValue) => {
        this.setState({curIdx: newValue});
    };

    handleLogIn = () => {
        this.setState({loading: true})

        const username = document.getElementById('log-in-username').value;
        const password = document.getElementById('log-in-password').value;
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
    };

    handleSignUp = () => {
        this.setState({loading: true})
        const username = document.getElementById('sign-up-username').value;
        const email = document.getElementById('sign-up-email').value;
        const password = document.getElementById('sign-up-password').value;

        axios.post('/api/register', {
            username, password, email
        }).then(response => {
            // FIXME: add sign up status
            window.location = '/';
        }).catch(error => {
            this.setState({
                error: htmlResponseToReason(error.response.data),
                loading: false,
            });
        });
    }

    render() {
        const {curIdx, loading} = this.state;

        return (
            <div>
                <AppBar position="static" color="">
                    <Tabs
                        value={curIdx}
                        onChange={this.handleTabChange}
                        indicatorColor="primary"
                        textColor="primary"
                        variant="fullWidth"
                        aria-label="full width tabs"
                    >
                        <Tab label="Log In" id={'login-tab'}/>
                        <Tab label="Sign Up" id={'signup-tab'}/>
                    </Tabs>
                </AppBar>
                <SwipeableViews
                    axis="x"
                    index={curIdx}
                    onChangeIndex={this.handleChangeIndex}
                >
                    <TabPanel currentIndex={curIdx} index={0}>
                        <TextField
                            required
                            id="log-in-username"
                            label="Username / Email"
                            variant="filled"
                            autoComplete={'username'}
                            fullWidth={true}
                        />
                        <TextField
                            required
                            id="log-in-password"
                            label="Password"
                            variant="filled"
                            type="password"
                            autoComplete={'current-password'}
                            fullWidth={true}
                        />
                        <LoadingButton variant={'contained'}
                                       loading={loading}
                                       loadingIndicator={'Logging in...'}
                                       onClick={this.handleLogIn}
                                       fullWidth
                                       color={'info'}
                                       size={'large'}
                        >
                            Log In
                        </LoadingButton>
                    </TabPanel>
                    <TabPanel currentIndex={curIdx} index={1}>
                        <TextField
                            required
                            id="sign-up-username"
                            label="Username"
                            variant="filled"
                            autoComplete={'new-password'}
                            fullWidth={true}
                        />
                        <TextField
                            required
                            id="sign-up-email"
                            label="Email"
                            variant="filled"
                            type={'email'}
                            autoComplete={'email'}
                            fullWidth={true}
                        />
                        <TextField
                            required
                            id="sign-up-password"
                            label="Password"
                            variant="filled"
                            type="password"
                            autoComplete={'new-password'}
                            fullWidth={true}
                        />
                        <LoadingButton variant={'contained'}
                                       loading={loading}
                                       loadingIndicator={'Signing up...'}
                                       onClick={this.handleSignUp}
                                       fullWidth
                                       color={'info'}
                                       size={'large'}
                        >
                            Sign Up
                        </LoadingButton>
                    </TabPanel>
                </SwipeableViews>
            </div>
        );
    }
}