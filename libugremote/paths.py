import os
import platform
import shutil

# FIXME: use user directory
USER_PROFILE_PATH = "./profile/user_profile.json"
PRIVATE_KEYS_PATH = "./profile/keys/"
CONN_PROFILE_PATH = "./profile/connections/"

VNC_PASSWORD_PATH = "./profile/vncpasswds/"
try:
    shutil.rmtree(VNC_PASSWORD_PATH)
except FileNotFoundError:
    pass
os.mkdir(VNC_PASSWORD_PATH)

TIGER_VNC_VIEWER_PATH_WIN64 = ""
TIGER_VNC_VIEWER_PATH_MACOS = "/Applications/TigerVNC Viewer*.app"

REAL_VNC_VIEWER_PATH_WIN64 = ""
REAL_VNC_VIEWER_PATH_MACOS = "/Applications/VNC Viewer.app"

if platform.system() == "Darwin":  # Mac OS
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
