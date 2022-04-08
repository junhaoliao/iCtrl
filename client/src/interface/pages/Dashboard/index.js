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
} from '@material-ui/core';
import AddBoxIcon from '@material-ui/icons/AddBox';
import InfoIcon from '@material-ui/icons/Info';
import BackgroundLetterAvatar from '../../components/BackgroundLetterAvatar';
import StorageIcon from '@material-ui/icons/Storage';
import {ConsoleIcon, FileManagerIcon, RemoteDesktopIcon} from '../../../icons';
import MoreVertIcon from '@material-ui/icons/MoreVert';
import DeleteIcon from '@material-ui/icons/Delete';
import ChangeMachine from '../../components/ChangeMachine';
import LogoutIcon from '@material-ui/icons/Logout';

import MenuItem from '@material-ui/core/MenuItem';
import NewSession from '../../components/NewSession';
import axios from 'axios';

import logo from '../../../icons/logo.png';
import {canChangeMachine} from '../../../actions/utils';
import About from '../../components/About';

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

  handleFeatureClick(sessionId, type) {
    switch (type) {
      case 'CM':
        this.handleChangeMachineOpen(sessionId);
        break;
      case 'vnc':
        window.open(`/vnc/${sessionId}`, '_blank');
        break;
      case 'term':
        window.open(`/terminal/${sessionId}`, '_blank');
        break;
      case 'file':
        window.open(`/fm/${sessionId}`, '_blank');
        break;
      case 'delete':
        axios.delete(`/api/session`, {
          params: {session_id: sessionId},
        }).then(response => {
          console.log(response.data);
          window.location.reload();
        }).catch(error => {
          console.log(error);
        });
        break;
      default:
        return;
    }
  }

  handleMenuOpen = (ev, session_id) => {
    this.setState({
      anchorEl: ev.target,
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

  componentDidMount() {
    axios.get('/api/profiles').then(response => {
      const {sessions, version} = response.data;
      this.setState({
        loading_sessions: false,
        sessions: sessions,
        isLocal: Boolean(version),
      });
    }).catch(error => {
      // possibly not logged in
      window.location = '/';
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
    } = this.state;

    const sessionList = [];
    const changeMachineHost = Boolean(changeMachineSessionId) ?
        sessions[changeMachineSessionId].host :
        null;

    for (const [key, value] of Object.entries(sessions)) {
      const showCM = canChangeMachine(value.host);
      sessionList.push(
          <ListItem style={{cursor: 'default'}} button key={key}>
            <ListItemAvatar>
              <BackgroundLetterAvatar name={value.host}/>
            </ListItemAvatar>
            <ListItemText
                primary={value.host}
                primaryTypographyProps={{
                  style: {
                    fontSize: 18,
                    fontWeight: 'bold',
                    wordWrap: 'break-word',
                  },
                }}
                secondary={value.username}/>
            <Menu
                id="simple-menu"
                anchorEl={anchorEl}
                open={anchorSessionId === key}
                onClose={this.handleMenuClose}
            >
              <Hidden smUp>
                {showCM &&
                    <MenuItem onClick={() => this.handleMenuClick(key, 'CM')}>
                      <ListItemIcon><StorageIcon
                          style={{color: '#4caf50'}}/></ListItemIcon>
                      Change Machine
                    </MenuItem>}
                <MenuItem onClick={() => this.handleMenuClick(key, 'vnc')}>
                  <ListItemIcon><RemoteDesktopIcon
                      style={{color: 'lightcoral'}}/>
                  </ListItemIcon>
                  VNC
                </MenuItem>
                <MenuItem onClick={() => this.handleMenuClick(key, 'term')}>
                  <ListItemIcon><ConsoleIcon
                      style={{color: 'black'}}/></ListItemIcon>
                  Terminal
                </MenuItem>
                <MenuItem onClick={() => this.handleMenuClick(key, 'file')}>
                  <ListItemIcon><FileManagerIcon
                      style={{color: '#1976d2'}}/></ListItemIcon>
                  File Manager
                </MenuItem>
              </Hidden>
              <MenuItem onClick={() => this.handleMenuClick(key, 'delete')}>
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
                          onClick={() => this.handleFeatureClick(key, 'CM')}>
                        <StorageIcon style={{color: '#4caf50'}}
                                     fontSize={'large'}/>
                      </IconButton>
                    </Tooltip>
                }
                <Tooltip title="VNC" aria-label="VNC">
                  <IconButton
                      onClick={() => this.handleFeatureClick(key, 'vnc')}>
                    <RemoteDesktopIcon style={{color: 'lightcoral'}}
                                       fontSize={'large'}/>
                  </IconButton>
                </Tooltip>
                <Tooltip title="Terminal" aria-label="terminal">
                  <IconButton
                      onClick={() => this.handleFeatureClick(key, 'term')}>
                    <ConsoleIcon style={{color: 'black'}} fontSize={'large'}/>
                  </IconButton>
                </Tooltip>
                <Tooltip title="File Manager" aria-label="file manager">
                  <IconButton
                      onClick={() => this.handleFeatureClick(key, 'file')}>
                    <FileManagerIcon style={{color: '#1976d2'}}
                                     fontSize={'large'}/>
                  </IconButton>
                </Tooltip>
              </Hidden>
              <Tooltip title="More Options" aria-label="more options">
                <IconButton onClick={(ev) => this.handleMenuOpen(ev, key)}>
                  <MoreVertIcon fontSize={'large'}/>
                </IconButton>
              </Tooltip>
            </ListItemSecondaryAction>
          </ListItem>,
      );
    }

    return (
        <>
          <AppBar position="static" color={'info'}>
            <Toolbar>
              <Typography variant="h5" component="div" sx={{flexGrow: 1}}>
                Dashboard
              </Typography>
              <Tooltip title="About iCtrl">
                <IconButton onClick={this.handleAboutOpen} size={'large'}>
                  <InfoIcon style={{color: 'white'}} fontSize="large"/>
                </IconButton>
              </Tooltip>
              <Tooltip title="Add new session">
                <IconButton onClick={this.handleAddNewSession} size={'large'}>
                  <AddBoxIcon style={{color: 'white'}} fontSize="large"/>
                </IconButton>
              </Tooltip>
              {!isLocal &&
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
        </>
    );
  }

}