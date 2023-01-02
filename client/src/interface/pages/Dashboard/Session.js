/*
 * Copyright (c) 2022 iCtrl Developers
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

import React, {createRef} from 'react';
import {
  CircularProgress,
  Hidden,
  IconButton,
  ListItem,
  ListItemAvatar,
  ListItemIcon,
  ListItemSecondaryAction,
  ListItemText,
  Menu,
  Popover,
  TextField,
  Tooltip,
} from '@mui/material';
import BackgroundLetterAvatar from '../../components/BackgroundLetterAvatar';
import MenuItem from '@mui/material/MenuItem';
import StorageIcon from '@mui/icons-material/Storage';
import {ConsoleIcon, FileManagerIcon, RemoteDesktopIcon} from '../../../icons';
import RefreshIcon from '@mui/icons-material/Refresh';
import DeleteIcon from '@mui/icons-material/Delete';
import MoreVertIcon from '@mui/icons-material/MoreVert';
import {canChangeMachine} from '../../../actions/utils';
import EditIcon from '@mui/icons-material/Edit';
import wcwidth from 'wcwidth';
import {
  getAvatarName,
  session_change_nickname,
  session_delete,
} from '../../../actions/session';
import {
  COLOR_CHANGE_MACHINE,
  COLOR_FILE_MANAGER,
  COLOR_TERM_VIEWER,
  COLOR_VNC_VIEWER,
} from '../../constants';

export default class Session extends React.Component {
  constructor(props) {
    super(props);

    this.nicknameAvatarRef = createRef();
    this.lastStoredNickname = '';

    this.moreButtonRef = createRef();

    this.state = {
      nickname: '',
      contextMenuAnchorEl: null,
      nicknameHovering: false,
      nicknamePopoverAnchorEl: null,
      nicknameChangeLoading: false,
      anchorMouseTop: null,
      anchorMouseLeft: null,
    };
  }

  handleFeatureClick(type) {
    const {sessionID, setResetDialogOpen, setChangeMachineOpen} = this.props;
    switch (type) {
      case 'CM':
        setChangeMachineOpen(sessionID);
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
        session_delete(sessionID);
        break;
      case 'resetVNC':
        setResetDialogOpen(sessionID);
        break;
      default:
        alert(`Feature ${type} on session ${sessionID} not implemented. `);
        return;
    }
  }

  handleContextMenuOpen = (ev) => {
    if (ev.type === 'contextmenu') {
      this.setState({
        anchorMouseLeft: ev.clientX,
        anchorMouseTop: ev.clientY,
      });
    } else if (ev.type === 'click') {
      this.setState({
        contextMenuAnchorEl: this.moreButtonRef.current,
      });
    } else {
      console.error(`Unknown event type: ${ev.type}`);
    }
  };

  handleContextMenuClose = () => {
    this.setState({
      contextMenuAnchorEl: null,
      anchorMouseTop: null,
      anchorMouseLeft: null,
    });
  };

  handleContextMenuClick = (type) => {
    this.handleContextMenuClose();
    this.handleFeatureClick(type);
  };

  handleNicknamePopoverOpen = () => {
    this.setState({
      nicknameHovering: true,
      nicknamePopoverAnchorEl: this.nicknameAvatarRef.current,
    });
  };

  handleNicknamePopoverClose = () => {
    const {sessionID, host} = this.props;
    const {nickname} = this.state;
    this.setState({
      nicknamePopoverAnchorEl: null,
      nicknameHovering: false,
    });
    if (nickname !== this.lastStoredNickname) {
      this.setState({
        nicknameChangeLoading: true,
      });
      session_change_nickname(this, sessionID, nickname, host);
    }
  };

  handleNicknameInputKeyDown = (ev) => {
    if (ev.key === 'Enter') {
      setTimeout(() => {
        this.handleNicknamePopoverClose();
      }, 0);
    }
  };
  handleNicknameInputChange = (ev) => {
    this.setState({
      nickname: ev.target.value,
    });
  };

  componentDidMount() {
    const {host, nickname} = this.props;
    const _nickname = (nickname && nickname !== '') ?
        nickname :
        getAvatarName(host);

    this.lastStoredNickname = _nickname;
    this.setState({nickname: _nickname});
  }

  render() {
    const {sessionID, host, username} = this.props;
    const {
      nickname,
      contextMenuAnchorEl,
      nicknameHovering,
      nicknamePopoverAnchorEl,
      nicknameChangeLoading,
      anchorMouseTop,
      anchorMouseLeft,
    } = this.state;

    const showCM = canChangeMachine(host);

    let doubleClickToOpenVNCTimeout = null;
    return (<>
      <ListItem style={{cursor: 'default'}}
                button={true}
                key={sessionID}
                onClick={(ev) => {
                  if (ev.target.className.includes &&
                      ev.target.className.includes(
                          'MuiBackdrop-root')) {
                    // don't open VNC when the menu button is double-clicked
                    return;
                  }
                  if (ev.detail === 2) {
                    // open VNC when double-clicked
                    doubleClickToOpenVNCTimeout = setTimeout(() => {
                      this.handleContextMenuClick('vnc');
                    }, 300);
                  } else if (ev.detail === 3) {
                    if (doubleClickToOpenVNCTimeout) {
                      clearTimeout(doubleClickToOpenVNCTimeout);
                      doubleClickToOpenVNCTimeout = null;
                    }
                    this.handleContextMenuClick('term');
                  }
                }}
                onContextMenu={(ev) => {
                  ev.preventDefault();

                  this.handleContextMenuClose();

                  if (contextMenuAnchorEl === null &&
                      anchorMouseLeft === null) {
                    this.handleContextMenuOpen(ev);
                  }
                }}
      >
        <ListItemAvatar>
          <IconButton ref={this.nicknameAvatarRef}
                      disabled={nicknameChangeLoading} size={'small'}
                      edge={'start'}
                      onFocus={() => {
                        this.setState({nicknameHovering: true});
                      }}
                      onMouseEnter={() => {
                        this.setState({nicknameHovering: true});
                      }}
                      onBlur={() => {
                        if (nicknamePopoverAnchorEl === null) {
                          this.setState({nicknameHovering: false});
                        }
                      }}
                      onMouseLeave={() => {
                        if (nicknamePopoverAnchorEl === null) {
                          this.setState({nicknameHovering: false});
                        }
                      }}
                      onClick={this.handleNicknamePopoverOpen}
          >
            {nicknameChangeLoading ? <CircularProgress/> :
                <div style={{filter: nicknameHovering && 'brightness(85%)'}}>
                  <BackgroundLetterAvatar
                      badgeContent={nicknameHovering &&
                          <EditIcon fontSize={'small'}/>}
                      name={nickname}/>
                </div>}

          </IconButton>
        </ListItemAvatar>
        <ListItemText
            primary={host}
            primaryTypographyProps={{
              style: {
                fontSize: 18,
                fontWeight: 'bold',
                wordWrap: 'break-word',
              },
            }}
            secondary={username}
        />
        <Menu
            anchorEl={contextMenuAnchorEl}
            anchorOrigin={{vertical: 'bottom', horizontal: 'right'}}
            anchorReference={anchorMouseTop === null ?
                'anchorEl' :
                'anchorPosition'}
            anchorPosition={anchorMouseTop &&
                {left: anchorMouseLeft, top: anchorMouseTop}}
            open={contextMenuAnchorEl !== null || anchorMouseTop !== null}
            onClose={this.handleContextMenuClose}
        >
          <Hidden smUp>
            {showCM &&
                <MenuItem
                    onClick={() => this.handleContextMenuClick('CM')}>
                  <ListItemIcon>
                    <StorageIcon style={{color: COLOR_CHANGE_MACHINE}}/>
                  </ListItemIcon>
                  Change Machine
                </MenuItem>}
            <MenuItem
                onClick={() => this.handleContextMenuClick('vnc')}>
              <ListItemIcon>
                <RemoteDesktopIcon style={{color: COLOR_VNC_VIEWER}}/>
              </ListItemIcon>
              VNC
            </MenuItem>
            <MenuItem
                onClick={() => this.handleContextMenuClick('term')}>
              <ListItemIcon>
                <ConsoleIcon style={{color: COLOR_TERM_VIEWER}}/>
              </ListItemIcon>
              Terminal
            </MenuItem>
            <MenuItem
                onClick={() => this.handleContextMenuClick('file')}>
              <ListItemIcon>
                <FileManagerIcon style={{color: COLOR_FILE_MANAGER}}/>
              </ListItemIcon>
              File Manager
            </MenuItem>
          </Hidden>
          <MenuItem
              onClick={() => this.handleContextMenuClick('resetVNC')}>
            <ListItemIcon>
              <RefreshIcon style={{color: 'orange'}}/>
            </ListItemIcon>
            Reset VNC
          </MenuItem>
          <MenuItem
              onClick={() => this.handleContextMenuClick('delete')}>
            <ListItemIcon>
              <DeleteIcon style={{color: 'grey'}}/></ListItemIcon>
            Delete
          </MenuItem>
        </Menu>
        <ListItemSecondaryAction>
          <Hidden smDown>
            {showCM &&
                <Tooltip title="Change Machine" aria-label="change machine">
                  <IconButton
                      onClick={() => this.handleFeatureClick('CM')}>
                    <StorageIcon style={{color: COLOR_CHANGE_MACHINE}}
                                 fontSize={'large'}/>
                  </IconButton>
                </Tooltip>
            }
            <Tooltip title="VNC" aria-label="VNC">
              <IconButton
                  onClick={() => this.handleFeatureClick('vnc')}>
                <RemoteDesktopIcon style={{color: COLOR_VNC_VIEWER}}
                                   fontSize={'large'}/>
              </IconButton>
            </Tooltip>
            <Tooltip title="Terminal" aria-label="terminal">
              <IconButton
                  onClick={() => this.handleFeatureClick('term')}>
                <ConsoleIcon style={{color: COLOR_TERM_VIEWER}}
                             fontSize={'large'}/>
              </IconButton>
            </Tooltip>
            <Tooltip title="File Manager" aria-label="file manager">
              <IconButton
                  onClick={() => this.handleFeatureClick('file')}>
                <FileManagerIcon style={{color: COLOR_FILE_MANAGER}}
                                 fontSize={'large'}/>
              </IconButton>
            </Tooltip>
          </Hidden>
          <Tooltip title="More Options" aria-label="more options">
            <IconButton
                ref={this.moreButtonRef}
                onClick={this.handleContextMenuOpen}>
              <MoreVertIcon fontSize={'large'}/>
            </IconButton>
          </Tooltip>
        </ListItemSecondaryAction>
      </ListItem>
      <Popover open={nicknamePopoverAnchorEl !== null}
               anchorEl={nicknamePopoverAnchorEl}
               anchorOrigin={{
                 vertical: 'bottom',
                 horizontal: 'left',
               }}
               onClose={this.handleNicknamePopoverClose}>
        <TextField
            autoFocus={true}
            sx={{
              minWidth: nickname === '' ? `${10 * 8 + 28}px` : `${28}px`,
              width: `${10 * wcwidth(nickname) + 28}px`,
            }}
            size={'small'}
            placeholder={'Nickname'}
            inputProps={{maxLength: 8, style: {fontFamily: 'monospace'}}}
            value={nickname}
            onKeyDown={this.handleNicknameInputKeyDown}
            onFocus={(ev) => {
              ev.target.select();
            }}
            onChange={this.handleNicknameInputChange}/>
      </Popover>
    </>);
  }
}

