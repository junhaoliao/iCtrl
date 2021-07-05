import {BrowserRouter as Router, Route, Switch} from 'react-router-dom';

import Home from './components/Home';
import FileManager from './components/FileManager';
import VNCViewer from './components/VNCViewer'
import React from 'react';


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
                    <Route path="/">
                        <Home/>
                    </Route>
                </Switch>
            </Router>
        );
    }

}
