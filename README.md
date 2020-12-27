# UG_Remote
**UofT EECG/ECF Lab Remote for macOS / Windows**

Download the latest version here: https://github.com/junhaoliao/UG_Remote/releases

[中文读我见下方](https://github.com/junhaoliao/UG_Remote#中文-读我)

<img width=512 alt="UG_Remote_Demo" src="https://github.com/junhaoliao/UG_Remote/blob/main/demo/UG_Remote_demo.png?raw=true">

## Disclaimer
Your EECG/ECF lab remote password, together with your VNC password when applicable, will be obfuscated and stored locally. Please understand the risk and do not use it on any public computers. If you have any concerns, please email to junhao@junhao.ca or junhao.liao@mail.utoronto.ca

You are welcome to visit my personal website: https://junhao.ca

## Instructions (macOS) - 5 Steps
0. Download UG_Remote.5.x.x.dmg from the [**Releases**](https://github.com/junhaoliao/UG_Remote/releases) page and double-click to mount.
1. From the mounted disk, drag "UG_Remote.app" into your "Applications" directory.
2. Open the "De-Quarantine" workflow and click the upper-right "Run" button.
3. If you haven't installed TigerVNC, drag "TigerVNC Viewer x.x.app" into your "Applications" directory.
4. Open **Launchpad** or **Applications**, you can find the installed "UG_Remote.app". You may drag the app into your dock to create a shortcut. 

## Instructions (Windows) - 1 Step
If the "Windows protected your PC" window pops up, click on <ins>More Info</ins> -> [Run anyway] to allow the installer to run.

0. Download and extract UG_Remote_win64.5.x.x.zip from the **Releases** page. Double-click on "UG_Remote.exe".

## V5 Change Log
This script is updated to v5.0.2 on December 27, 2020
1. Added support for ECF

This script is updated to v5.0.1 on December 24, 2020
1. Added a "random port selection" feature
2. Redesigned user interface
3. Added installer for windows

This script is updated to v5.0.0 on December 19, 2020
1. Now we use Python. Goodbye C++. 

## This setup is possible thanks to the following free libraries/tools
1. TigerVNC: https://tigervnc.org/
2. Paramiko: http://www.paramiko.org/
3. PySimpleGUI: https://pysimplegui.readthedocs.io/

## Special Thanks to... 
- Richard Shen: Uoft Architect Undergraduate, helped make the icon with Adobe Illustrator for this project.
- Olivia Ziting Xu: Uoft Architect Undergraduate, helped with some Mac OS translations in the Chinese README.

# 中文 读我
前往Release页面获取最新版本：https://github.com/junhaoliao/UG_Remote/releases

## 声明
你的EECG/ECF密码，当适用时及VNC密码，将在混淆后本地存储。请明晰风险并不要在公共电脑上使用。如有疑问欢迎来邮junhao.liao@mail.utoronto.ca 或 junhao@junhao.ca

欢迎来我的个人网站逛逛：https://junhao.ca

## 使用说明 (MacOS) - 4 步
0. 从 [**Releases**](https://github.com/junhaoliao/UG_Remote/releases) 页面下载UG_Remote.5.x.x.dmg，双击以挂载。
1. 在挂载的镜像里，拖动"UG_Remote.app"到你的"Applications"/"应用程序" 目录
2. 打开"De-Quarantine"，点击右上角的"Run"/"运行"按钮
3. 打开**Launchpad**或**Applications**即可看见安装好的"UG_Remote.app"。你可以拖动应用到**Dock**/**坞**上以创建快捷方式。

## 使用说明 (Windows) - 1 步
0. 从**Releases**页面下载并解压UG_Remote_win64.5.x.x.zip。双击"UG_Remote.exe"。

## V5 版本说明
本脚本于2020年12月24日更新v5.0.1。
1. 新增ECF支持

本脚本于2020年12月24日更新v5.0.1。
1. 新增"随机选择端口"功能
2. 重新设计操作界面
3. 新增Windows安装器

本脚本于2020年12月19日更新v5.0.0。
1. 再见，C++。你好呀，Python。

## 在此感谢以下开源软件/库开发者
1. TigerVNC: https://tigervnc.org/
2. Paramiko: http://www.paramiko.org/
3. PySimpleGUI: https://pysimplegui.readthedocs.io/

## 特别感谢
- Richard Shen：多伦多大学建筑系本科，使用Adobe Illustrator制作了本脚本的图标。
- Olivia Ziting Xu：多伦多大学建筑系本科，协助了中文读我中有关Mac OS部分的翻译。
