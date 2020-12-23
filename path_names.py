import platform
import sys
import os

REFRESH_BUTTON_ICON_PATH = "Gnome-view-refresh-20x20.png"
PROFILE_FILE_PATH = "profile.json"
VNC_PASSWD_PATH = "passwd"
VNC_VIEWER_PATH_WIN64 = "vncviewer64.exe"
VNC_VIEWER_PATH_MACOS = "TigerVNC.app/Contents/MacOS/TigerVNC Viewer"
APP_PATH = os.path.dirname(sys.executable)

if platform.system() == 'Windows':
    WIN_INSTALL_DIR_PATH = os.path.join(os.environ['ProgramFiles'], "UG_Remote")
    if WIN_INSTALL_DIR_PATH == APP_PATH:
        print("App installed at ProgramFiles, using LocalAppData for profile storage. ")
        WIN_LOCALAPPDATA_PATH = os.path.join(os.environ['LOCALAPPDATA'],"UG_Remote")
        if not os.path.exists(WIN_LOCALAPPDATA_PATH):
            os.mkdir(WIN_LOCALAPPDATA_PATH)
        PROFILE_FILE_PATH = os.path.join(WIN_LOCALAPPDATA_PATH, PROFILE_FILE_PATH)
        VNC_PASSWD_PATH = os.path.join(WIN_LOCALAPPDATA_PATH, VNC_PASSWD_PATH)

        # redirect stdout if enabled
        stdout_path = os.path.join(WIN_LOCALAPPDATA_PATH, "stdout.log")
        if os.path.isfile(stdout_path):
            sys.stdout = open(stdout_path, 'w')
        # redirect stderr if enabled
        stderr_path = os.path.join(WIN_LOCALAPPDATA_PATH, "stderr.log")
        if os.path.isfile(stderr_path):
            sys.stderr = open(stderr_path, 'w')

elif getattr(sys, 'frozen', False):  # standalone mode
    REFRESH_BUTTON_ICON_PATH = os.path.join(sys._MEIPASS, REFRESH_BUTTON_ICON_PATH)

    # redirect stdout if enabled
    stdout_path = os.path.join(APP_PATH, "stdout.log")
    if os.path.isfile(stdout_path):
        sys.stdout = open(stdout_path, 'w')

    # redirect stderr if enabled
    stderr_path = os.path.join(APP_PATH, "stderr.log")
    if os.path.isfile(stderr_path):
        sys.stderr = open(stderr_path, 'w')

    VNC_VIEWER_PATH_WIN64 = os.path.join(APP_PATH, VNC_VIEWER_PATH_WIN64)
    VNC_VIEWER_PATH_MACOS = os.path.join(APP_PATH, VNC_VIEWER_PATH_MACOS)

    PROFILE_FILE_PATH = os.path.join(APP_PATH, PROFILE_FILE_PATH)
    VNC_PASSWD_PATH = os.path.join(APP_PATH, VNC_PASSWD_PATH)

elif platform.system() == 'Darwin':
    VNC_VIEWER_PATH_MACOS = os.path.join("./", VNC_VIEWER_PATH_MACOS)