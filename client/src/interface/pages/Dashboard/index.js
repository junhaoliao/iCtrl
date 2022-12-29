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

import './index.css';

import {
  AppBar,
  IconButton,
  List,
  Skeleton,
  Toolbar,
  Tooltip,
  Typography,
} from '@mui/material';
import AddBoxIcon from '@mui/icons-material/AddBox';
import InfoIcon from '@mui/icons-material/Info';
import ChangeMachine from '../../components/ChangeMachine';
import LogoutIcon from '@mui/icons-material/Logout';
import NewSession from '../../components/NewSession';
import axios from 'axios';

import logo from '../../../icons/logo.webp';
import ictrlLogo from '../../../icons/logo.webp';
import About from '../../components/About';
import ResetVNCDialog from '../../components/ResetVNCDialog';
import TrafficLights from '../../components/TrafficLights/TrafficLights';
import Session from './Session';
import {ipcRenderer} from '../../../actions/ipc';

export default class Dashboard extends React.Component {
  constructor(props) {
    super(props);
    document.title = 'iCtrl - Dashboard';

    this.state = {
      addNewSessionOpen: false,
      changeMachineSessionId: null,
      loading_sessions: true,
      sessions: {},
      isLocal: true,
      aboutOpened: false,
      resettingSessionID: null,
    };
  }

  handleAddNewSession = (_) => {
    this.setState({addNewSessionOpen: true});
  };

  handleChangeMachineOpen = (sessionId) => {
    this.setState({changeMachineSessionId: sessionId});
  };

  handleChangeMachineClose = () => {
    this.setState({changeMachineSessionId: null});
  };

  handleAddNewSessionClose = (_) => {
    this.setState({
      addNewSessionOpen: false,
    });
  };

  handleLogout = () => {
    axios.get('/api/logout').finally(_ => {
      window.location = '/';
    });
  };
  handleAboutOpen = () => {
    this.setState({
      aboutOpened: true,
    });
  };

  handleAboutClose = () => {
    this.setState({
      aboutOpened: false,
    });
  };

  handleResetDialogOpen = (sessionID) => {
    this.setState({
      resettingSessionID: sessionID,
    });
  };
  handleResetDialogClose = () => {
    this.setState({
      resettingSessionID: null,
    });
  };

  handleDoubleClickAppBar = () => {
    ipcRenderer.send('win-max');
  };

  componentDidMount() {
    axios.get('/api/profiles').then(response => {
      const {sessions, version} = response.data;
      this.setState({
        loading_sessions: false,
        sessions: sessions,
        isLocal: Boolean(version),
      });
    }).catch(_ => {
      // if not accessing directly from Electron
      if (window.location.protocol !== 'file:') {
        // possibly not logged in
        window.location = '/';
      }
    });
  }

  render() {
    const {
      changeMachineSessionId,
      addNewSessionOpen,
      loading_sessions,
      sessions,
      isLocal,
      aboutOpened,
      resettingSessionID,
    } = this.state;

    const platform = window.require &&
        window.require('electron').ipcRenderer.sendSync('platform');

    const sessionList = [];
    const changeMachineHost = Boolean(changeMachineSessionId) ?
        sessions[changeMachineSessionId].host :
        null;

    for (const [sessionID, sessionProps] of Object.entries(sessions)) {
      sessionList.push(<Session key={`session-${sessionID}`}
                                sessionID={sessionID}
                                setResetDialogOpen={this.handleResetDialogOpen}
                                setChangeMachineOpen={this.handleChangeMachineOpen}
                                {...sessionProps}/>);
    }

    return (
        <>
          <AppBar position="static" color={'primary'} id={'titlebar'}
                  onDoubleClick={this.handleDoubleClickAppBar}>
            <Toolbar>
              {platform === 'darwin' &&
                  <div style={{width: '64px'}}/>}
              <img src={ictrlLogo} style={{
                // background: 'white',
                height: '30px',
                width: '30px',
                marginRight: '16px',
              }} alt="ictrl-logo"/>
              <Typography variant="h5" component="div"
                          sx={{flexGrow: 1}}>
                iCtrl Dashboard
              </Typography>
              <Tooltip title="About iCtrl"
                       className={'titlebar-buttons'}>
                <span>
                  <IconButton disabled={loading_sessions}
                              onClick={this.handleAboutOpen}
                              size={'large'}>
                    <InfoIcon style={{color: 'white'}}
                              fontSize="large"/>
                  </IconButton>
                </span>
              </Tooltip>
              <Tooltip title="Add new session"
                       className={'titlebar-buttons'}>
                <span>
                  <IconButton disabled={loading_sessions}
                              onClick={this.handleAddNewSession} size={'large'}>
                  <AddBoxIcon style={{color: 'white'}} fontSize="large"/>
                </IconButton>
                </span>
              </Tooltip>
              {isLocal ? (platform === 'win32' && <TrafficLights/>) :
                  <Tooltip title="Log out">
                    <IconButton edge={'end'}
                                onClick={this.handleLogout}
                                size={'large'}>
                      <LogoutIcon style={{color: 'white'}}
                                  fontSize="large"/>
                    </IconButton>
                  </Tooltip>
              }
            </Toolbar>
          </AppBar>

          {/* Display a greyed-out logo when there is no session configured */}
          {loading_sessions ?
              [...Array(3)].map((e, i) =>
                  <Skeleton key={`skeleton-${i}`} variant="rectangular"
                            height={75} style={{marginTop: 8}}/>,
              )
              :
              (sessionList.length !== 0 ?
                      <List>
                        {sessionList}
                      </List> :
                      <div style={{
                        display: 'flex',
                        flexDirection: 'column',
                        marginTop: '22vh',
                      }}>
                        <img style={{
                          margin: 'auto',
                          height: '20vh',
                          marginBottom: '8vh',
                          filter: 'grayscale(75%)',
                        }}
                             src={logo} alt="Logo"/>
                        <h4 style={{
                          margin: 'auto',
                          textAlign: 'center',
                          color: 'grey',
                        }}>No Session Found<br/>
                          Please click on <AddBoxIcon
                              style={{
                                color: 'grey',
                                position: 'relative',
                                top: '6px',
                              }}/> to add a new
                          session
                        </h4>
                      </div>
              )
          }

          <NewSession open={addNewSessionOpen}
                      onAddNewSessionClose={this.handleAddNewSessionClose}/>
          {Boolean(changeMachineSessionId) &&
              <ChangeMachine
                  session_id={changeMachineSessionId}
                  domain={changeMachineHost.substr(
                      changeMachineHost.indexOf('.'))}
                  onChangeMenuClose={this.handleChangeMachineClose}/>}
          {aboutOpened && <About onClose={this.handleAboutClose}/>}

          <ResetVNCDialog open={Boolean(resettingSessionID)}
                          sessionID={resettingSessionID}
                          onClose={this.handleResetDialogClose}/>
        </>
    );
  }
}