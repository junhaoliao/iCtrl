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
  admins,
  authors,
  disclaimer,
  introduction,
  projects,
  supervisors,
} from './info';
import Avatar from '@mui/material/Avatar';
import LinkForNewWindow from '../LinkToNewWindow';

export default class About extends React.Component {
  handleClose = (_) => {
    this.props.onClose();
  };

  render() {
    return <Dialog open={true} fullWidth={true} maxWidth={'md'}>
      <DialogTitle>About iCtrl</DialogTitle>
      <DialogContent style={{maxHeight: '630px'}} className={'selectable'}>
        <p>
          {introduction}
        </p>
        <Divider>
          <Chip label={<b>Supervisor</b>} variant={'outlined'} size={'small'}/>
        </Divider>
        <List>
          {supervisors.map((s) => (<ListItem key={s.name}>
            <ListItemText
                primary={s.name}
                secondary={<LinkForNewWindow url={s.url}>{s.url}</LinkForNewWindow>}/>
          </ListItem>))}
        </List>

        <Divider>
          <Chip label={<b>Administrator</b>} variant={'outlined'}
                size={'small'}/>
        </Divider>
        <List>
          {admins.map((a) => (<ListItem key={a.name}>
            <ListItemText
                primary={a.name}
                secondary={<LinkForNewWindow url={a.url}>{a.url}</LinkForNewWindow>}/>
          </ListItem>))}
        </List>

        <Divider>
          <Chip label={<b>Authors - Team 2021320</b>} variant={'outlined'}
                size={'small'}/>
        </Divider>
        <List>
          {authors.map((a) => (<ListItem key={a.name}>
            <ListItemAvatar>
              <Avatar>
                <img width={'100%'} src={a.pic}
                     alt={`${a.name} Profile`}/>
              </Avatar>
            </ListItemAvatar>
            <ListItemText
                primary={a.name}
                secondary={<LinkForNewWindow url={a.url}>{a.url}</LinkForNewWindow>}/>
          </ListItem>))}
        </List>

        <Divider>
          <Chip label={<b>Open Source Projects</b>} variant={'outlined'}
                size={'small'}/>
        </Divider>
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
              {p.url2 && <LinkForNewWindow url={p.url2}>{p.url2}</LinkForNewWindow>}
            </p>))}
          </List>
        </Marquee>

        <Divider>
          <Chip label={<b>Disclaimer</b>} variant={'outlined'} size={'small'}/>
        </Divider>
        <div>
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