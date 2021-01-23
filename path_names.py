import os
import platform
import sys

UG_REMOTE_ICON_PATH = "icon.png"

PROFILE_FILE_PATH = "profile.json"
VNC_PASSWD_PATH = "passwd"

TIGER_VNC_VIEWER_PATH_WIN64 = "vncviewer64.exe"
TIGER_VNC_VIEWER_PATH_MACOS = "/Applications/TigerVNC Viewer*.app"
REAL_VNC_VIEWER_PATH_WIN64 = ""
REAL_VNC_VIEWER_PATH_MACOS = "/Applications/VNC Viewer.app"

APP_PATH = os.path.dirname(sys.executable)

if getattr(sys, 'frozen', False):  # standalone mode
    # noinspection PyUnresolvedReferences
    UG_REMOTE_ICON_PATH = os.path.join(sys._MEIPASS, UG_REMOTE_ICON_PATH)

if platform.system() == "Windows":
    if not os.path.isfile(TIGER_VNC_VIEWER_PATH_WIN64):
        print("Could not find TigerVNC")
        TIGER_VNC_VIEWER_PATH_WIN64 = None
    if not os.path.isfile(REAL_VNC_VIEWER_PATH_WIN64):
        print("Could not find RealVNC")
        REAL_VNC_VIEWER_PATH_WIN64 = None

    WIN_INSTALL_DIR_PATH = os.path.join(os.environ['ProgramFiles'], "UG_Remote")
    if WIN_INSTALL_DIR_PATH == APP_PATH:
        print("App installed in ProgramFiles, using LocalAppData for profile storage. ")
        WIN_LOCALAPPDATA_PATH = os.path.join(os.environ['LOCALAPPDATA'], "UG_Remote")
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

elif platform.system() == "Darwin":  # Mac OS
    print("On Mac OS, using ~/.ug_remote for profile storage. ")

    MACOS_HOME_UG_REMOTE_DIR_PATH = os.path.join(os.path.expanduser("~"), ".ug_remote")
    if not os.path.exists(MACOS_HOME_UG_REMOTE_DIR_PATH):
        os.mkdir(MACOS_HOME_UG_REMOTE_DIR_PATH)

    PROFILE_FILE_PATH = os.path.join(MACOS_HOME_UG_REMOTE_DIR_PATH, PROFILE_FILE_PATH)
    VNC_PASSWD_PATH = os.path.join(MACOS_HOME_UG_REMOTE_DIR_PATH, VNC_PASSWD_PATH)

    import glob

    available_tigervnc_paths = glob.glob(TIGER_VNC_VIEWER_PATH_MACOS)
    if len(available_tigervnc_paths) == 0:
        TIGER_VNC_VIEWER_PATH_MACOS = None
    else:
        # replace " " with "\ " on Unix system paths
        TIGER_VNC_VIEWER_PATH_MACOS = available_tigervnc_paths[0].replace(" ", "\ ")

    # check whether RealVNC is installed
    if not os.path.exists(REAL_VNC_VIEWER_PATH_MACOS):
        REAL_VNC_VIEWER_PATH_MACOS = None
    else:
        # replace " " with "\ " on Unix system paths
        REAL_VNC_VIEWER_PATH_MACOS = REAL_VNC_VIEWER_PATH_MACOS.replace(" ", "\ ")

    # redirect stdout if enabled
    stdout_path = os.path.join(MACOS_HOME_UG_REMOTE_DIR_PATH, "stdout.log")
    if os.path.isfile(stdout_path):
        sys.stdout = open(stdout_path, 'w')
    # redirect stderr if enabled
    stderr_path = os.path.join(MACOS_HOME_UG_REMOTE_DIR_PATH, "stderr.log")
    if os.path.isfile(stderr_path):
        sys.stderr = open(stderr_path, 'w')
