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
import Button from '@mui/material/Button';
import {
  Box,
  Checkbox,
  Dialog,
  DialogActions,
  DialogTitle,
  FormControlLabel,
  Switch,
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableRow,
  TextField,
  Tooltip,
} from '@mui/material';

import './index.css';
import {PERMISSION_BITS} from '../../pages/FileManager/constants';
import {isDir} from '../../pages/FileManager/utils';
import {sftp_chmod} from '../../../actions/sftp';

export default class ChangePermission extends React.Component {
  constructor(props) {
    super(props);
    this.cwd = null;
    this.state = {
      name: null,
      mode: null,
      modeCheck: null,
      modeInput: null,
      applyRecursively: false,
    };
  }

  handleSubmit() {
    sftp_chmod(
        this.props.fm,
        this.cwd,
        this.state.name,
        this.state.mode & 0o777,
        this.state.applyRecursively);
  }

  handleClose = (ev) => {
    if (ev.target && ev.target.id === 'button_apply') {
      this.handleSubmit();
    }

    this.props.fm.setState({
      changePermissionOpen: false,
    });
  };

  handleModeChange = (ev) => {
    const bit = parseInt(ev.target.name);
    this.setState({
      mode: this.state.mode ^ bit,
      modeCheck: this.state.modeCheck ^ bit,
      modeInput: (this.state.modeCheck ^ bit).toString(8).padStart(3, '0'),
    });
  };

  handleModeInputChange = (ev) => {
    const value = ev.target.value;
    if (value.length > 3) {
      return;
    }
    if (value.length !== 0 && !/^[0-7]+$/.test(value)) {
      return;
    }
    this.setState({
      modeInput: value,
      modeCheck: parseInt(value.padEnd(3, '0'), 8),
    });
  };
  handleModeInputBlur = (_) => {
    if (this.state.modeInput.length !== 3) {
      this.setState({
        modeCheck: (this.state.mode & 0o777),
        modeInput: (this.state.mode & 0o777).toString(8).padStart(3, '0'),
      });
    } else {
      this.setState({
        mode: (this.state.mode & 0xfe00) | this.state.modeCheck,
      });
    }
  };
  updateRef = (_cwd, _name, _mode) => {
    this.cwd = _cwd;
    this.setState({
      name: _name,
      mode: _mode,
      modeCheck: (_mode & 0o777),
      modeInput: (_mode & 0o777).toString(8).padStart(3, '0'),
    });
  };

  render() {
    const {open} = this.props;
    if (!open) {
      return null;
    }

    const {name, mode, modeCheck, modeInput, applyRecursively} = this.state;
    const entryIsDir = isDir(mode);

    const rows_list = [];
    for (let i = 0; i < 3; i++) {
      const who = ['Owner', 'Group', 'Others'][i];
      const row = [
        <TableCell key={who}><Box fontWeight={'bold'}>{who}</Box></TableCell>];

      for (let j = 0; j < 3; j++) {
        const op = ['read', 'write', 'execute'][j];
        const index = i * 3 + j;
        const bit = PERMISSION_BITS[index];
        row.push(<TableCell key={String(bit)} align={'center'}>
          <Tooltip
              placement={'top-start'}
              title={`If set, the ${who} can ${op} on the ${entryIsDir ?
                  'directory' :
                  'file'}`}>
            <Checkbox
                name={String(bit)}
                onChange={this.handleModeChange}
                checked={Boolean(modeCheck & bit)}/>
          </Tooltip>
        </TableCell>);
      }
      rows_list.push(
          <TableRow key={`row_${i}`}>
            {row}
          </TableRow>,
      );
    }

    return (
        <Dialog
            open={open}
            fullWidth={true}
            maxWidth={'xs'}
            aria-labelledby="change permission"
        >
          <DialogTitle>{name} - Permissions</DialogTitle>
          <div className={'change-permission-content-wrapper'}>
            <Box display={'flex'}>
              <Box flexGrow={1}
                   fontWeight={'bold'}
                   alignSelf={'center'}>
                Unix Permission
              </Box>
              <TextField
                  title={'Unix Permissions'}
                  size={'small'}
                  onChange={this.handleModeInputChange}
                  onBlur={this.handleModeInputBlur}
                  value={modeInput}
              />
            </Box>
            <br/>
            <Table size={'small'}>
              <TableHead>
                <TableRow>
                  <TableCell/>
                  <TableCell align={'center'}><Box
                      fontWeight={'bold'}>Read</Box></TableCell>
                  <TableCell align={'center'}><Box
                      fontWeight={'bold'}>Write</Box></TableCell>
                  <TableCell align={'center'}><Box
                      fontWeight={'bold'}>Exec</Box></TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {rows_list}
              </TableBody>
            </Table>
            <br/>
            {entryIsDir &&
                <Tooltip
                    placement={'top-start'}
                    title={'Apply the permissions to the children in this directory as well'}>
                  <FormControlLabel
                      control={
                        <Switch
                            checked={applyRecursively}
                            color={'warning'}
                            onChange={() => {
                              this.setState(
                                  {applyRecursively: !this.state.applyRecursively});
                            }}
                        />
                      }
                      label="Apply changes recursively"/>
                </Tooltip>
            }
          </div>
          <DialogActions>
            <Button onClick={this.handleClose}>Close</Button>
            <Button variant={'contained'}
                    id={'button_apply'}
                    onClick={this.handleClose}>
              Apply
            </Button>
          </DialogActions>
        </Dialog>
    );
  }
}