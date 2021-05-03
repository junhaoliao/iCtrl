import os
import platform
import shutil


def makedir_if_not_exists(path):
    if not os.path.exists(path):
        os.mkdir(path)


# PROFILE_PATH = "./profile/"
# FIXME: use user directory on Windows as well
if platform.system() == "Windows":
    PROFILE_PATH = os.path.join(os.environ['LOCALAPPDATA'], "PyMotron")
elif platform.system() == "Darwin":
    PROFILE_PATH = os.path.join(os.path.expanduser("~"), ".pymotron")
else:
    raise SystemError(f"Operating System: {platform.system()} not supported")

makedir_if_not_exists(PROFILE_PATH)

VNC_PASSWORD_PATH = os.path.join(PROFILE_PATH, "vncpasswds")
USER_PROFILE_PATH = os.path.join(PROFILE_PATH, "user_profile.json")
PRIVATE_KEYS_PATH = os.path.join(PROFILE_PATH, "keys")
CONN_PROFILE_PATH = os.path.join(PROFILE_PATH, "connections")
XSTARTUP_PATH = os.path.join(PROFILE_PATH, "xstartup")

try:
    shutil.rmtree(VNC_PASSWORD_PATH)
except FileNotFoundError:
    pass

makedir_if_not_exists(VNC_PASSWORD_PATH)
makedir_if_not_exists(PRIVATE_KEYS_PATH)
if not os.path.exists(CONN_PROFILE_PATH):
    integrated_conn_profiles_path = os.path.join(os.getcwd(), "profile", "connections")
    shutil.copytree(integrated_conn_profiles_path, CONN_PROFILE_PATH)
if not os.path.exists(XSTARTUP_PATH):
    integrated_xstartup_path = os.path.join(os.getcwd(), "profile", "xstartup")
    shutil.copy(integrated_xstartup_path, XSTARTUP_PATH)

TIGER_VNC_VIEWER_PATH_WIN64 = "vncviewer64.exe"
TIGER_VNC_VIEWER_PATH_MACOS = "/Applications/TigerVNC Viewer*.app"

REAL_VNC_VIEWER_PATH_WIN64 = ""
REAL_VNC_VIEWER_PATH_MACOS = "/Applications/VNC Viewer.app"

if platform.system() == "Windows":
    if not os.path.isfile(TIGER_VNC_VIEWER_PATH_WIN64):
        print("Could not find TigerVNC")
        TIGER_VNC_VIEWER_PATH_WIN64 = None

    import winreg
    try:
        key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\RealVNC\installer\vncviewer")
        REAL_VNC_VIEWER_PATH_WIN64 = os.path.join(winreg.QueryValueEx(key, "InstallLocation")[0], "vncviewer.exe")
    except Exception as e:
        print("Registry key of RealVNC cannot be read. Could not find RealVNC")
        REAL_VNC_VIEWER_PATH_WIN64 = None

elif platform.system() == "Darwin":  # Mac OS
    import glob

    # check whether TigerVNC is installed
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
