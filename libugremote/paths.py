import os
import platform
import shutil


def makedir_if_not_exists(path):
    if not os.path.exists(path):
        os.mkdir(path)


# PROFILE_PATH = "./profile/"
# FIXME: use user directory on Windows as well
PROFILE_PATH = os.path.join(os.path.expanduser("~"), ".pymotron") + "/"
print(PROFILE_PATH)
makedir_if_not_exists(PROFILE_PATH)

VNC_PASSWORD_PATH = PROFILE_PATH + "vncpasswds/"
USER_PROFILE_PATH = PROFILE_PATH + "user_profile.json"
PRIVATE_KEYS_PATH = PROFILE_PATH + "keys/"
CONN_PROFILE_PATH = PROFILE_PATH + "connections/"

try:
    shutil.rmtree(VNC_PASSWORD_PATH)
except FileNotFoundError:
    pass

makedir_if_not_exists(VNC_PASSWORD_PATH)
makedir_if_not_exists(PRIVATE_KEYS_PATH)
if not os.path.exists(CONN_PROFILE_PATH):
    shutil.copytree("./profile/connections", CONN_PROFILE_PATH)

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
