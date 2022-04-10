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

import {GridToolbarContainer} from '@mui/x-data-grid';
import {
  Button,
  Dialog,
  DialogActions,
  DialogContent,
  DialogContentText,
  DialogTitle,
  Hidden,
  IconButton,
  InputAdornment,
  Menu,
  MenuItem,
  OutlinedInput,
  TextField,
  Tooltip,
} from '@mui/material';
import {
  ArrowUpward,
  Delete,
  DriveFileRenameOutline,
  GetApp,
  KeyboardArrowRight,
  PermIdentity,
  Visibility,
  VisibilityOff,
} from '@mui/icons-material';
import MenuIcon from '@mui/icons-material/Menu';

import {
  DensityComfortableIcon,
  DensityCompactIcon,
  DensityIcon,
  DensityStandardIcon,
} from '../../../icons';
import {sftp_dl, sftp_rm} from '../../../actions/sftp';

export default class CustomToolbar extends React.Component {
  constructor(props) {
    super(props);

    this.state = {
      renamePromptOpen: false,
      densityMenuAnchorEl: null,
      deleteAllPromptOpen: false,
    };
  }

  handleShowSideBar = (_) => {
    this.props.fm.setState({sideBarOpen: true});
  };

  handleClose = (_) => {
    this.setState({
      densityMenuAnchorEl: null,
    });
  };

  handleMenuOpen = (ev) => {
    this.setState({
      densityMenuAnchorEl: ev.currentTarget,
    });
  };

  handleDensityChange = (ev) => {
    this.props.fm.setState({
      density: ev.currentTarget.getAttribute('aria-label'),
    });
    this.setState({
      densityMenuAnchorEl: null,
    });
  };

  handleHiddenFiles = (_) => {
    const {showHidden} = this.props.fm.state;
    this.props.fm.setState({
      showHidden: !showHidden,
    });
  };

  handleRename = (_) => {
    const {fm} = this.props;
    if (fm.selected.length !== 1) {
      fm.showAlert('Please select only 1 file to rename. ');
      return;
    }

    this.setState({
      renamePromptOpen: true,
    });
  };

  handleChangePermissions = (_) => {
    const {fm} = this.props;
    if (fm.selected.length !== 1) {
      fm.showAlert('Please select only 1 file to change permissions. ');
      return;
    }

    const name = fm.selected[0];
    fm.handleChangePermission(name);
  };

  handleDownload = (_) => {
    if (this.props.fm.selected.length === 0) {
      this.props.fm.showAlert('No files selected for download. ');
      return;
    }
    sftp_dl(this.props.fm.session_id, this.props.fm.state.cwd,
        this.props.fm.selected);
  };

  handleRenamePrompt = (ev) => {
    if (ev.target.id === 'button-rename-proceed') {
      const {fm} = this.props;
      const oldName = fm.selected[0];
      const newName = document.getElementById('rename-newname').value;
      fm.handleChangeName(oldName, newName);
    }

    this.setState({
      renamePromptOpen: false,
    });
  };

  handleDeleteAllPrompt = (ev) => {
    if (ev.target.id !== 'button_proceed_delete') {
      this.setState({
        deleteAllPromptOpen: false,
      });
      return;
    }
    this.props.fm.setState({
      loading: true,
    });
    sftp_rm(this.props.fm, this.props.fm.session_id, this.props.fm.state.cwd,
        this.props.fm.selected);
    this.setState({
      deleteAllPromptOpen: false,
    });
  };

  handleDelete = (_) => {
    if (this.props.fm.selected.length === 0) {
      this.props.fm.showAlert('No files selected for removal.');
      return;
    }
    this.setState({
      deleteAllPromptOpen: true,
    });
  };

  handleCwdSubmit = (ev) => {
    const path = this.props.fm.state.cwdInput;
    this.props.fm.loadDir(path);

    ev.preventDefault();
  };

  handleCwdInputKeyPress = (ev) => {
    if (ev.key === 'Enter') {
      this.handleCwdSubmit(ev);
    }
  };

  handleCwdInputChange = (ev) => {
    this.props.fm.setState({
      cwdInput: ev.target.value,
    });
  };

  handleCwdInputBlur = (ev) => {
    if (ev === undefined) {
      return;
    }
    if (ev.relatedTarget && ev.relatedTarget.id === 'enter_button') {
      return;
    }
    this.props.fm.setState({
      cwdInput: this.props.fm.state.cwd,
      cwdInputErr: null,
    });
  };

  handleUpOneLevel = (_) => {
    const cwd = this.props.fm.state.cwd;
    const path = cwd.substring(0, cwd.lastIndexOf('/'));
    if (path === '') {
      this.props.fm.loadDir('/');
    } else {
      this.props.fm.loadDir(path);
    }

  };

  render() {
    const {fm} = this.props;
    const pluralSelection = fm.selected.length > 1;
    const {loading, showHidden} = fm.state;

    const {renamePromptOpen} = this.state;
    const onlySelectedId = fm.selected.length === 1 ? fm.selected[0] : '';

    return (
        <>
          <GridToolbarContainer
              style={{overflowX: 'auto', overflowY: 'hidden'}}>
            <Hidden smUp>
              <Tooltip title={'Show Side Bar'}>
                <IconButton
                    aria-label={'sidebar'}
                    onClick={this.handleShowSideBar}
                    color={'primary'}>
                  <MenuIcon/>
                </IconButton>
              </Tooltip>
            </Hidden>

            <Tooltip title={'Go to Parent Folder'}>
                <span><IconButton
                    disabled={loading}
                    aria-label={'up'}
                    onClick={this.handleUpOneLevel}
                    color={'primary'}>
                    <ArrowUpward/>
                </IconButton></span>
            </Tooltip>

            <OutlinedInput
                disabled={loading}
                fullWidth
                style={{height: 40, minWidth: 200}}
                autoComplete={'new-password'}
                onKeyPress={this.handleCwdInputKeyPress}
                onBlur={this.handleCwdInputBlur}
                onChange={this.handleCwdInputChange}
                value={this.props.fm.state.cwdInput}
                error={Boolean(this.props.fm.state.cwdInputErr)}
                endAdornment={
                  <InputAdornment position="end">
                    <IconButton
                        disabled={loading}
                        color={'primary'} id={'enter_button'} edge={'end'}
                        aria-label={'enter'}
                        onClick={this.handleCwdSubmit}>
                      <KeyboardArrowRight/>
                    </IconButton>
                  </InputAdornment>
                }
                inputProps={{'aria-label': 'current-directory'}}/>

            <Hidden smDown>
              <Tooltip title={'Density'}>
                <span><IconButton
                    disabled={loading}
                    color={'primary'}
                    onClick={this.handleMenuOpen}>
                    <DensityIcon/>
                </IconButton></span>
              </Tooltip>
            </Hidden>

            <Tooltip title={`${showHidden ? 'Hide' : 'Show'} Hidden Files`}>
                <span><IconButton
                    disabled={loading}
                    color={'primary'}
                    onClick={this.handleHiddenFiles}>
                    {showHidden ? <VisibilityOff/> : <Visibility/>}
                </IconButton></span>
            </Tooltip>

            <Tooltip title={'Rename'}>
                <span><IconButton
                    disabled={loading}
                    color={'primary'}
                    onClick={this.handleRename}>
                    <DriveFileRenameOutline/>
                </IconButton></span>
            </Tooltip>

            <Tooltip title={'Change Permissions'}>
                <span><IconButton
                    disabled={loading}
                    color={'primary'}
                    onClick={this.handleChangePermissions}>
                    <PermIdentity/>
                </IconButton></span>
            </Tooltip>

            <Tooltip title={'Delete'}>
                <span><IconButton
                    disabled={loading}
                    color={'primary'}
                    onClick={this.handleDelete}>
                    <Delete/>
                </IconButton></span>
            </Tooltip>

            <Tooltip title={'Download'}>
                <span><IconButton
                    disabled={loading}
                    color={'primary'}
                    onClick={this.handleDownload}>
                    <GetApp/>
                </IconButton></span>
            </Tooltip>
          </GridToolbarContainer>
          <Menu
              id="density"
              anchorEl={this.state.densityMenuAnchorEl}
              keepMounted
              open={Boolean(this.state.densityMenuAnchorEl)}
              onClose={this.handleClose}
          >
            <MenuItem aria-label="compact" onClick={this.handleDensityChange}>
              <DensityCompactIcon/>
              Compact
            </MenuItem>
            <MenuItem aria-label="standard" onClick={this.handleDensityChange}>
              <DensityStandardIcon/>
              Standard
            </MenuItem>
            <MenuItem aria-label="comfortable"
                      onClick={this.handleDensityChange}>
              <DensityComfortableIcon/>
              Comfortable
            </MenuItem>
          </Menu>
          <Dialog
              open={this.state.deleteAllPromptOpen}
              keepMounted
              onClose={this.handleDeleteAllPrompt}
              aria-describedby="delete all prompt"
              fullWidth={true}
              maxWidth={'sm'}
          >
            <DialogTitle>{`Delete ${pluralSelection ?
                'files' :
                'file'} permanently?`}</DialogTitle>
            <DialogContent>
              <DialogContentText id="delete all description">
                Your {pluralSelection ? 'files' : 'file'} will be deleted
                permanently and cannot be
                recovered.<br/>
                Do you want to proceed?
              </DialogContentText>
            </DialogContent>
            <DialogActions>
              <Button variant={'contained'}
                      onClick={this.handleDeleteAllPrompt}>Cancel</Button>
              <Button id={'button_proceed_delete'}
                      onClick={this.handleDeleteAllPrompt}>Delete</Button>
            </DialogActions>
          </Dialog>
          <Dialog
              open={renamePromptOpen}
              keepMounted
              onClose={this.handleRenamePrompt}
              aria-describedby="rename prompt"
              fullWidth={true}
              maxWidth={'sm'}
          >
            <DialogTitle>{`Rename ${onlySelectedId}`}</DialogTitle>
            <DialogContent>
              <TextField
                  autoFocus={true}
                  margin={'dense'}
                  id={'rename-newname'}
                  label={'New file name'}
                  fullWidth={true}
                  variant={'standard'}
              />
            </DialogContent>
            <DialogActions>
              <Button onClick={this.handleRenamePrompt}>Cancel</Button>
              <Button id={'button-rename-proceed'}
                      onClick={this.handleRenamePrompt}>Rename</Button>
            </DialogActions>
          </Dialog>
        </>);
  }
}




