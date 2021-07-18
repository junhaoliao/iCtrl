import React from 'react';
import Button from '@material-ui/core/Button';
import TextField from '@material-ui/core/TextField';
import {Box, Dialog, DialogActions, DialogTitle, Divider, Tooltip, Typography} from '@material-ui/core';
import axios from 'axios';

import './index.css';

export default class NewSession extends React.Component {
    handleSubmit() {
        const host = document.getElementById('host').value;
        const username = document.getElementById('username').value;
        const password = document.getElementById('password').value;

        axios.post('/session', {
            host, username, password
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
        this.props.onAddNewSessionClose();
    };

    render() {
        const {open} = this.props;
        return (
            <Dialog
                open={open}
                fullWidth={true}
                maxWidth={'xs'}
                aria-labelledby="new session"
            >
                <DialogTitle>Create New Session</DialogTitle>

                <div className={'new-session-content-wrapper'}>
                    <Box display={'flex'}>
                        <Tooltip flexGrow={1} title={'[Required] host name of the target SSH server'}>
                            <Typography variant={'subtitle1'}>Host<span style={{color:'red'}}>*</span></Typography>
                        </Tooltip>
                        <TextField style={{width: 250}} size={'small'} autoComplete={'off'} id="host"
                                   placeholder={'example.com'}
                                   variant="standard"/>
                    </Box>
                    <Box display={'flex'}>
                        <Tooltip flexGrow={1} title={'[Required] username for login'}>
                            <Typography variant={'subtitle1'}>Username<span style={{color:'red'}}>*</span></Typography>
                        </Tooltip>
                        <TextField style={{width: 250}} size={'small'} autoComplete={'off'} id="username"
                                   placeholder={'username'}
                                   variant="standard"/>
                    </Box>
                    <Box display={'flex'}>
                        <Tooltip flexGrow={1} title={'[Optional] password for login'}>
                        <Typography variant={'subtitle1'}>Password</Typography>
                        </Tooltip>
                        <TextField type={'password'} style={{width: 250}} size={'small'} autoComplete={'off'}
                                   id="password"
                                   placeholder={'****'}
                                   variant="standard"/>
                    </Box>

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