/* eslint-disable react-hooks/rules-of-hooks */
import React from 'react';
import Button from '@material-ui/core/Button';
import MenuItem from '@material-ui/core/MenuItem';
import TextField from '@material-ui/core/TextField';
import Dialog from '@material-ui/core/Dialog';
import axios from 'axios';

import './index.css';

const machineList = [ 'ug250', 'ug249' ];

export default class ChangeMachine extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            open: true,
        }
    }

    handleClickOpen() {
        this.setState({ open: true });
      };
    
    handleClose() {
        this.props.handleDone()
        this.setState({ open: false });
    };

    handleSave() {
        // to do
        const newMachine = document.getElementById('change-machine-selector').innerHTML;
        const { sessionId } = this.props;
        // console.log(newMachine, this.props.sessionId);
        axios.patch('/change_host', {
            session_id: sessionId, 
            new_host: `${newMachine}.eecg.toronto.edu`
        }).then(response => {
            console.log(response.data);
        }).catch(err => {
            console.log('error', err)
        })
        this.handleClose();
    }

    handleMachineChange(e) {
        // console.log('machine changed', e.target.value)
        document.getElementById('change-machine-selector').innerHTML = e.target.value;
    }

    render() {
        const { open } = this.state;
        return (
            <div className="change-machine-bg">
                <div className="change-machine-mask" />
                <div>
                    <Dialog
                        open={open}
                        onClose={() => this.handleClose()}
                        aria-labelledby="alert-dialog-title"
                        aria-describedby="alert-dialog-description"
                    >
                        <div className="change-machine-content-wrapper">
                            <TextField
                                id="change-machine-selector"
                                select
                                label="Select"
                                value={'ug250'}
                                onChange={(e) => this.handleMachineChange(e)}
                                helperText="Please select your machine"
                                style={{ width: '-webkit-fill-available' }}
                                >
                                {machineList.map((option) => (
                                    <MenuItem id="machine-name" key={option} value={option}>
                                    {option}
                                    </MenuItem>
                                ))}
                            </TextField>
                            <div className="change-machine-save">
                                <Button variant="contained" color="secondary" onClick={() => this.handleClose()}>Close</Button>
                                <Button style={{ marginLeft: 20 }} variant="contained" color="primary" onClick={() => this.handleSave()}>Change</Button>
                            </div>
                        </div>
                    </Dialog>
                </div>
            </div>
        )
    }
}