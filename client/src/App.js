import React from 'react';

import {BrowserRouter as Router, Route, Switch} from 'react-router-dom';

import FileManager from './interface/pages/FileManager';
import VNCViewer from './interface/pages/VNCViewer';
import Term from './interface/pages/Term';
import Dashboard from './interface/pages/Dashboard';
import Home from './interface/pages/Home';


export default class App extends React.Component {
    render() {
        return (
            <Router>
                <Switch>
                    <Route path="/fm/:session_id" component={FileManager}/>
                    <Route path="/vnc/:session_id" component={VNCViewer}/>
                    <Route path="/terminal/:session_id" component={Term}/>
                    <Route exact path="/dashboard" component={Dashboard}/>
                    <Route exact path={'/'} component={Home}/>
                    <Route path={'/*'}>
                        <div>404</div>
                    </Route>
                </Switch>
            </Router>
        );
    }
}
