# iCtrl

**SSH Remote Web Service / Desktop Client** (Previously known as **UG_Remote**)


[![Download Stats](https://img.shields.io/github/downloads/junhaoliao/iCtrl/total)]()

## Build Status
| Platform | Status |
| --- | --- |
| Web | [![Build Status](https://jenkins.junhao.ca/buildStatus/icon?job=iCtrl)](https://jenkins.junhao.ca/job/iCtrl/) |

## Disclaimer
If you are using the desktop client, your SSH hosts and credentials will be stored locally on the computer you run the program with. 
In the web service, we store the hosts and credentials in a database on our server. 
Although we have been trying to protect your information with honest efforts, we are not cyber security experts and cannot guarantee the program is 100% bug-free. 

Please do not use the program on a public computer. 
We are not responsible for any unintended use of our program, including but not limited to Academic Misconduct, loss of data when the APIs are called with unofficial web clients, and any hacking behaviour that utilises our tool. However, if you suspect there is any security vulnerability, you are more than welcome to email support@ictrl.ca , and we will try our best to address such issues. 

## Demo Screenshots
<table>
  <tr>
    <th colspan="2">Features</th>
  </tr>
  <tr>
    <td>Dashboard</td>
    <td>File Manager via SFTP</td>
  </tr>
  <tr>
    <td>Graphical Remote via VNC</td>
    <td>Terminal Console via SSH</td>
  </tr>
</table>

![image](https://user-images.githubusercontent.com/43196707/201545822-0782c64d-fbac-4286-9af8-1cd5af3c30a5.png)

## Instructions
The tool is provided in two variants: a web service and a desktop client. You can pick from one of the below options to best suit your need.

### Option I. Desktop Client
1. Go to https://ictrl.ca
2. Download the desktop client for your platform (Mac or Windows)
3. i. On a Mac computer, you can open the DMG file and drag the app into the "Application" folder. Then you can find the installed app in LaunchPad or "Applications" in Finder. \
   ii. On a Windows computer, the installer download might be blocked. Check your browser settings and click on "Keep Anyways" to download the installer. Once the download is finished, double click on the installer, and the app will be installed in your user directory. You can find the installed app in the Start Menu. 

### Option II. Web Service (Not available as of Sepetemeber 30, 2023)
1. Go to https://ictrl.ca
2. Under the "Sign Up" tab, register an account with Uoft email
3. Verify your account by checking your [Uoft email inbox](https://mail.utoronto.ca)
4. Log in with your credentials

Now you can add a new session by clicking the "+" (Plus) button in the upper right corner of the opened app window. 

## Special thanks to ...
- The following open-source libraries
   - **Paramiko**: https://www.paramiko.org/
   - **NoVNC**: https://github.com/novnc/noVNC
   - **Websockify**: https://github.com/novnc/websockify-other and https://github.com/novnc/websockify
   - **simple-websocket-server**: https://github.com/junhaoliao/simple-websocket-server \
     previously maintained at: https://github.com/dpallot/simple-websocket-server (no longer active)
   - **Material UI**: https://mui.com/
- **Richard Junjie Shen**, a graduated Uoft Architecture undergraduate student, who designed the logo

## Contributors
### Since 2019
- [@junhaoliao](https://www.github.com/junhaoliao) Junhao Liao
### Since 2021
- [@Kruz-X](https://www.github.com/Kruz-X) Kruzer Yizhong Xu
- [@KevinHaoranZhang](https://www.github.com/KevinHaoranZhang) Kevin Haoran Zhang
- [@leojiaxingli](https://www.github.com/leojiaxingli) Leo Jiaxing Li
### Since 2023
- [@Leo6Leo](https://www.github.com/Leo6Leo) Leo Haocheng Li
### Since 2024
- [@xx12345798](https://www.github.com/xx12345798) Xuan Xu
- [@li-ruihao](https://www.github.com/li-ruihao) Ruihao Li
- [@IreneLime](https://www.github.com/IreneLime) Irene Li
- [@Nuovaxu](https://www.github.com/Nuovaxu) Nuova Nuo Xu

## Docs
 - [Deployment](https://github.com/junhaoliao/iCtrl/blob/main/docs/deployment.md)
