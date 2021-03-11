;UG_Remote Windows Installer
;Copyright (C) Junhao Liao 2020-2021 (https://junhao.ca)

;--------------------------------
;Include Modern UI

  !include "MUI2.nsh"

;--------------------------------
;Set Project Directory
  !define ProjectDir "..\.."

;--------------------------------
;General

  ;Name and file
  Name "UG_Remote"
  OutFile "UG_Remote.exe"
  Unicode True

  ;Set installer icon
  !define MUI_ICON "${ProjectDir}\packing\Windows\installer_icon.ico"

  ;Set compression method
  SetCompressor /SOLID lzma
  SetCompressorDictSize 64
  SetDatablockOptimize ON

  ;Default installation folder
  InstallDir "$PROGRAMFILES64\UG_Remote"
  
  ;Get installation folder from registry if available
  InstallDirRegKey HKCU "Software\UG_Remote" ""

  ;Request application privileges for Windows Vista
  RequestExecutionLevel admin
  
  ;Show installation details by default
  ShowInstDetails show
  
;--------------------------------
;Interface Configuration

  !define MUI_HEADERIMAGE
  !define MUI_HEADERIMAGE_BITMAP "${ProjectDir}\packing\Windows\installer_banner.bmp" ; optional
  !define MUI_WELCOMEFINISHPAGE_BITMAP "${ProjectDir}\packing\Windows\installer_finish_page.bmp" ; optional
  !define MUI_ABORTWARNING

;--------------------------------
;Pages

  !insertmacro MUI_PAGE_LICENSE "${ProjectDir}\docs\UG_Remote_Disclaimer.rtf"
  !insertmacro MUI_PAGE_LICENSE "${ProjectDir}\docs\TigerVNC_LICENCE.TXT"
  !insertmacro MUI_PAGE_COMPONENTS
  !insertmacro MUI_PAGE_DIRECTORY
  !insertmacro MUI_PAGE_INSTFILES
  ; finish page options
    !define MUI_FINISHPAGE_RUN
    !define MUI_FINISHPAGE_RUN_TEXT $(DESC_FINISH_PAGE_LAUNCH_APP)
    !define MUI_FINISHPAGE_RUN_FUNCTION LaunchUGRemote
    !define MUI_FINISHPAGE_SHOWREADME
    !define MUI_FINISHPAGE_SHOWREADME_TEXT $(DESC_FINISH_PAGE_CREATE_SHORTCUT)
    !define MUI_FINISHPAGE_SHOWREADME_FUNCTION CreateDesktopShortcut
  !insertmacro MUI_PAGE_FINISH

  !insertmacro MUI_UNPAGE_CONFIRM
  !insertmacro MUI_UNPAGE_INSTFILES

;--------------------------------
;Languages

  !insertmacro MUI_LANGUAGE "English"
  !insertmacro MUI_LANGUAGE "SimpChinese"

Function .onInit
	;Language selection dialog

  Push ""
	Push ${LANG_ENGLISH}
	Push English
	Push ${LANG_SIMPCHINESE}
	Push "Simplified Chinese"
  Push A ; A means auto count languages
	       ; for the auto count to work the first empty push (Push "") must remain
	LangDLL::LangDialog "Installer Language" "Please select the language of the installer"

	Pop $LANGUAGE
	StrCmp $LANGUAGE "cancel" 0 +2
		Abort
FunctionEnd

;--------------------------------
;Finish Page
LangString DESC_FINISH_PAGE_LAUNCH_APP ${LANG_ENGLISH} "Launch UG_Remote"
LangString DESC_FINISH_PAGE_CREATE_SHORTCUT ${LANG_ENGLISH} "Create Desktop Shortcut"
LangString DESC_UGRemote_SHORTCUT_DESCRIPTION ${LANG_ENGLISH} "Connect to UG Remote Machines under 5s"

LangString DESC_FINISH_PAGE_LAUNCH_APP ${LANG_SIMPCHINESE} "启动 UG_Remote"
LangString DESC_FINISH_PAGE_CREATE_SHORTCUT ${LANG_SIMPCHINESE} "创建桌面快捷方式"
LangString DESC_UGRemote_SHORTCUT_DESCRIPTION ${LANG_SIMPCHINESE} "5秒内连上UG远程机器"

Function LaunchUGRemote
  Exec "$INSTDIR\UG_Remote.exe"
FunctionEnd
Function CreateDesktopShortcut
  CreateShortCut "$DESKTOP\UG_Remote.lnk" "$INSTDIR\UG_Remote.exe" "" "$INSTDIR\icon.ico" 0 "" "" $(DESC_UGRemote_SHORTCUT_DESCRIPTION)
FunctionEnd

;--------------------------------
;Installer Sections

Section "UG_Remote" SecUGRemote

  SectionIn RO

  SetOutPath "$INSTDIR"
  
  File /r UG_Remote\*.*
  File /oname=icon.ico "${ProjectDir}\resources\icons\icon_white_bg.ico"
  File reset.bat

  ;Store installation folder
  WriteRegStr HKCU "Software\UG_Remote" "" $INSTDIR
  
  ;Create uninstaller
  WriteUninstaller "$INSTDIR\Uninstall.exe"

  ;Create StartMenu shortcuts
  CreateDirectory "$SMPROGRAMS\UG_Remote"
  CreateShortCut "$SMPROGRAMS\UG_Remote\UG_Remote.lnk" "$INSTDIR\UG_Remote.exe" "" "$INSTDIR\icon.ico" 0 "" "" $(DESC_UGRemote_SHORTCUT_DESCRIPTION)
  CreateShortCut "$SMPROGRAMS\UG_Remote\Reset UG_Remote Profile.lnk" "$INSTDIR\reset.bat"
SectionEnd

LangString DESC_TigerVNC_DOWNLOADING ${LANG_ENGLISH} "vncviewer64.exe Downloading..."
LangString DESC_TigerVNC_CONNECTING ${LANG_ENGLISH} "Connecting..."
LangString DESC_TigerVNC_SECOND ${LANG_ENGLISH} "second"
LangString DESC_TigerVNC_MINUTE ${LANG_ENGLISH} "minute"
LangString DESC_TigerVNC_HOUR ${LANG_ENGLISH} "hour"
LangString DESC_TigerVNC_PLURAL ${LANG_ENGLISH} "s"
LangString DESC_TigerVNC_PROGRESS ${LANG_ENGLISH} "%d.%01dkB/s" ;"%dkB (%d%%) of %dkB @ %d.%01dkB/s"
LangString DESC_TigerVNC_REMAINING ${LANG_ENGLISH} " (%d %s%s remaining)"
LangString DESC_TigerVNC_DOWNLOADFAILED ${LANG_ENGLISH} "TigerVNC Download Failed: "
LangString DESC_TigerVNC_DOWNLOAD_RETRY_PROMPT ${LANG_ENGLISH} "Retry?"
LangString DESC_TigerVNC_DOWNLOAD_REFUSED_RETRY ${LANG_ENGLISH} "User refused to retry downloading TigerVNC. Installtion aborted!!"

LangString DESC_TigerVNC_DOWNLOADING ${LANG_SIMPCHINESE} "vncviewer64.exe 下载中..."
LangString DESC_TigerVNC_CONNECTING ${LANG_SIMPCHINESE} "连接中..."
LangString DESC_TigerVNC_SECOND ${LANG_SIMPCHINESE} "秒"
LangString DESC_TigerVNC_MINUTE ${LANG_SIMPCHINESE} "分钟"
LangString DESC_TigerVNC_HOUR ${LANG_SIMPCHINESE} "小时"
LangString DESC_TigerVNC_PLURAL ${LANG_SIMPCHINESE} " "
LangString DESC_TigerVNC_PROGRESS ${LANG_SIMPCHINESE} "%d.%01dkB/s" ;"%dkB (%d%%) of %dkB @ %d.%01dkB/s"
LangString DESC_TigerVNC_REMAINING ${LANG_SIMPCHINESE} " (还需%d %s%s)"
LangString DESC_TigerVNC_DOWNLOADFAILED ${LANG_SIMPCHINESE} "TigerVNC 下载失败: "
LangString DESC_TigerVNC_DOWNLOAD_RETRY_PROMPT ${LANG_SIMPCHINESE} "重试?"
LangString DESC_TigerVNC_DOWNLOAD_REFUSED_RETRY ${LANG_SIMPCHINESE} "用户取消了TigerVNC下载。安装中断！！"

;!define TigerVNC_URL "https://junhao.ca/shared/cad2.7z" ; large file for testing only
;define TigerVNC_URL "null" ; non-existing file for testing only
!define TigerVNC_URL "https://bintray.com/tigervnc/stable/download_file?file_path=vncviewer64-1.11.0.exe"
!define TigerVNC_Filename "vncviewer64.exe"

Section "TigerVNC Viewer 1.11.0" SecTigerVNC

  SetOutPath "$INSTDIR"

  download_tigervnc:
  inetc::get /TRANSLATE "$(DESC_TigerVNC_DOWNLOADING)" "$(DESC_TigerVNC_CONNECTING)" \
       "$(DESC_TigerVNC_SECOND)" "$(DESC_TigerVNC_MINUTE)" "$(DESC_TigerVNC_HOUR)" "$(DESC_TigerVNC_PLURAL)" \
       "$(DESC_TigerVNC_PROGRESS)" "$(DESC_TigerVNC_REMAINING)" \
       "${TigerVNC_URL}" "${TigerVNC_Filename}" /END
    
  Pop $0
  StrCmp "$0" "OK" install_cont
  DetailPrint "$(DESC_TigerVNC_DOWNLOADFAILED) $0"
  MessageBox MB_RETRYCANCEL \
    "$(DESC_TigerVNC_DOWNLOADFAILED) $0. $(DESC_TigerVNC_DOWNLOAD_RETRY_PROMPT)"\
     IDRETRY download_tigervnc IDCANCEL
  DetailPrint "$(DESC_TigerVNC_DOWNLOAD_REFUSED_RETRY)"
  Abort

  install_cont:
  
SectionEnd

;--------------------------------
;Descriptions

  ;Language strings
  LangString DESC_SecUGRemote ${LANG_ENGLISH} "Install the UG_Remote Excuatble."
  LangString DESC_SecTigerVNC ${LANG_ENGLISH} "Automatically download the Official TigerVNC Viewer. $\n\
      A reliable network connection is required.$\n\
      You can also download it yourself, rename it to $\"vncviewer64.exe$\", \
      and place it under the installation directory. "
  LangString DESC_SecUGRemote ${LANG_SIMPCHINESE} "安装UG_Remote可执行文件。"
  LangString DESC_SecTigerVNC ${LANG_SIMPCHINESE} "自动下载官方TigerVNC Viewer。$\n\
      请确保网络连接稳定。$\n\
      你也可自行下载后重命名至$\"vncviewer64.exe$\"并放置于安装目录下。"

  ;Assign language strings to sections
  !insertmacro MUI_FUNCTION_DESCRIPTION_BEGIN
    !insertmacro MUI_DESCRIPTION_TEXT ${SecUGRemote} $(DESC_SecUGRemote)
    !insertmacro MUI_DESCRIPTION_TEXT ${SecTigerVNC} $(DESC_SecTigerVNC)
  !insertmacro MUI_FUNCTION_DESCRIPTION_END
 
;--------------------------------
;Uninstaller Section

Section "Uninstall"

  RMDir /r /REBOOTOK "$INSTDIR"

  ;remove shortcuts from the desktop and start menu
  Delete /REBOOTOK "$DESKTOP\UG_Remote.lnk"
  RMDir /r /REBOOTOK "$SMPROGRAMS\UG_Remote"

  DeleteRegKey HKCU "Software\UG_Remote"

SectionEnd