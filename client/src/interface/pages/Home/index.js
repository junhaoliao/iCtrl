import React from 'react';

import {
    AppBar,
    Toolbar,
    Typography,
    Button,
    Box, Divider, Hidden
} from '@material-ui/core';
import { Swiper, SwiperSlide } from 'swiper/react/swiper-react.js';
import 'swiper/swiper-bundle.css';

import axios from 'axios';
import ictrlLogo from '../../../icons/logo.png';
import backgroundImage from '../../../icons/McLaren.jpg';
import LogIn from '../../components/LogIn';

import './index.css';

let navbar, bgImage, loginBox, displayBox = null;

export default class Home extends React.Component {
    constructor(props) {
        super(props);
    }

    componentDidMount() {
        // listen for the scroll of page
        navbar = document.getElementById('nav-bar');
        bgImage = document.getElementById('bg-image');
        loginBox = document.getElementById('login-box');
        displayBox = document.getElementById('display-box');
        window.addEventListener('scroll', this.handleScreenScroll);

        axios.get('/api/userid')
            .then(response => {
                window.location = '/dashboard';
            })
            .catch(_ => {
                // do nothing for now
            });
    }

    componentWillUnmount() {
        window.removeEventListener('scroll', this.handleScreenScroll);
    }

    handleScreenScroll() {
        const scrollTop = window.pageYOffset;
        let opacity = scrollTop / 350;

        if (opacity > 0.5) {
            loginBox.style.pointerEvents = 'none';
        } else {
            loginBox.style.pointerEvents = 'auto';
        }

        if (opacity > 1) {
            opacity = 1;
        }

        navbar.style.backgroundColor = `rgba(0, 0, 0, ${opacity})`;
        bgImage.style.top = `${- scrollTop}px`;
        bgImage.style.transform = `translateZ(0) scale(${1 + 0.5 * opacity})`;
        loginBox.style.opacity = 1 - opacity;
        displayBox.style.marginRight = `${(1 - opacity) * 100}px`;
        displayBox.style.marginLeft = `${(1 - opacity) * 100}px`;
    }

    render() {
        return (
            <div position="relative">
                <AppBar position="static" color={'info'} class="nav-bar" id="nav-bar">
                    <Toolbar>
                        <img src={ictrlLogo} style={{background: 'transparent', height: 30, width: 30, marginRight: 10}}
                             alt=""/>
                        <Typography style={{flex: 1, fontWeight: 'bold', color: 'white'}} variant="h6">
                            iCtrl
                        </Typography>
                        <Button style={{color: 'white'}}>About</Button>
                    </Toolbar>
                </AppBar>
                
                <img src={backgroundImage} className="background-image" id="bg-image" />

                <div className="login-wrapper" id="login-box">
                    <LogIn/>
                </div>

                <div class="main-content" id="display-box">
                    {/* <Hidden mdDown>
                        <Box sx={{flex:5, alignSelf:'center', alignItems:'center'}}>
                            <img style={{display:'block', maxWidth: '240px', marginLeft:'auto', marginRight:'auto'}}
                            src={ictrlLogo} alt=""/>
                            <br/><br/>
                            <Typography
                                align={'center'}
                                variant={'h5'}>
                                Connect to uoft engineering labs in 5 seconds.
                            </Typography>
                        </Box>
                    </Hidden>

                    <Divider orientation="vertical" flexItem/> */}
                    <div className="title">Discover more about iCtrl</div>

                    <div className="swiper-wrapper">
                        <Swiper
                            spaceBetween={0}
                            slidesPerView={1}
                        >
                            <SwiperSlide>
                                <div className="single-swiper-container">
                                    Slide 1
                                </div>
                            </SwiperSlide>
                            
                            <SwiperSlide>
                                <div className="single-swiper-container">
                                    Slide 2
                                </div>
                            </SwiperSlide>

                            <SwiperSlide>
                                <div className="single-swiper-container">
                                    Slide 3
                                </div>
                            </SwiperSlide>

                            <SwiperSlide>
                                <div className="single-swiper-container">
                                    Slide 4
                                </div>
                            </SwiperSlide>
                        </Swiper>
                    </div>
                    
                    <div className="title">Start your adventure with iCtrl</div>

                </div>
                {/* <div>
                    Intro
                </div> */}
            </div>
        );
    }
}


