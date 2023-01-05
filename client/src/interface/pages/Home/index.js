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
  ButtonGroup,
  Divider,
  Hidden,
  IconButton,
  Stack,
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
  };

  downloadCountString = (platform) => {
    const {publishDate, windowsCount, macIntelCount, macARMCount} = this.state;

    const [publishDateY, publishDateM, publishDateD] = [
      publishDate.getFullYear(),
      publishDate.getMonth() + 1, // zero-based : https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Date/getMonth
      publishDate.getDate(),
    ];

    let count = 0;
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
    axios.get('/api/userid').then(response => {
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

  render() {
    const {
      publishDate,
      totalDownloadCount,
      aboutOpened,
      detectedPlatform,
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
                       target="_blank" rel={'noopener noreferrer'}
                       style={{marginRight: '6px'}}>
                <Button
                    sx={{padding: '2px', minWidth: 0, backgroundColor: 'white'}}
                    color={'inherit'}
                    variant={'contained'}
                    href={'http://elcano.ictrl.ca'}
                    size={'large'}>
                  <img
                      alt={'elcano-icon'}
                      width={32}
                      height={32}
                      src={'http://elcano.ictrl.ca/favicon.ico'}
                  />
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
                          placement={'top'}
                          title={showPublishCount &&
                              this.downloadCountString('all platforms')}>
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
                      <Stack alignItems={'center'}>
                        <ButtonGroup color={'info'}>
                          {[
                            {
                              name: 'windows',
                              fullName: 'Windows',
                            }, {
                              name: 'mac-intel',
                              fullName: 'Intel Mac',
                            }, {
                              name: 'mac-arm',
                              fullName: 'ARM Mac',
                            }].map((p) => (
                              <Tooltip key={`download-count-tooltip-${p.name}`}
                                       title={showPublishCount &&
                                           this.downloadCountString(p.fullName)}
                                       placement={'top'}>
                                <Button id={`download-${p.name}`}
                                        variant={detectedPlatform === p.name ?
                                            'contained' :
                                            'outlined'}
                                        onClick={this.handleDesktopDownload}>
                                  {p.fullName}
                                </Button>
                              </Tooltip>
                          ))}
                        </ButtonGroup>
                      </Stack>
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
        </div>
    );
  }
}


