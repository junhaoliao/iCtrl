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

import React from 'react';
import {
  Button,
  Chip,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  Divider,
  List,
  ListItem,
  ListItemAvatar,
  ListItemText,
  Typography,
} from '@mui/material';
import Marquee from 'react-easy-marquee';
import {
  authors,
  disclaimer,
  introduction,
  projects,
  specialThanks,
  supervisors,
} from './info';
import Avatar from '@mui/material/Avatar';
import LinkForNewWindow from '../LinkToNewWindow';

import iCtrlQRCode from './iCtrlQRCode.svg';
import './index.css';
import ICtrlVoiceButton from '../iCtrlVoiceButton/iCtrlVoiceButton';

const AboutSection = (props) => (
    <>
      <Divider>
        <Chip label={<b>{props.title}</b>} variant={'outlined'}
              size={'small'}/>
      </Divider>
      <List className={'selectable'}>
        {props.list.map((i) => (<ListItem key={i.name}>
          {i.pic && <ListItemAvatar>
            <Avatar>
              <img width={'100%'} src={i.pic}
                   alt={`${i.name} Profile`}/>
            </Avatar>
          </ListItemAvatar>}
          <ListItemText
              primary={i.name}
              secondary={<div>
                {i.reason && <Typography variant={'body2'}>
                  {i.reason}
                </Typography>}
                <LinkForNewWindow
                    url={i.url}>{i.url}</LinkForNewWindow>
              </div>
              }/>
        </ListItem>))}
      </List>
    </>
);

export default class About extends React.Component {
  handleClose = (_) => {
    this.props.onClose();
  };

  render() {
    const version = window.require &&
        window.require('electron').ipcRenderer.sendSync('version');

    return <Dialog open={true} fullWidth={true} maxWidth={'md'}>
      <DialogTitle>
          About iCtrl {version && `(v${version})`} <ICtrlVoiceButton/>
      </DialogTitle>
      <DialogContent style={{maxHeight: '630px'}}>
        <div>
          <img width={85} src={iCtrlQRCode} alt={'ictrl-qr-code'}
               style={{
                 float: 'right',
                 marginLeft: '10px',
                 marginBottom: '10px',
               }}/>
          <p className={'about-section-container selectable'}>
            {introduction}
          </p>
        </div>

        <AboutSection title={'Authors'} list={authors}/>
        <AboutSection title={'Supervisor'} list={supervisors}/>
        <AboutSection title={'Special Thanks'} list={specialThanks}/>

        <Divider>
          <Chip label={<b>Open Source Projects</b>} variant={'outlined'}
                size={'small'}/>
        </Divider>
        <div className={'about-section-container'}>
          <Typography variant={'body2'}>
            Thanks to the following open source projects:
          </Typography>
          <Marquee axis={'Y'} height={'200px'} duration={projects.length * 1000}
                   reverse={true}
                   pauseOnHover={true}>
            <List>
              {projects.map((p) => (<p key={p.name}>
                <b>{p.name}</b>
                <br/>
                <LinkForNewWindow url={p.url}>{p.url}</LinkForNewWindow>
                {p.url2 && <br/>}
                {p.url2 &&
                    <LinkForNewWindow url={p.url2}>{p.url2}</LinkForNewWindow>}
              </p>))}
            </List>
          </Marquee>
        </div>

        <Divider>
          <Chip label={<b>Disclaimer</b>} variant={'outlined'} size={'small'}/>
        </Divider>
        <div className={'about-section-container'}>
          {disclaimer}
        </div>
      </DialogContent>

      <DialogActions>
        <Button onClick={this.handleClose}>
          Close
        </Button>
      </DialogActions>
    </Dialog>;
  }
}