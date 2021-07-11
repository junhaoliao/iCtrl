import React from 'react';
import Button from '@material-ui/core/Button';
import TextField from '@material-ui/core/TextField';
import {Box, Dialog, DialogActions, Divider, Typography} from '@material-ui/core';
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
                onClose={this.handleClose}
                fullWidth={true}
                maxWidth={'xs'}
                aria-labelledby="new session"
            >
                <div className={'new-session-content-wrapper'}>
                    <Typography flexGrow={1} variant={'h4'}>Create New Session</Typography>
                    <Divider/>
                    <Box display={'flex'}>
                        <Typography flexGrow={1} variant={'h6'}>Host*</Typography>
                        <TextField style={{width: 240}} size={'small'} autoComplete={'off'} id="host"
                                   placeholder={'example.com'}
                                   variant="standard"/>
                    </Box>
                    <Box display={'flex'}>
                        <Typography flexGrow={1} variant={'h6'}>Username*</Typography>
                        <TextField style={{width: 240}} size={'small'} autoComplete={'off'} id="username"
                                   placeholder={'username'}
                                   variant="standard"/>
                    </Box>
                    <Box display={'flex'}>
                        <Typography flexGrow={1} variant={'h6'}>Password</Typography>
                        <TextField type={'password'} style={{width: 240}} size={'small'} autoComplete={'off'}
                                   id="password"
                                   placeholder={'****'}
                                   variant="standard"/>
                    </Box>
                    <DialogActions>
                        <Button onClick={this.handleClose}>Close</Button>
                        <Button variant={'contained'}
                                id={'button_save'}
                                onClick={this.handleClose}>
                            Save
                        </Button>
                    </DialogActions>
                </div>


            </Dialog>
        );
    }
}