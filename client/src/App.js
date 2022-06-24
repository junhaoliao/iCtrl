/*
 * Copyright (c) 2021-2022 iCtrl Developers
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

import {BrowserRouter as Router, Route, Switch} from 'react-router-dom';

import FileManager from './interface/pages/FileManager';
import VNCViewer from './interface/pages/VNCViewer';
import Term from './interface/pages/Term';
import Dashboard from './interface/pages/Dashboard';
import Home from './interface/pages/Home';
import ReactDOM from 'react-dom';

export default class App extends React.Component {
  componentDidMount() {
    if (window.location.protocol === 'file:'){
    ReactDOM.render(
        <React.StrictMode>
          <Dashboard/>
        </React.StrictMode>,
        document.getElementById('root'));
    }
  }

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
