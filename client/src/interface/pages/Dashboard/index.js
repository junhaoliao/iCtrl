import React from 'react';
import {Helmet, HelmetProvider} from 'react-helmet-async';

import './index.css';

import {
    Box,
    Container,
    Divider,
    Hidden,
    IconButton,
    List,
    ListItem,
    ListItemAvatar,
    ListItemIcon,
    ListItemSecondaryAction,
    ListItemText,
    Menu,
    Tooltip,
    Typography
} from '@material-ui/core';
import AddCircleIcon from '@material-ui/icons/AddCircle';
import BackgroundLetterAvatar from '../../components/BackgroundLetterAvatar';
import StorageIcon from '@material-ui/icons/Storage';
import {ConsoleIcon, FileManagerIcon, RemoteDesktopIcon} from '../../../icons';
import MoreVertIcon from '@material-ui/icons/MoreVert';
import DeleteIcon from '@material-ui/icons/Delete';
import ChangeMachine from '../../components/ChangeMachine';

import MenuItem from '@material-ui/core/MenuItem';
import NewSession from '../../components/NewSession';
import axios from 'axios';

import logo from '../../../icons/logo.png';
import {canChangeMachine} from '../../../actions/utils';

export default class Dashboard extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            addNewSessionOpen: false,
            changeMachineSessionId: null,
            anchorEl: null,
            anchorSessionId: null,
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
                axios.delete(`/session`, {
                    params: {session_id: sessionId}
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
            anchorSessionId: session_id
        });
    };

    handleMenuClose = (_) => {
        this.setState({
            anchorEl: null,
            anchorSessionId: null
        });
    };

    handleMenuClick = (sessionId, type) => {
        this.setState({
            anchorEl: null,
            anchorSessionId: null
        });
        this.handleFeatureClick(sessionId, type);
    };

    handleAddNewSessionClose = (_) => {
        this.setState({
            addNewSessionOpen: false
        });
    };


    render() {
        const {
            anchorEl,
            anchorSessionId,
            changeMachineSessionId,
            addNewSessionOpen
        } = this.state;

        const sessionList = [];
        const sessions = this.props.profiles['sessions'];
        const changeMachineHost = Boolean(changeMachineSessionId)? sessions[changeMachineSessionId].host : null

        for (const [key, value] of Object.entries(sessions)) {
            const showCM = canChangeMachine(value.host);
            sessionList.push(
                <ListItem style={{cursor: 'default'}} button key={key}>
                    <ListItemAvatar>
                        <BackgroundLetterAvatar name={value.host}/>
                    </ListItemAvatar>
                    <ListItemText
                        primary={value.host}
                        primaryTypographyProps={{style: {fontSize: 18, fontWeight: 'bold', wordWrap: 'break-word'}}}
                        secondary={value.username}/>
                    <Menu
                        id="simple-menu"
                        anchorEl={anchorEl}
                        open={anchorSessionId === key}
                        onClose={this.handleMenuClose}
                    >
                        <Hidden smUp>
                            {showCM && <MenuItem>
                                <ListItemIcon><StorageIcon style={{color: '#4caf50'}}/></ListItemIcon>
                                Change Machine
                            </MenuItem>}
                            <MenuItem onClick={() => this.handleMenuClick(key, 'vnc')}>
                                <ListItemIcon><RemoteDesktopIcon style={{color: 'lightcoral'}}/>
                                </ListItemIcon>
                                VNC
                            </MenuItem>
                            <MenuItem onClick={() => this.handleMenuClick(key, 'term')}>
                                <ListItemIcon><ConsoleIcon style={{color: 'black'}}/></ListItemIcon>
                                Terminal
                            </MenuItem>
                            <MenuItem onClick={() => this.handleMenuClick(key, 'file')}>
                                <ListItemIcon><FileManagerIcon style={{color: '#1976d2'}}/></ListItemIcon>
                                File Manager
                            </MenuItem>
                        </Hidden>
                        <MenuItem onClick={() => this.handleMenuClick(key, 'delete')}>
                            <ListItemIcon><DeleteIcon style={{color: 'grey'}}/></ListItemIcon>
                            Delete
                        </MenuItem>
                    </Menu>
                    <ListItemSecondaryAction>
                        <Hidden smDown>
                            {showCM &&
                            <Tooltip title="Change Machine" aria-label="change machine">
                                <IconButton onClick={() => this.handleFeatureClick(key, 'CM')}>
                                    <StorageIcon style={{color: '#4caf50'}} fontSize={'large'}/>
                                </IconButton>
                            </Tooltip>
                            }
                            <Tooltip title="VNC" aria-label="VNC">
                                <IconButton onClick={() => this.handleFeatureClick(key, 'vnc')}>
                                    <RemoteDesktopIcon style={{color: 'lightcoral'}} fontSize={'large'}/>
                                </IconButton>
                            </Tooltip>
                            <Tooltip title="Terminal" aria-label="terminal">
                                <IconButton onClick={() => this.handleFeatureClick(key, 'term')}>
                                    <ConsoleIcon style={{color: 'black'}} fontSize={'large'}/>
                                </IconButton>
                            </Tooltip>
                            <Tooltip title="File Manger" aria-label="file manager">
                                <IconButton onClick={() => this.handleFeatureClick(key, 'file')}>
                                    <FileManagerIcon style={{color: '#1976d2'}} fontSize={'large'}/>
                                </IconButton>
                            </Tooltip>
                        </Hidden>
                        <Tooltip title="More Options" aria-label="more options">
                            <IconButton onClick={(ev) => this.handleMenuOpen(ev, key)}>
                                <MoreVertIcon fontSize={'large'}/>
                            </IconButton>
                        </Tooltip>
                    </ListItemSecondaryAction>
                </ListItem>
            );
        }

        return (
            <Container maxWidth={'lg'}>
                <HelmetProvider>
                    <Helmet>
                        <title>iCtrl - Dashboard</title>
                    </Helmet>
                </HelmetProvider>

                <br/><br/>
                <Box display="flex">
                    <Typography flexGrow={1} variant={'h3'}>Dashboard</Typography>
                    <IconButton onClick={this.handleAddNewSession} size={'large'}>
                        <AddCircleIcon style={{color: 'darkorange'}} fontSize="large"/>
                    </IconButton>
                </Box>
                <Divider/>

                {/* Display a greyed-out logo when there is no session configured */}
                {sessionList.length !== 0 ?
                    <List>
                        {sessionList}
                    </List> :
                    <div style={{display: 'flex', flexDirection: 'column', marginTop: '22vh'}}>
                        <img style={{margin: 'auto', height: '20vh', marginBottom: '8vh', filter: 'grayscale(75%)'}}
                             src={logo} alt="Logo"/>
                        <h4 style={{margin: 'auto', textAlign: 'center', color: 'grey'}}>No Session Found<br/>
                            Please click on <AddCircleIcon
                                style={{color: 'orange', position: 'relative', top: '6px'}}/> to add a new session</h4>
                    </div>
                }

                <NewSession open={addNewSessionOpen} onAddNewSessionClose={this.handleAddNewSessionClose}/>
                {Boolean(changeMachineSessionId) &&
                <ChangeMachine
                    session_id={changeMachineSessionId}
                    domain={changeMachineHost.substr(changeMachineHost.indexOf('.'))}
                    onChangeMenuClose={this.handleChangeMachineClose}/>}
            </Container>
        );
    }

}