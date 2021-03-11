# UG_Remote

**UofT EECG/ECF Lab Remote for macOS / Windows**

[中文读我见下方](https://github.com/junhaoliao/UG_Remote#中文-读我)

Following the steps in "Instructions" below will install everything you need to connect to U of T Engineering Labs
through VNC, and connect with a simple GUI.

<img width=512 alt="UG_Remote_Demo" src="https://github.com/junhaoliao/UG_Remote/blob/main/demo/UG_Remote_demo.png?raw=true">

## Disclaimer

Your EECG/ECF lab remote password, together with your VNC password when applicable, will be obfuscated and stored
locally. Please understand the risk and do not use it on any public computers. If you have any concerns, please email to
junhao@junhao.ca or junhao.liao@mail.utoronto.ca

You are welcome to visit my personal website: https://junhao.ca

## Instructions (macOS) - 5 Steps

0. Download UG_Remote-5.x.x.dmg from the [**Releases**](https://github.com/junhaoliao/UG_Remote/releases) page and
   double-click to mount.
1. From the mounted disk, drag "UG_Remote.app" into your "Applications" directory.
2. Open the "De-Quarantine" workflow and click the upper-right "Run" button.
3. If you haven't installed TigerVNC, drag "TigerVNC Viewer x.x.app" into your "Applications" directory.
4. Open **Launchpad** or **Applications**, you can find the installed "UG_Remote.app". You may drag the app into your
   dock to create a shortcut.

## Instructions (Windows) - 1 Step

If the "Windows protected your PC" window pops up, click on <ins>More Info</ins> -> [Run anyway] to allow the installer
to run.

0. Download and extract UG_Remote_win64-5.x.x.zip from the **Releases** page. Double-click on "UG_Remote.exe".

## V5 Change Log
### [5.1.0] - 2021-03-11
1. Change app icon
2. Remove ug250 and ug251 from EECG recommended list
3. Fix a bug where incorrect buttons may show under the Misc tab
4. Ugrade Python toolchain to 3.9.2 and upgrade the libraries
5. Fix a bug in the udpater where it prompts for an update even if the major/minor version is greater than the API

### [5.0.8] - 2021-02-08
1. If user doesn't supply a machine number, randomly generate one
2. Remove lock files on the host to avoid "stale" servers
3. Disable the interface before everything is loaded up
4. Permit VNC password longer than 8 characters
5. Instead of only selecting the machine, "Connect" directly in "Check Loads"

### [5.0.7] - 2021-01-23
1. Added support for RealVNC: users can switch their viewer under Misc
2. Fixed a potential index-out-of-range exception in "check loads"
3. Fixed a bug that the ECF "Connect" button not loaded with ECF as the last lab


## This setup is possible thanks to the following free libraries/tools

1. TigerVNC: https://tigervnc.org/
2. Paramiko: http://www.paramiko.org/
3. PySimpleGUI: https://pysimplegui.readthedocs.io/

## Special Thanks to...

- Richard Shen: Uoft Architect Undergraduate, helped make the icon with Adobe Illustrator for this project.
- Olivia Ziting Xu: Uoft Architect Undergraduate, helped with some Mac OS translations in the Chinese README.

# 中文 读我

以下 "使用说明" 的步骤将安装远程VNC连接到多大工程系机房你所需的一切，并通过图形界面简易连接。

## 声明

你的EECG/ECF密码，当适用时及VNC密码，将在混淆后本地存储。请明晰风险并不要在公共电脑上使用。如有疑问欢迎来邮junhao.liao@mail.utoronto.ca 或 junhao@junhao.ca

欢迎来我的个人网站逛逛：https://junhao.ca

## 使用说明 (MacOS) - 4 步

0. 从 [**Releases**](https://github.com/junhaoliao/UG_Remote/releases) 页面下载UG_Remote-5.x.x.dmg，双击以挂载。
1. 在挂载的镜像里，拖动"UG_Remote.app"到你的 "应用程序" 目录
2. 打开"De-Quarantine"，点击右上角的 "运行" 按钮
3. 打开**启动台**或**应用程序**即可看见安装好的"UG_Remote.app"。你可以拖动应用到**坞**上以创建快捷方式。

## 使用说明 (Windows) - 1 步

0. 从**Releases**页面下载并解压UG_Remote_win64-5.x.x.zip。双击"UG_Remote.exe"。

## V5 版本说明
### [5.1.0] - 2021-03-11
1. 更改应用图标
2. 将 ug250 和 ug251 从 EECG 建议列表中移除
3. 修复了 Misc 选项卡下可能出现的错误按钮
4. 升级 Python 工具链至 3.9.2 以及更新若干库
5. 修复了升级器在主/次版本比API高时仍提醒升级的bug

### [5.0.8] - 2021-02-08
1. 如果用户没有选择机器号码，随机生成一个
2. 在主机上删除lock文件，以防服务器"stale"
3. 在所有东西加载出来前禁用界面
4. 允许多于8位的VNC密码
5. "检查负载"时，"Connect"而不是单单选中

### [5.0.7] - 2021-01-23
1. 新增RealVNC支持: 用户可在Misc选项卡下切换Viewer
2. 解决了"检查负载"中可能出现的 索引超出范围 异常
3. 解决了ECF "Connect"按钮不与ECF(作为上次连的lab)同时加载的问题


## 在此感谢以下开源软件/库开发者

1. TigerVNC: https://tigervnc.org/
2. Paramiko: http://www.paramiko.org/
3. PySimpleGUI: https://pysimplegui.readthedocs.io/

## 特别感谢

- Richard Shen：多伦多大学建筑系本科，使用Adobe Illustrator制作了本脚本的图标。
- Olivia Ziting Xu：多伦多大学建筑系本科，协助了中文读我中有关Mac OS部分的翻译。
