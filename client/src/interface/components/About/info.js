/*
 * Copyright (c) 2022-2023 iCtrl Developers
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

export const introduction = `iCtrl is a web-based remote-control application, 
which supports Virtual Network Console (VNC) connections with a graphical 
interface and audio, Secure Shell (SSH) connections with a terminal 
interface, changing machines with workload detection, file management over SFTP.  
The web version, designed with mobile accessibilities in mind, allows users to 
manage and access their own sessions in a browser. `;

export const disclaimer = <>
  <p>If you are using the desktop client, your SSH hosts and credentials are
    stored locally on which the computer you run the program.
    In the web service, hosts and credentials are stored in a database on our
    server. Although we always try to protect your information with honest
    efforts, we are not cyber security experts and cannot guarantee the program
    is 100% bug-free.
  </p>
  <p>
    Please do not use the desktop client on a public computer.
  </p>
  <p>
    We are not responsible for any unintended uses of our program, including but
    not limited to Academic Misconducts, loss of data when APIs are called
    with unofficial web clients, and any hacking behaviours that utilise the
    application.
    However, if you suspect there is any security vulnerability, you are more
    than welcome to email <a
      href={'mailto:support@ictrl.ca?cc=junhao@junhao.ca&subject=Bug%20Report&body=Hi%20there%2C%0D%0A%0D%0AI%20am%20writing%20this%20to%20report%20a%20bug%20in%20iCtrl.%0D%0A%0D%0ABug%20Title%3A%0D%0A%0D%0ADetails%3A%0D%0A%0D%0APlatform%20%5Bweb%2FWindows%2FMac%5D%3A%0D%0A%0D%0AFrequency%20%5Bonce%2Foccasionally%2Falways%5D%3A%0D%0A%0D%0AHow%20to%20reproduce%3A%0D%0A%0D%0A'}>
    support@ictrl.ca</a> , and we will try our best to address such issues.
  </p>
</>;

export const supervisors = [
  {
    name: 'Timorabadi, Hamid',
    url: 'https://www.ece.utoronto.ca/people/timorabadi-h/',
    desc: `University of Toronto Electrical & Computer Engineering capstone project supervisor. `,
  },
];

export const specialThanks = [
  {
    name: 'Betz, Vaughn',
    url: 'https://www.eecg.utoronto.ca/~vaughn/',
    desc: `Extensive support for the application's integration into course 
    "ECE297 - Software Design & Communication" at University of Toronto. `,
  },
  {
    name: 'Phang, Khoman',
    url: 'https://www.eecg.utoronto.ca/~kphang/',
    desc: `University of Toronto Electrical & Computer Engineering capstone project administrator. `,
  },
  {
    name: 'Richard Junjie Shen',
    url: 'https://www.linkedin.com/in/junjie-shen-38a450210/',
    desc: `Icon designer. `,
  },
];

export const authors = [
  {
    name: 'Junhao Liao',
    url: 'https://junhao.ca',
    pic: 'https://junhao.ca/wp-content/uploads/2020/10/portrait-edited-768x768.jpeg',
    desc: <>
      <div>Qualcomm Canada Ulc. - Automotive SW Engineer</div>
      <div>University of Toronto - ECE 2T1 + PEY</div>
      </>,
  },
  {
    name: 'Leo HC Li',
    url: 'http://me.leo6leo.cool',
    pic: '/profile-pics/leo-pic.webp',
    desc: 'University of Toronto - ECE 2T4 + PEY',
  },
  {
    name: 'Jiaxing Li',
    url: 'https://www.linkedin.com/in/jiaxing-leo-li/',
    pic: '/profile-pics/jiaxing-pic.webp',
    desc: 'University of Toronto - ECE 2T1 + PEY',
  },
  {
    name: 'Yizhong Xu',
    url: 'https://www.linkedin.com/in/yizhong-xu-076bb9157/',
    pic: '/profile-pics/yizhong-pic.webp',
    desc: 'University of Toronto - ECE 2T1 + PEY',
  },
  {
    name: 'Haoran Zhang',
    url: 'https://www.linkedin.com/in/haoran-zhang-424b33196/',
    pic: '/profile-pics/haoran-pic.webp',
    desc: 'University of Toronto - ECE 2T1 + PEY',
  },
];

export const projects = [
  {
    name: 'Paramiko',
    url: 'https://www.paramiko.org/',
  },
  {
    name: 'noVNC',
    url: 'https://github.com/novnc/noVNC',
  },
  {
    name: 'simple-websocket-server',
    url: 'https://github.com/junhaoliao/simple-websocket-server',
    url2: 'https://github.com/dpallot/simple-websocket-server',
  },
  {
    name: 'Websockify',
    url: 'https://github.com/novnc/websockify',
    url2: 'https://github.com/novnc/websockify-other',
  },
  {
    name: 'Flask',
    url: 'https://flask.palletsprojects.com/',
  },
  {
    name: 'Flask-SQLAlchemy',
    url: 'https://flask-sqlalchemy.palletsprojects.com/',
  },
  {
    name: 'pyDes',
    url: 'https://pypi.org/project/pyDes/',
  },
  {
    name: 'PyInstaller',
    url: 'https://pyinstaller.readthedocs.io/',
  },
  {
    name: 'zipstream-new',
    url: 'https://github.com/arjan-s/python-zipstream',
  },
  {
    name: 'cachetools',
    url: 'https://github.com/tkem/cachetools/',
  },
  {
    name: 'Material UI',
    url: 'https://mui.com/',
  },
  {
    name: 'Axios',
    url: 'https://axios-http.com/',
  },
  {
    name: 'Xterm.js',
    url: 'https://xtermjs.org/',
  },
  {
    name: 'React Transition Group',
    url: 'https://reactcommunity.org/react-transition-group/',
  },
  {
    name: 'react-github-btn',
    url: 'https://buttons.github.io/',
  },
  {
    name: 'React.js',
    url: 'https://reactjs.org/',
  },
  {
    name: 'react-easy-marquee',
    url: 'https://github.com/jagnani73/react-easy-marquee',
  },
  {
    name: 'Electron',
    url: 'https://www.electronjs.org/',
  },
  {
    name: 'pako',
    url: 'http://nodeca.github.io/pako/',
  },
  {
    name: 'wcwidth',
    url: 'https://github.com/timoxley/wcwidth',
  },
  {
    name: 'DOM to Image',
    url: 'https://github.com/tsayen/dom-to-image',
  },
];
