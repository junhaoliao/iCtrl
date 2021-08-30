import React from 'react';
import {
    AppBar,
    Tabs,
    Tab,
    Box,
    Typography,
    TextField
} from '@material-ui/core';
import SwipeableViews from 'react-swipeable-views';
import { LoadingButton } from '@material-ui/lab';

import './index.css';

export default class LogIn extends React.Component {
    constructor(props) {
        super(props);

        this.state = {
            value: 0,
            index: 0,
            loading: false,
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
    }

    handleChange = (event, newValue) => {
        // console.log(newValue)
        this.setState({ value: newValue })
    };

    a11yProps = (index) => {
        return {
            id: `full-width-tab-${index}`,
            'aria-controls': `full-width-tabpanel-${index}`,
        };
    };

    handleLogInTab = () => {
        // Click on LogIn tab
    }

    handleSignUpTab = () => {
        // Click on SignUp tab
    }

    handleButtonClick = (ev) => {
        if (ev.target && ev.target.id === 'button-log-in') {
            // Click on LogIn button
        } else if (ev.target && ev.target.id === 'button-sign-up') {
            // Click on SignUp button 
        }
    }

    render() {
        const { value, loading } = this.state;

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
                        <Tab label="Log In" {...this.a11yProps(0)} onClick={() => this.handleLogInTab()} />
                        <Tab label="Sign Up" {...this.a11yProps(1)} onClick={() => this.handleSignUpTab()} />
                    </Tabs>
                </AppBar>
                <SwipeableViews
                    axis='x-reverse'
                    index={value}
                    style={{ height: '80%', alignContent: 'center' }}
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
                                            label="UserName/Email"
                                            defaultValue=""
                                            variant="outlined"
                                            style={{ width: '100%' }}
                                        />
                                    </div>
                                    <div className="input-wrapper">
                                        <TextField
                                            required
                                            id="log-in-password"
                                            label="PassWord"
                                            defaultValue=""
                                            variant="outlined"
                                            style={{ width: '100%' }}
                                        />
                                    </div>
                                    <LoadingButton variant={'contained'}
                                        id={'button-save'}
                                        loading={loading}
                                        loadingIndicator={'Saving...'}
                                        onClick={this.handleButtonClick}
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
                                            label="UserName"
                                            defaultValue=""
                                            variant="outlined"
                                            style={{ width: '100%' }}
                                        />
                                    </div>
                                    <div className="input-wrapper">
                                        <TextField
                                            required
                                            id="sign-up-email"
                                            label="Email"
                                            defaultValue=""
                                            variant="outlined"
                                            style={{ width: '100%' }}
                                        />
                                    </div>
                                    <div className="input-wrapper">
                                        <TextField
                                            required
                                            id="sign-up-password"
                                            label="PassWord"
                                            defaultValue=""
                                            variant="outlined"
                                            style={{ width: '100%' }}
                                        />
                                    </div>
                                    <LoadingButton variant={'contained'}
                                        id={'button-save'}
                                        loading={loading}
                                        loadingIndicator={'Saving...'}
                                        onClick={this.handleButtonClick}
                                        className="submit-button">
                                        Sign Up
                                    </LoadingButton>
                                </div>
                            </Box>
                        )}
                    </div>
                </SwipeableViews>
            </div>
        )
    }
}