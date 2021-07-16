import React from 'react';
import Button from '@material-ui/core/Button';
import Checkbox from '@material-ui/core/Checkbox';
import FormGroup from '@material-ui/core/FormGroup';
import FormControlLabel from '@material-ui/core/FormControlLabel';
import {Box, Dialog, DialogActions, DialogTitle, Divider, Tooltip, Typography} from '@material-ui/core';
import axios from 'axios';

import './index.css';
import * as constants from '../../pages/FileManager/constants';

export default class ChangePermission extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            cwd: '',
            id: '',
            mode: 0,
            session_id: ''
        };
    }

    handleSubmit() {
        axios.patch(`/sftp_remode/${this.state.session_id}`, {
            cwd: this.state.cwd + "/" + this.state.id, 
            new_mode: this.state.mode
        }).then(response => {
            console.log(response.data);
            window.location.reload();
        }).catch(err => {
            console.log('error', err);
        });
    }

    handleClose = (ev) => {
        if (ev.target && ev.target.id === 'button_save') {
            this.handleSubmit();
        }
        this.props.onChangePermissionClose();
    };
    
    handleOnChange = (mode_bit) => {
        this.setState({mode: this.state.mode ^ mode_bit})
    }

    update_id_mode = (_cwd, _id, _mode, _session_id) => {
        this.setState({cwd: _cwd,
                       id: _id, 
                       mode: _mode,
                       session_id: _session_id})
    }

    render() {
        const {open} = this.props;
        return (
            <Dialog
                open={open}
                onClose={this.handleClose}
                fullWidth={true}
                maxWidth={'xs'}
                aria-labelledby="change permission"
            >
                <DialogTitle>Change Permission</DialogTitle>
                <DialogTitle>{this.state.id}</DialogTitle>
                <div className={'change-permission-content-wrapper'}>
                    <FormGroup row>
                        <Tooltip flexGrow={1} title={'Owner Permission'}>
                            <Typography variant={'subtitle1'}>Owner</Typography>
                        </Tooltip>
                        <FormControlLabel
                        control={
                            <Checkbox
                            checked={this.state.mode & constants.M_IROWR ? true : false}
                            onChange={(event) => {this.handleOnChange(constants.M_IROWR)}}
                            name="owner_read"
                            color="primary"
                            />
                        }
                        label="Read"
                        />
                        <FormControlLabel
                        control={
                            <Checkbox
                            checked={this.state.mode & constants.M_IWOWR ? true : false}
                            onChange={(event) => {this.handleOnChange(constants.M_IWOWR)}}
                            name="owner_write"
                            color="primary"
                            />
                        }
                        label="Write"
                        />
                        <FormControlLabel
                        control={
                            <Checkbox
                            checked={this.state.mode & constants.M_IXOWR ? true : false}
                            onChange={(event) => {this.handleOnChange(constants.M_IXOWR)}}
                            name="owner_execute"
                            color="primary"
                            />
                        }
                        label="Execute"
                        />
                        </FormGroup>
                        <FormGroup row>
                        <Tooltip flexGrow={1} title={'Group Permission'}>
                        <Typography variant={'subtitle1'}>Group</Typography>
                        </Tooltip>
                        <FormControlLabel
                        control={
                            <Checkbox
                            checked={this.state.mode & constants.M_IRGRP ? true : false}
                            onChange={(event) => {this.handleOnChange(constants.M_IRGRP)}}
                            name="group_read"
                            color="primary"
                            />
                        }
                        label="Read"
                        />
                        <FormControlLabel
                        control={
                            <Checkbox
                            checked={this.state.mode & constants.M_IWGRP ? true : false}
                            onChange={(event) => {this.handleOnChange(constants.M_IWGRP)}}
                            name="group_write"
                            color="primary"
                            />
                        }
                        label="Write"
                        />
                        <FormControlLabel
                        control={
                            <Checkbox
                            checked={this.state.mode & constants.M_IXGRP ? true : false}
                            onChange={(event) => {this.handleOnChange(constants.M_IXGRP)}}
                            name="group_execute"
                            color="primary"
                            />
                        }
                        label="Execute"
                        />
                        </FormGroup>
                        <FormGroup row>
                        <Tooltip flexGrow={1} title={'Others Permission'}>
                        <Typography variant={'subtitle1'}>Others</Typography>
                        </Tooltip>
                        <FormControlLabel
                        control={
                            <Checkbox
                            checked={this.state.mode & constants.M_IROTH ? true : false}
                            onChange={(event) => {this.handleOnChange(constants.M_IROTH)}}
                            name="others_read"
                            color="primary"
                            />
                        }
                        label="Read"
                        />
                        <FormControlLabel
                        control={
                            <Checkbox
                            checked={this.state.mode & constants.M_IWOTH ? true : false}
                            onChange={(event) => {this.handleOnChange(constants.M_IWOTH)}}
                            name="others_write"
                            color="primary"
                            />
                        }
                        label="Write"
                        />
                        <FormControlLabel
                        control={
                            <Checkbox
                            checked={this.state.mode & constants.M_IXOTH ? true : false}
                            onChange={(event) => {this.handleOnChange(constants.M_IXOTH)}}
                            name="others_execute"
                            color="primary"
                            />
                        }
                        label="Execute"
                        />
                    </FormGroup>
                </div>
                <DialogActions>
                    <Button onClick={this.handleClose}>Close</Button>
                    <Button variant={'contained'}
                            id={'button_save'}
                            onClick={this.handleClose}>
                        Save
                    </Button>
                </DialogActions>

            </Dialog>
        );
    }
}