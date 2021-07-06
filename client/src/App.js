import React from 'react';

import {BrowserRouter as Router, Route, Switch} from 'react-router-dom';

import Home from './interface/pages/Home';
import FileManager from './interface/pages/FileManager';
import VNCViewer from './interface/pages/VNCViewer';
import Term from './interface/pages/Term';


export default class App extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            profiles: {}
        };
    }

    componentDidMount() {
        if (Object.keys(this.state.profiles).length === 0) {
            fetch('/profiles')
                .then(res => res.json())
                .then(result => {
                    console.log('fetch');
                    this.setState({
                        profiles: result
                    });
                });
        }
    }

    render() {
        if (Object.keys(this.state.profiles).length === 0) {
            return null;
        }

        return (
            <Router>
                <Switch>
                    <Route path="/fm/:session_id" render={(props) => (
                        <FileManager {...props} profiles={this.state.profiles}/>
                    )}/>
                    <Route path="/vnc/:session_id" render={(props) => (
                        <VNCViewer {...props} profiles={this.state.profiles}/>
                    )}/>
                    <Route path="/terminal/:session_id" render={(props) => (
                        <Term {...props} profiles={this.state.profiles}/>
                    )}/>
                    <Route path="/">
                        <Home/>
                    </Route>
                </Switch>
            </Router>
        );
    }

}
