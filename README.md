
# UG_Remote
**UofT Engineering Undergraduate Lab Remote 多伦多大学工程系本科远程自动连接**

Scorll down to see the Chinese README.中文版在页面下方。

Check the "Release" page for the latest version: https://github.com/junhaoliao/UG_Remote/releases

## Disclaimer
Your remote password, will be stored locally in the folder where you initiate the script. Please understand the risk and do not use it on any public computers. If you have any concerns, please email to junhao@junhao.ca or junhao.liao@mail.utoronto.ca

You are also welcome to visit my personal website: https://junhao.ca

## Instructions
1. Double click on "UG_Remote.exe" to initiate the profile.
2. After the initialization, run "UG_Remote.exe" again to start a new connection.
3. If you are disconnected, you can choose to resume the last session also by "UG_Remote.exe". 

Microsoft Windows Only. Mac/Linux users please see https://github.com/Louis-He/ug_connection Credits to: @Louis-He
Support for Linux/Mac will be added (when I actually found my MacBook useful... Thumbs down for Apple not supporting Linux on their latest models).

## V4 Change Log
This scipt is updated to v4.1 on Decemeber 22, 2019.
1. Added icon for the executable. See "Sepcial Thanks to..." for more details.
2. Fixed a bug where establishing multiple VNC connections on a same machine can cause fatal errors, which is due to the enviroment of the lab machines.

This scipt is updated to v4 on Decemeber 21, 2019.
1. Ece297vnc method deprecated. Now etablish VNC connections directly by calling "vncserver" on the remote machine.
2. Port scaning tool to confirm the availability of selection. 
3. Password is now encryted. It is definitely safer than plain text.

## This setup is possible thanks to the following free libraries/tools
1. libssh – The SSH Library!: http://www.libssh.org/
2. JSON for Modern C++: https://nlohmann.github.io/json/
3. Crypto++: https://cryptopp.com/
4. TigerVNC: https://tigervnc.org/
5. KiTTY: http://www.9bis.net/kitty/
6. PSCP from PuTTY: https://www.chiark.greenend.org.uk/~sgtatham/putty/

## Sepcial Thanks to... 
Richard Shen from Uoft Architect helped make the icon with Adobe Illustrator for this project.

# 中文 读我
前往Release页面获取最新版本：https://github.com/junhaoliao/UG_Remote/releases

## 声明

你的密码将本地存储于你启用脚本的文件夹。请明晰风险并不要在公共电脑上使用。如有疑问欢迎来邮junhao.liao@mail.utoronto.ca 或 junhao@junhao.ca
欢迎来我的个人网站逛逛：https://junhao.ca

## 使用说明

1. 双击"UG_Remote.exe" 初始化。
2. 初始化完毕后，再次运行"UG_Remote.exe"以建立新连接。
3. 如果掉线了，可以运行"UG_Remote.exe"继续上次连接。

本脚本暂时只对Windows兼容，Mac/Linux 版本请见@Louis-He 的 https://github.com/Louis-He/ug_connection

日后将增加对Linux/Mac 支持（有空再说，MacBook已经吃灰了...新版Mac不支持Linux，必须给苹果差评）

## V4 版本说明
本脚本于2019年12月22日更新v4.1。
1. 为程序添加了图标。详见“特别感谢”。
2. 修复了一个严重错误：由于实验室环境的配置，当在同一台实验室机器上建立多个VNC连接时会严重出错。

本脚本于2019年12月21日更新v4。
1. 弃用学校给的ece297vnc。直接用 "vncserver" 在远程机器上建立VNC连接。
2. 新增端口扫描工具，轻松辨别端口是否可用。
3. 密码现在为加密保存，比原来的明文密码更为安全。

## 在此感谢以下开源软件开发者

1. libssh – The SSH Library!: http://www.libssh.org/
2. JSON for Modern C++: https://nlohmann.github.io/json/
3. Crypto++: https://cryptopp.com/
4. TigerVNC: https://tigervnc.org/
5. KiTTY: http://www.9bis.net/kitty/
6. PSCP from PuTTY: https://www.chiark.greenend.org.uk/~sgtatham/putty/

## 特别感谢
Richard Shen：多伦多大学建筑系，使用Adobe Illustrator制作了本脚本的图标。

