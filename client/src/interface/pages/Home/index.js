import React from 'react';

import {Input} from '@material-ui/core';
import axios from 'axios';

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
            <div>
                <h1>I'm the Home Page</h1>
                <h1>Counter: </h1>
                <Input value={this.state.counter}/>
                <div style={{height: 100}}/>
                <h1>I'm also the Login Page</h1>
                <h1>I'm also the Signup Page</h1>
            </div>
        );
    }
}


