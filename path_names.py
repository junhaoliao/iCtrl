import sys
import os

REFRESH_BUTTON_ICON_PATH = "Gnome-view-refresh-20x20.png"
PROFILE_FILE_PATH = "profile.json"
VNC_PASSWD_PATH = "passwd"
VNC_VIEWER_PATH_WIN64 = "vncviewer64.exe"
if getattr(sys, 'frozen', False):
    REFRESH_BUTTON_ICON_PATH = os.path.join(sys._MEIPASS, REFRESH_BUTTON_ICON_PATH)

    app_path = os.path.dirname(sys.executable)

    # redirect stdout if enabled
    stdout_path = os.path.join(app_path, "stdout.log")
    if os.path.isfile(stdout_path):
        sys.stdout = open(stdout_path, 'w')

    # redirect stderr if enabled
    stderr_path = os.path.join(app_path, "stderr.log")
    if os.path.isfile(stderr_path):
        sys.stderr = open(stderr_path, 'w')

    VNC_VIEWER_PATH_WIN64 = os.path.join(app_path, VNC_VIEWER_PATH_WIN64)
    PROFILE_FILE_PATH = os.path.join(app_path, PROFILE_FILE_PATH)
    VNC_PASSWD_PATH = os.path.join(app_path, VNC_PASSWD_PATH)
