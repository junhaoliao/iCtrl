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

const Link = (props) => (
    <a href={props.url} rel={'noreferrer'} target={'_blank'}
       style={{wordWrap: 'break-word'}}>
      {props.children}
    </a>);

export default class About extends React.Component {
  handleClose = (_) => {
    this.props.onClose();
  };

  render() {
    return <Dialog open={true} fullWidth={true} maxWidth={'md'}>
      <DialogTitle>About iCtrl</DialogTitle>
      <DialogContent style={{maxHeight: '630px'}}>
        <p className={'selectable'}>
          {introduction}
        </p>
        <Divider>
          <Chip label={<b>Supervisor</b>} variant={'outlined'} size={'small'}/>
        </Divider>
        <List>
          {supervisors.map((s) => (<ListItem key={s.name}>
            <ListItemText
                primary={s.name}
                secondary={<Link url={s.url}>{s.url}</Link>}/>
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
                secondary={<Link url={a.url}>{a.url}</Link>}/>
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
                     alt={`${a.name} Profile Picture`}/>
              </Avatar>
            </ListItemAvatar>
            <ListItemText
                primary={a.name}
                secondary={<Link url={a.url}>{a.url}</Link>}/>
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
              <Link url={p.url}>{p.url}</Link>
              {p.url2 && <br/>}
              {p.url2 && <Link url={p.url2}>{p.url2}</Link>}
            </p>))}
          </List>
        </Marquee>

        <Divider>
          <Chip label={<b>Disclaimer</b>} variant={'outlined'} size={'small'}/>
        </Divider>
        <p className={'selectable'}>
          {disclaimer}
        </p>
      </DialogContent>

      <DialogActions>
        <Button onClick={this.handleClose}>
          Close
        </Button>
      </DialogActions>
    </Dialog>;
  }
}