import {GridToolbarContainer} from '@material-ui/data-grid';
import {Button, IconButton, InputAdornment, Menu, MenuItem, OutlinedInput} from '@material-ui/core';
import React from 'react';
import {GetApp, VisibilityOff} from '@material-ui/icons';
import ArrowUpwardIcon from '@material-ui/icons/ArrowUpward';
import KeyboardArrowRightIcon from '@material-ui/icons/KeyboardArrowRight';
import {DensityComfortableIcon, DensityCompactIcon, DensityStandardIcon} from '../../icons';
import PublishIcon from '@material-ui/icons/Publish';

export default class CustomToolbar extends React.Component {
    constructor(props) {
        super(props);
        this.fm = props.fm;

        this.state = {
            densityMenuAnchorEl: null
        };
    }


    handleClose = (ev) => {
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
        this.fm.setState({
            density: ev.currentTarget.getAttribute('aria-label')
        });
        this.setState({
            densityMenuAnchorEl: null
        });
    };

    handleHiddenFiles = (ev) => {
        this.fm.showHidden = !this.fm.showHidden;
        this.fm.setState({
            filesDisplaying: this.fm.showHidden ? this.fm.files : this.fm.nonHiddenFiles(),
        });
    };

    handleDownload = (ev) => {
        if (this.fm.selected.length === 0) {
            this.fm.showAlert('No files selected for download. ');
            return;
        }
        const url = `http://localhost:5000/sftp_dl/${this.fm.session_id}?` +
            `cwd=${this.fm.state.cwd}&` +
            `files=${JSON.stringify(this.fm.selected)}`;
        const a = document.createElement('a');
        a.download = '';
        a.href = url;
        a.click();
    };

    handleCwdSubmit = (ev) => {
        const path = this.fm.state.cwdInput;
        this.fm.loadDir(path);

        ev.preventDefault();
    };

    handleCwdInputChange = (ev) => {
        this.fm.setState({
            cwdInput: ev.target.value
        });
    };
    handleCwdInputBlur = (ev) => {
        if (ev.relatedTarget && ev.relatedTarget.id === 'enter_button') {
            return;
        }
        this.fm.setState({
            cwdInput: this.fm.state.cwd,
            cwdInputErr: null
        });
    };

    handleUpOneLevel = (ev) => {
        const cwd = this.fm.state.cwd;
        const path = cwd.substring(0, cwd.lastIndexOf('/'));
        if (path === '') {
            this.fm.loadDir('/');
        } else {
            this.fm.loadDir(path);
        }

    };

    render() {
        return (<GridToolbarContainer>
            <IconButton aria-label={'up'} onClick={this.handleUpOneLevel} color={'primary'}>
                <ArrowUpwardIcon/>
            </IconButton>
            <form onSubmit={this.handleCwdSubmit} autoComplete="off">
                <OutlinedInput style={{width: '30vw'}}
                               onBlur={this.handleCwdInputBlur} onChange={this.handleCwdInputChange}
                               value={this.fm.state.cwdInput}
                               error={Boolean(this.fm.state.cwdInputErr)}
                               endAdornment={
                                   <InputAdornment position="end">
                                       <IconButton color={'primary'} id={'enter_button'} edge={'end'}
                                                   aria-label={'enter'}
                                                   onClick={this.handleCwdSubmit}>
                                           <KeyboardArrowRightIcon/>
                                       </IconButton>
                                   </InputAdornment>
                               }
                               inputProps={{'aria-label': 'current-directory'}}/>
            </form>
            <Button color={'primary'} onClick={this.handleDownload}
                    startIcon={<GetApp/>}>
                Download
            </Button>
            <Button color={'primary'} onClick={this.handleDownload}
                    startIcon={<PublishIcon/>}>
                Upload
            </Button>
            <Button color={'primary'} onClick={() => {
                this.handleHiddenFiles();
            }}
                    startIcon={<VisibilityOff/>}>
                {this.fm.showHidden ? 'Hide' : 'Show'} Hidden Files
            </Button>
            <Button color={'primary'} aria-controls="density" aria-haspopup="true" onClick={this.handleMenuOpen}
                    startIcon={<svg style={{position: 'relative', top: -2}} className="MuiSvgIcon-root"
                                    focusable="false"
                                    aria-hidden="true">
                        <path d="M21,8H3V4h18V8z M21,10H3v4h18V10z M21,16H3v4h18V16z"/>
                    </svg>}>
                Density
            </Button>
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

        </GridToolbarContainer>);
    }
}




