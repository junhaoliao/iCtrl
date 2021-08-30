import React from 'react';

import {
    // Input,
    AppBar,
    Toolbar,
    Typography,
    Button
} from '@material-ui/core';
import axios from 'axios';
import ictrlLogo from '../../../icons/logo.png';
import LogIn from '../../components/LogIn';

import './index.css';

export default class Home extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            counter: 1,
        };
    }

    componentDidMount() {
        axios.get('/api/userid')
            .then(response => {
                window.location = '/dashboard';
            })
            .catch(_ => {
                // do nothing for now
            });

        // TODO: remove this
        setInterval(() => {
            this.setState({
                counter: this.state.counter + 1,
            });
        }, 100);
    }

    render() {
        return (
            <div className="home-page-background">
                <AppBar position="static">
                    <Toolbar>
                        <img src={ictrlLogo} style={{height: 30, width: 30, marginRight: 10}} alt="" />
                        <Typography style={{flex: 1}} variant="h6">
                            iCtrl
                        </Typography>
                        <Button color="inherit">Team</Button>
                    </Toolbar>
                </AppBar>
                {/* <h1>I'm the Home Page</h1>
                <h1>Counter: </h1>
                <Input value={this.state.counter}/>
                <div style={{height: 100}}/>
                <h1>I'm also the Login Page</h1>
                <h1>I'm also the Signup Page</h1> */}
                <div className="home-page-main-wrapper">
                    <div style={{ flex: 2, height: '80%' }}>
                        <img src={ictrlLogo} className="ictrl-logo" alt="" />
                    </div>
                    <div className="split" />
                    <LogIn />
                </div>
            </div>
        );
    }
}


