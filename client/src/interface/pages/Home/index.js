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

import {
  Accordion,
  AccordionDetails,
  AccordionSummary,
  AppBar,
  Box,
  Button,
  Dialog,
  DialogActions,
  DialogContent,
  DialogContentText,
  DialogTitle,
  Divider,
  Hidden,
  IconButton,
  ToggleButton,
  ToggleButtonGroup,
  Toolbar,
  Tooltip,
  Typography,
} from '@mui/material';
import GitHubButton from 'react-github-btn';
import axios from 'axios';
import ictrlLogo from '../../../icons/logo.webp';
import LogIn from '../../components/LogIn';
import UAParser from 'ua-parser-js';

import About from '../../components/About';
import InfoIcon from '@mui/icons-material/Info';
import ICtrlVoiceButton
  from '../../components/iCtrlVoiceButton/iCtrlVoiceButton';
import {ExpandMore} from '@mui/icons-material';

const ElcanoIcon = (props) => (<img
        alt={'elcano-icon'}
        width={props.size || 32}
        height={props.size || 32}
        src={'http://elcano.ictrl.ca/favicon.ico'}
    />
);

export default class Home extends React.Component {
  constructor(props) {
    super(props);

    this.state = {
      windowsCount: 0,
      macIntelCount: 0,
      macARMCount: 0,
      totalDownloadCount: 0,
      publishDate: null,
      aboutOpened: false,
      detectedPlatform: null,
      postDownloadDialogOpen: false,
    };
  }

  handleDesktopDownload = (ev) => {
    const platform = ev.target.id;
    let download_link = 'https://github.com/junhaoliao/iCtrl/releases/latest/download/';
    if (platform === 'download-windows') {
      download_link += 'ictrl-desktop-setup.exe';
    } else if (platform === 'download-mac-intel') {
      download_link += 'ictrl-desktop-darwin-x64.dmg';
    } else if (platform === 'download-mac-arm') {
      download_link += 'ictrl-desktop-darwin-arm64.dmg';
    }
    window.location.href = download_link;
    this.setState({
      postDownloadDialogOpen: true,
    });
  };

  downloadCountString = (platform) => {
    const {publishDate, windowsCount, macIntelCount, macARMCount} = this.state;

    const [publishDateY, publishDateM, publishDateD] = [
      publishDate.getFullYear(),
      publishDate.getMonth() + 1, // zero-based : https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Date/getMonth
      publishDate.getDate(),
    ];

    let count;
    if (platform === 'Windows') {
      count = windowsCount;
    } else if (platform === 'Intel Mac') {
      count = macIntelCount;
    } else if (platform === 'ARM Mac') {
      count = macARMCount;
    } else {
      // all platforms
      count = windowsCount + macIntelCount + macARMCount;
    }

    return `${count} downloads on ${platform} since 
    ${publishDateY}-${publishDateM}-${publishDateD}`;
  };

  updatePlatformDownloadCount = () => {
    axios.get('https://api.github.com/repos/junhaoliao/iCtrl/releases/latest').
        then((response) => {
          const {assets, published_at} = response.data;

          let windowsCount = 0;
          let macIntelCount = 0;
          let macARMCount = 0;
          for (const asset of assets) {
            if (asset['name'].includes('exe') ||
                asset['name'].includes('nupkg')) {
              windowsCount += asset['download_count'];
            } else if (asset['name'].includes('x64')) {
              macIntelCount += asset['download_count'];
            } else if (asset['name'].includes('arm64')) {
              macARMCount += asset['download_count'];
            }
          }
          this.setState({
            windowsCount: windowsCount,
            macIntelCount: macIntelCount,
            macARMCount: macARMCount,
            publishDate: new Date(published_at),
          });
        });
  };

  updateTotalDownloadCount = () => {
    axios.get('https://api.github.com/repos/junhaoliao/iCtrl/releases').
        then((response) => {
          const {data} = response;
          let totalDownloadCount = 0;
          for (const release of data) {
            for (const asset of release['assets']) {
              // exclude those named "RELEASE" because the file
              //  is used for Windows auto-update
              if (asset['name'] !== 'RELEASES') {
                totalDownloadCount += asset['download_count'];
              }
            }
          }
          this.setState({
            totalDownloadCount: totalDownloadCount,
          });
        });
  };

  handleAboutOpen = () => {
    this.setState({
      aboutOpened: true,
    });
  };

  handleAboutClose = () => {
    this.setState({
      aboutOpened: false,
    });
  };

  componentDidMount() {
    axios.get('/api/userid').then(_ => {
      window.location = '/dashboard';
    }).catch(_ => {
      this.updatePlatformDownloadCount();
      this.updateTotalDownloadCount();
    });

    const osName = (new UAParser()).getOS().name;
    if (osName === 'Windows') {
      this.setState({detectedPlatform: 'windows'});
    } else if (osName === 'Mac OS') {
      // is mac, check whether is ARM by checking whether GPU vendor is Apple
      const canvas = document.createElement('canvas');
      const gl = canvas && canvas.getContext('webgl');
      const debuggerInfo = gl && gl.getExtension('WEBGL_debug_renderer_info');
      const renderer = debuggerInfo &&
          gl.getParameter(debuggerInfo.UNMASKED_RENDERER_WEBGL);
      if (renderer && renderer.match(/Apple/)) {
        if (!renderer.match(/Apple GPU/)) {
          // must be ARM
          this.setState({detectedPlatform: 'mac-arm'});
        } else {
          // cannot really tell whether it is ARM-based
          // because Safari tries to hide any platform-related info as of today
          console.log('Safari');
        }
      } else {
        this.setState({detectedPlatform: 'mac-intel'});
      }
    }
  }

  handlePostDownloadDialogClose = () => {
    this.setState({
      postDownloadDialogOpen: false,
    });
  };

  render() {
    const {
      publishDate,
      totalDownloadCount,
      aboutOpened,
      detectedPlatform,
      postDownloadDialogOpen,
    } = this.state;
    const showPublishCount = (publishDate !== null);

    return (
        <div style={{height: '100vh'}}>
          <AppBar position="absolute" color={'info'}>
            <Toolbar>
              <img src={ictrlLogo} style={{
                height: 30,
                width: 30,
                marginRight: 10,
              }}
                   alt="ictrl-logo"/>
              <Typography style={{flex: 1, fontWeight: 'bold'}} variant="h6">
                iCtrl
              </Typography>

              <Tooltip title="Magellan didn't circle the globe. Elcano did."
                       style={{marginRight: '6px'}}>
                <Button
                    sx={{padding: '2px', minWidth: 0, backgroundColor: 'white'}}
                    color={'inherit'}
                    variant={'contained'}
                    href={'http://elcano.ictrl.ca'}
                    target="_blank" rel={'noopener noreferrer'}
                    size={'large'}>
                  <ElcanoIcon/>
                </Button>
              </Tooltip>

              <Tooltip title="About iCtrl" style={{marginRight: '8px'}}>
                <IconButton onClick={this.handleAboutOpen} size={'large'}>
                  <InfoIcon style={{color: 'white'}} fontSize="large"/>
                </IconButton>
              </Tooltip>
              <GitHubButton href="https://github.com/junhaoliao/iCtrl"
                            data-size="large" data-show-count="true"
                            aria-label="Star junhaoliao/iCtrl on GitHub">Star</GitHubButton>
            </Toolbar>
          </AppBar>

          <Box sx={{display: 'flex', height: '100%'}}>
            <Hidden mdDown>
              <Box sx={{
                flex: 6,
                marginTop: '30px',
                alignSelf: 'center',
                alignItems: 'center',
              }}>
                <img style={{
                  display: 'block',
                  maxWidth: '200px',
                  marginLeft: 'auto',
                  marginRight: 'auto',
                }}
                     src={ictrlLogo} alt=""/>
                <br/>

                <div style={{marginLeft: '40px'}}>
                  <div style={{
                    display: 'flex',
                    justifyContent: 'center',
                    gap: '4px',
                  }}>
                    <Typography
                        sx={{fontWeight: '600'}}
                        variant={'h2'}>
                      iCtrl
                    </Typography>
                    <ICtrlVoiceButton/>
                  </div>
                </div>

                <br/>

                <Typography
                    align={'center'}
                    variant={'h5'}>
                  A Simple VNC + SSH Shell + SFTP Client
                </Typography>
                <br/>

                <div style={{display: 'flex', justifyContent: 'center'}}>
                  <Accordion style={{width: '30em'}}>
                    <AccordionSummary expandIcon={<ExpandMore/>}>
                      <Tooltip
                          sx={{flexGrow: 1}}
                          placement={'bottom-start'}
                          title={showPublishCount &&
                              this.downloadCountString('all platforms')}
                          PopperProps={{
                            modifiers: [
                              {
                                name: 'offset',
                                options: {
                                  offset: [12, -15],
                                },
                              },
                            ],
                          }}
                      >
                        <Typography>
                          1. Download Desktop Client
                        </Typography>
                      </Tooltip>
                      {(totalDownloadCount !== 0) && <Typography
                          sx={{marginRight: '8px', color: 'text.secondary'}}>
                        Total downloads: {totalDownloadCount}
                      </Typography>}
                    </AccordionSummary>
                    <AccordionDetails>
                      <ToggleButtonGroup color={'info'}
                                         size={'small'}
                                         fullWidth={true}
                                         value={detectedPlatform}>
                        {[
                          {
                            name: 'windows',
                            fullName: 'Windows',
                            placement: 'top-start',
                          }, {
                            name: 'mac-intel',
                            fullName: 'Intel Mac',
                            placement: 'top',
                          }, {
                            name: 'mac-arm',
                            fullName: 'ARM Mac',
                            placement: 'top-end',
                          }].map((p) => (
                            <Tooltip key={`download-count-tooltip-${p.name}`}
                                     value={p.name}
                                     title={showPublishCount &&
                                         this.downloadCountString(p.fullName)}
                                     placement={p.placement}
                                     PopperProps={{
                                       modifiers: [
                                         {
                                           name: 'offset',
                                           options: {
                                             offset: [0, -8],
                                           },
                                         },
                                       ],
                                     }}
                            >
                              <ToggleButton id={`download-${p.name}`}
                                            value={p.name}
                                            sx={{
                                              fontWeight: 'bold',
                                              color: 'rgb(40,40,40)',
                                            }}
                                            onClick={this.handleDesktopDownload}>
                                {p.fullName}
                              </ToggleButton>
                            </Tooltip>
                        ))}
                      </ToggleButtonGroup>
                    </AccordionDetails>
                  </Accordion>
                </div>

                <Typography align={'center'}
                            variant={'h6'}
                            sx={{color: 'text.secondary', marginTop: '5px'}}>
                  or
                </Typography>

                <Typography
                    align={'center'}
                    variant={'h6'}>
                  2. Use iCtrl online 👉
                </Typography>
              </Box>
            </Hidden>

            <Divider orientation="vertical" flexItem/>

            <Box sx={{flex: 3}}>
              {/* add an empty toolbar to prevent elements below being covered*/}
              {/*https://mui.com/components/app-bar/#fixed-placement*/}
              <Toolbar/>
              <LogIn/>
            </Box>
          </Box>

          {aboutOpened && <About onClose={this.handleAboutClose}/>}

          <Dialog
              open={postDownloadDialogOpen}
              onClose={this.handlePostDownloadDialogClose}
              aria-labelledby="post-download-dialog-title"
              aria-describedby="post-download-dialog-description"
          >
            <DialogTitle id="post-download-dialog-title">
              {'Thank you for downloading iCtrl! '}
            </DialogTitle>
            <DialogContent>
              <DialogContentText id="post-download-dialog-description">
                iCtrl is a free and open-source project.
                <br/>
                It will be great if you can support us with just a few clicks.
              </DialogContentText>
            </DialogContent>
            <DialogActions>
              <Tooltip title={'Magellan didn\'t circle the globe. Elcano did.'}>
                <Button
                    sx={{
                      height: '28px',
                      backgroundColor: 'rgb(50,62,102)',
                      '&:hover': {
                        backgroundColor: 'rgba(50,62,102,0.75)',
                      },
                      textTransform: 'none',
                    }}
                    variant={'contained'} size={'small'}
                    href={'http://elcano.ictrl.ca'}
                    target="_blank" rel={'noopener noreferrer'}
                    startIcon={<ElcanoIcon size={20}/>}
                >
                  Try Elcano
                </Button>
              </Tooltip>

              <div style={{marginLeft: '12px', height: '28px'}}>
                <GitHubButton href="https://github.com/junhaoliao/iCtrl"
                              data-size="large" data-show-count="true"
                              aria-label="Star junhaoliao/iCtrl on GitHub"
                              data-color-scheme="no-preference: light_high_contrast; light: light_high_contrast; dark: light_high_contrast;"
                >
                  Give us a star
                </GitHubButton>
              </div>
            </DialogActions>
          </Dialog>
        </div>
    );
  }
}


