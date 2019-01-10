@echo off
TITLE 首次设置
color 30

:MENU
CLS
echo. ----------------------------------------

echo. 1. 全自动
echo. 2. 安装TightVNC
echo. 3. 生成自动连接文件
echo. 4. 退出
echo. ----------------------------------------

set choice=
set /p choice= 如果你啥都不知道就按1吧:
IF NOT "%Choice%"=="" SET Choice=%Choice:~0,1%
if /i "%choice%"=="1" goto AUTO
if /i "%choice%"=="2" goto INSTALL
if /i "%choice%"=="3" goto SETPASSWORD
if /i "%choice%"=="4" goto EXIT
echo.
goto MENU

:AUTO
start tightvnc-2.8.11-gpl-setup-64bit.msi
set "reply=y"
echo. 安装选项选“Complete”
echo. 会提示是否设置访问密码，建议不设置
set /p "reply=装好没? [y|n]: "
if /i not "%reply%" == "y" goto :eof

echo. 输入远程账户登录名
set /P userName=: 

echo. 输入ug账户密码，默认为学号
set /P realPassword=: 

echo. 设个远程连接的登录密码，最少6位数
set /P fakePassword=: 

echo. [在出现“Would you like to enter a view-only password (y/n)? n”后将窗口关闭]
echo. 将连接学校VNC服务器并自动初始化，按任意键开始

PAUSE >nul
set /a ranMachine=132+(%random%*49/32768)
kitty_portable.exe -ssh -L 5901:127.0.0.1:5901 %userName%@ug%ranMachine%.eecg.toronto.edu -pw %realPassword% -cmd "ece297vnc password\n\p\p\p\p%fakePassword%\n\p\p\p\p%fakePassword%\n\p\p\p\pn\n"

@echo @echo on > 隧道.bat
@echo set /a ranMachine=132+(%%random%%*49/32768) >> 隧道.bat
@echo kitty_portable.exe -ssh -L 5901:127.0.0.1:5901 %userName%@ug%%ranMachine%%.eecg.toronto.edu -pw %realPassword% -cmd "ece297vnc stop all \n \p \p  ece297vnc start" >> 隧道.bat

@echo start 隧道.bat > 远程连接.bat
@echo TIMEOUT 8 >> 远程连接.bat
@echo "C:\Program Files\TightVNC\tvnviewer.exe" 127.0.0.1:1 -password=%fakePassword% >> 远程连接.bat

echo. 初始化完成
echo. 双击“远程连接.bat”即可进行连接
echo. 按任意键返回主菜单
PAUSE >nul

goto MENU

:INSTALL
start tightvnc-2.8.11-gpl-setup-64bit.msi
set "reply=y"
set /p "reply=装好没? [y|n]: "
if /i not "%reply%" == "y" goto :eof
goto MENU

:SETPASSWORD

echo. 输入远程账户登录名
set /P userName=: 

echo. 输入ug账户密码，默认为学号
set /P realPassword=: 

echo. 设个远程连接的登录密码，最少6位数
set /P fakePassword=: 

echo. [在出现“Would you like to enter a view-only password (y/n)? n”后将窗口关闭]
echo. 将连接学校VNC服务器并自动初始化，按任意键开始

PAUSE >nul
set /a ranMachine=132+(%random%*49/32768)
kitty_portable.exe -ssh -L 5901:127.0.0.1:5901 %userName%@ug%ranMachine%.eecg.toronto.edu -pw %realPassword% -cmd "ece297vnc password\n\p\p\p\p%fakePassword%\n\p\p\p\p%fakePassword%\n\p\p\p\pn\n"

@echo @echo on > 隧道.bat
@echo set /a ranMachine=132+(%%random%%*49/32768) >> 隧道.bat
@echo kitty_portable.exe -ssh -L 5901:127.0.0.1:5901 %userName%@ug%%ranMachine%%.eecg.toronto.edu -pw %realPassword% -cmd "ece297vnc stop all \n \p \p  ece297vnc start" >> 隧道.bat

@echo start 隧道.bat > 远程连接.bat
@echo TIMEOUT 8 >> 远程连接.bat
@echo "C:\Program Files\TightVNC\tvnviewer.exe" 127.0.0.1:1 -password=%fakePassword% >> 远程连接.bat

echo. 初始化完成
echo. 双击“远程连接.bat”即可进行连接
echo. 按任意键返回主菜单
PAUSE >nul

goto MENU
:EXIT
exit