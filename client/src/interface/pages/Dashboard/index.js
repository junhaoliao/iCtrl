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
  Hidden,
  IconButton,
  List,
  ListItem,
  ListItemAvatar,
  ListItemIcon,
  ListItemSecondaryAction,
  ListItemText,
  Menu,
  Skeleton,
  Toolbar,
  Tooltip,
  Typography,
} from '@mui/material';
import AddBoxIcon from '@mui/icons-material/AddBox';
import InfoIcon from '@mui/icons-material/Info';
import BackgroundLetterAvatar from '../../components/BackgroundLetterAvatar';
import StorageIcon from '@mui/icons-material/Storage';
import {ConsoleIcon, FileManagerIcon, RemoteDesktopIcon} from '../../../icons';
import MoreVertIcon from '@mui/icons-material/MoreVert';
import DeleteIcon from '@mui/icons-material/Delete';
import RefreshIcon from '@mui/icons-material/Refresh';
import ChangeMachine from '../../components/ChangeMachine';
import LogoutIcon from '@mui/icons-material/Logout';

import MenuItem from '@mui/material/MenuItem';
import NewSession from '../../components/NewSession';
import axios from 'axios';

import logo from '../../../icons/logo.webp';
import ictrlLogo from '../../../icons/logo.webp';
import {canChangeMachine, openInNewWindow} from '../../../actions/utils';
import About from '../../components/About';
import GitHubButton from 'react-github-btn';
import ResetVNCDialog from '../../components/ResetVNCDialog';
import TrafficLights from '../../components/TrafficLights/TrafficLights';

export default class Dashboard extends React.Component {
  constructor(props) {
    super(props);
    document.title = 'iCtrl - Dashboard';

    this.state = {
      addNewSessionOpen: false,
      changeMachineSessionId: null,
      anchorEl: null,
      anchorSessionId: null,
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

  handleFeatureClick(sessionID, type) {
    switch (type) {
      case 'CM':
        this.handleChangeMachineOpen(sessionID);
        break;
      case 'vnc':
        window.open(`/vnc/${sessionID}`, '_blank');
        break;
      case 'term':
        window.open(`/terminal/${sessionID}`, '_blank');
        break;
      case 'file':
        window.open(`/fm/${sessionID}`, '_blank');
        break;
      case 'delete':
        axios.delete(`/api/session`, {
          params: {session_id: sessionID},
        }).then(response => {
          console.log(response.data);
          window.location.reload();
        }).catch(error => {
          console.log(error);
        });
        break;
      case 'resetVNC':
        this.setState({
          resettingSessionID: sessionID,
        });
        break;
      default:
        alert(`Feature ${type} on session ${sessionID} not implemented. `);
        return;
    }
  }

  handleMenuOpen = (target, session_id) => {
    this.setState({
      anchorEl: target,
      anchorSessionId: session_id,
    });
  };

  handleMenuClose = (_) => {
    this.setState({
      anchorEl: null,
      anchorSessionId: null,
    });
  };

  handleMenuClick = (sessionId, type) => {
    this.setState({
      anchorEl: null,
      anchorSessionId: null,
    });
    this.handleFeatureClick(sessionId, type);
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

  handleResetDialogClose = () => {
    this.setState({
      resettingSessionID: null,
    });
  };

  handleDoubleClickAppBar = () => {
    const {ipcRenderer} = window.require('electron');
    if (ipcRenderer) {
      ipcRenderer.send('win-max');
    }
  };

  componentDidMount() {
    axios.get('/api/profiles').then(response => {
      const {sessions, version} = response.data;
      this.setState({
        loading_sessions: false,
        sessions: sessions,
        isLocal: Boolean(version),
      });
    }).catch(error => {
      // if not accessing directly from Electron
      if (window.location.protocol !== 'file:') {
        // possibly not logged in
        window.location = '/';
      }
    });
  }

  render() {
    const {
      anchorEl,
      anchorSessionId,
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

    let doubleClickToOpenVNCTimeout = null;

    for (const [sessionID, sessionProps] of Object.entries(sessions)) {
      const showCM = canChangeMachine(sessionProps.host);
      sessionList.push(
          <ListItem style={{cursor: 'default'}} button key={sessionID}
                    onClick={(ev) => {
                      if (ev.target.className.includes(
                          'MuiBackdrop-root')) {
                        // don't open VNC when the menu button is double-clicked
                        return;
                      }
                      if (ev.detail === 2) {
                        // open VNC when double-clicked
                        doubleClickToOpenVNCTimeout = setTimeout(() => {
                          this.handleMenuClick(sessionID, 'vnc');
                        }, 300);
                      } else if (ev.detail === 3) {
                        if (doubleClickToOpenVNCTimeout) {
                          clearTimeout(doubleClickToOpenVNCTimeout);
                          doubleClickToOpenVNCTimeout = null;
                        }
                        this.handleMenuClick(sessionID, 'term');
                      }
                    }}
                    onContextMenu={(ev) => {
                      ev.preventDefault();

                      this.handleMenuClose();

                      if (this.state.anchorEl === null) {
                        // using this as anchor seems not to cover any valid info
                        const anchorElem = document.getElementById(
                            `${sessionID}-username`);
                        this.handleMenuOpen(anchorElem, sessionID);
                      }
                    }}
          >
            <ListItemAvatar>
              <BackgroundLetterAvatar name={sessionProps.host}/>
            </ListItemAvatar>
            <ListItemText
                primary={sessionProps.host}
                primaryTypographyProps={{
                  style: {
                    fontSize: 18,
                    fontWeight: 'bold',
                    wordWrap: 'break-word',
                  },
                }}
                secondary={<div id={`${sessionID}-username`}>
                  {sessionProps.username}
                </div>}/>
            <Menu
                anchorEl={anchorEl}
                open={anchorSessionId === sessionID}
                onClose={this.handleMenuClose}
            >
              <Hidden smUp>
                {showCM &&
                    <MenuItem
                        onClick={() => this.handleMenuClick(sessionID, 'CM')}>
                      <ListItemIcon><StorageIcon
                          style={{color: '#4caf50'}}/></ListItemIcon>
                      Change Machine
                    </MenuItem>}
                <MenuItem
                    onClick={() => this.handleMenuClick(sessionID, 'vnc')}>
                  <ListItemIcon><RemoteDesktopIcon
                      style={{color: 'lightcoral'}}/>
                  </ListItemIcon>
                  VNC
                </MenuItem>
                <MenuItem
                    onClick={() => this.handleMenuClick(sessionID, 'term')}>
                  <ListItemIcon><ConsoleIcon
                      style={{color: 'black'}}/></ListItemIcon>
                  Terminal
                </MenuItem>
                <MenuItem
                    onClick={() => this.handleMenuClick(sessionID, 'file')}>
                  <ListItemIcon><FileManagerIcon
                      style={{color: '#1976d2'}}/></ListItemIcon>
                  File Manager
                </MenuItem>
              </Hidden>
              <MenuItem
                  onClick={() => this.handleMenuClick(sessionID, 'resetVNC')}>
                <ListItemIcon><RefreshIcon
                    style={{color: 'orange'}}/>
                </ListItemIcon>
                Reset VNC
              </MenuItem>
              <MenuItem
                  onClick={() => this.handleMenuClick(sessionID, 'delete')}>
                <ListItemIcon><DeleteIcon
                    style={{color: 'grey'}}/></ListItemIcon>
                Delete
              </MenuItem>
            </Menu>
            <ListItemSecondaryAction>
              <Hidden smDown>
                {showCM &&
                    <Tooltip title="Change Machine" aria-label="change machine">
                      <IconButton
                          onClick={() => this.handleFeatureClick(sessionID,
                              'CM')}>
                        <StorageIcon style={{color: '#4caf50'}}
                                     fontSize={'large'}/>
                      </IconButton>
                    </Tooltip>
                }
                <Tooltip title="VNC" aria-label="VNC">
                  <IconButton
                      onClick={() => this.handleFeatureClick(sessionID, 'vnc')}>
                    <RemoteDesktopIcon style={{color: 'lightcoral'}}
                                       fontSize={'large'}/>
                  </IconButton>
                </Tooltip>
                <Tooltip title="Terminal" aria-label="terminal">
                  <IconButton
                      onClick={() => this.handleFeatureClick(sessionID,
                          'term')}>
                    <ConsoleIcon style={{color: 'black'}} fontSize={'large'}/>
                  </IconButton>
                </Tooltip>
                <Tooltip title="File Manager" aria-label="file manager">
                  <IconButton
                      onClick={() => this.handleFeatureClick(sessionID,
                          'file')}>
                    <FileManagerIcon style={{color: '#1976d2'}}
                                     fontSize={'large'}/>
                  </IconButton>
                </Tooltip>
              </Hidden>
              <Tooltip title="More Options" aria-label="more options">
                <IconButton
                    onClick={(ev) => this.handleMenuOpen(ev.target, sessionID)}>
                  <MoreVertIcon fontSize={'large'}/>
                </IconButton>
              </Tooltip>
            </ListItemSecondaryAction>
          </ListItem>,
      );
    }

    return (
        <>
          <AppBar position="static" color={'primary'} id={'titlebar'}
                  onDoubleClick={this.handleDoubleClickAppBar}>
            <Toolbar>
              {platform === 'darwin' && <div style={{width: '64px'}}/>}
              <img src={ictrlLogo} style={{
                // background: 'white',
                height: '30px',
                width: '30px',
                marginRight: '16px',
              }} alt="ictrl-logo"/>
              <Typography variant="h5" component="div" sx={{flexGrow: 1}}>
                iCtrl Dashboard
              </Typography>
              <div
                  className={'titlebar-buttons'}
                  onClick={(ev) => {
                    openInNewWindow('https://github.com/junhaoliao/iCtrl', ev);
                  }}
                  style={{
                    marginTop: '5px',
                    marginRight: '16px',
                    overflowX: 'auto',
                    overflowY: 'hidden',
                  }}>
                <GitHubButton href="https://github.com/junhaoliao/iCtrl"
                              data-color-scheme="no-preference: light_high_contrast; light: light_high_contrast; dark: light_high_contrast;"
                              data-show-count="true"
                              aria-label="Star junhaoliao/iCtrl on GitHub">Star</GitHubButton>

              </div>
              <Tooltip title="About iCtrl" className={'titlebar-buttons'}>
                <IconButton onClick={this.handleAboutOpen} size={'large'}>
                  <InfoIcon style={{color: 'white'}} fontSize="large"/>
                </IconButton>
              </Tooltip>
              <Tooltip title="Add new session" className={'titlebar-buttons'}>
                <span>
                  <IconButton disabled={loading_sessions}
                              onClick={this.handleAddNewSession} size={'large'}>
                  <AddBoxIcon style={{color: 'white'}} fontSize="large"/>
                </IconButton>
                </span>
              </Tooltip>
              {isLocal ? (platform === 'win32' && <TrafficLights/>) :
                  <Tooltip title="Log out">
                    <IconButton edge={'end'} onClick={this.handleLogout}
                                size={'large'}>
                      <LogoutIcon style={{color: 'white'}} fontSize="large"/>
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