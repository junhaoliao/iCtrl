import React from 'react';

import {GridToolbarContainer} from '@material-ui/data-grid';
import {
    Button,
    Dialog,
    DialogActions,
    DialogContent,
    DialogContentText,
    DialogTitle,
    IconButton,
    InputAdornment,
    Menu,
    MenuItem,
    OutlinedInput,
    Tooltip
} from '@material-ui/core';
import {ArrowUpward, Delete, GetApp, KeyboardArrowRight, Visibility, VisibilityOff} from '@material-ui/icons';

import {DensityComfortableIcon, DensityCompactIcon, DensityIcon, DensityStandardIcon} from '../../../icons';
import {sftp_dl, sftp_rm} from '../../../actions/sftp';

export default class CustomToolbar extends React.Component {
    constructor(props) {
        super(props);

        this.state = {
            densityMenuAnchorEl: null,
            deleteAllPromptOpen: false
        };
    }

    handleClose = (_) => {
        this.setState({
            densityMenuAnchorEl: null
        });
    };

    handleMenuOpen = (ev) => {
        this.setState({
            densityMenuAnchorEl: ev.currentTarget
        });
    };

    handleDensityChange = (ev) => {
        this.props.fm.setState({
            density: ev.currentTarget.getAttribute('aria-label')
        });
        this.setState({
            densityMenuAnchorEl: null
        });
    };

    handleHiddenFiles = (_) => {
        this.props.fm.showHidden = !this.props.fm.showHidden;
        this.props.fm.setState({
            filesDisplaying: this.props.fm.showHidden ? this.props.fm.files : this.props.fm.nonHiddenFiles(),
        });
    };

    handleDownload = (_) => {
        if (this.props.fm.selected.length === 0) {
            this.props.fm.showAlert('No files selected for download. ');
            return;
        }
        sftp_dl(this.props.fm.session_id, this.props.fm.state.cwd, this.props.fm.selected);
    };

    handleDeleteAllPrompt = (ev) => {
        if (ev.target.id !== 'button_proceed_delete') {
            this.setState({
                deleteAllPromptOpen: false
            });
            return;
        }
        sftp_rm(this.props.fm, this.props.fm.session_id, this.props.fm.state.cwd, this.props.fm.selected);
        this.setState({
            deleteAllPromptOpen: false
        });
    };

    handleDelete = (_) => {
        if (this.props.fm.selected.length === 0) {
            this.props.fm.showAlert('No files selected for removal.');
            return;
        }
        this.setState({
            deleteAllPromptOpen: true
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
            cwdInput: ev.target.value
        });
    };
    handleCwdInputBlur = (ev) => {
        if (ev.relatedTarget && ev.relatedTarget.id === 'enter_button') {
            return;
        }
        this.props.fm.setState({
            cwdInput: this.props.fm.state.cwd,
            cwdInputErr: null
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
        const pluralSelection = this.props.fm.selected.length > 1;
        return (<GridToolbarContainer>
            <Tooltip title={'Go to Parent Folder'}>
                <IconButton aria-label={'up'} onClick={this.handleUpOneLevel} color={'primary'}>
                    <ArrowUpward/>
                </IconButton>
            </Tooltip>

            <OutlinedInput
                fullWidth
                style={{height: 40}}
                autoComplete={'new-password'}
                onKeyPress={this.handleCwdInputKeyPress}
                onBlur={this.handleCwdInputBlur}
                onChange={this.handleCwdInputChange}
                value={this.props.fm.state.cwdInput}
                error={Boolean(this.props.fm.state.cwdInputErr)}
                endAdornment={
                    <InputAdornment position="end">
                        <IconButton color={'primary'} id={'enter_button'} edge={'end'}
                                    aria-label={'enter'}
                                    onClick={this.handleCwdSubmit}>
                            <KeyboardArrowRight/>
                        </IconButton>
                    </InputAdornment>
                }
                inputProps={{'aria-label': 'current-directory'}}/>

            <Tooltip title={'Density'}>
                <IconButton color={'primary'} onClick={this.handleMenuOpen}>
                    <DensityIcon/>
                </IconButton>
            </Tooltip>

            <Tooltip title={`${this.props.fm.showHidden ? 'Hide' : 'Show'} Hidden Files`}>
                <IconButton color={'primary'} onClick={this.handleHiddenFiles}>
                    {this.props.fm.showHidden ? <VisibilityOff/> : <Visibility/>}
                </IconButton>
            </Tooltip>

            <Tooltip title={'Delete'}>
                <IconButton color={'primary'} onClick={this.handleDelete}>
                    <Delete/>
                </IconButton>
            </Tooltip>

            <Tooltip title={'Download'}>
                <IconButton color={'primary'} onClick={this.handleDownload}>
                    <GetApp/>
                </IconButton>
            </Tooltip>

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
                <MenuItem aria-label="comfortable" onClick={this.handleDensityChange}>
                    <DensityComfortableIcon/>
                    Comfortable
                </MenuItem>
            </Menu>
            <Dialog
                open={this.state.deleteAllPromptOpen}
                keepMounted
                onClose={this.handleDeleteAllPrompt}
                aria-describedby="delete all alert"
                fullWidth={true}
                maxWidth={'sm'}
            >
                <DialogTitle>{`Delete ${pluralSelection ? 'files' : 'file'} permanently?`}</DialogTitle>
                <DialogContent>
                    <DialogContentText id="delete all description">
                        Your {pluralSelection ? 'files' : 'file'} will be deleted permanently and cannot be
                        recovered.<br/>
                        Do you want to proceed?
                    </DialogContentText>
                </DialogContent>
                <DialogActions>
                    <Button variant={'contained'} onClick={this.handleDeleteAllPrompt}>Cancel</Button>
                    <Button id={'button_proceed_delete'} onClick={this.handleDeleteAllPrompt}>Delete</Button>
                </DialogActions>
            </Dialog>
        </GridToolbarContainer>);
    }
}




