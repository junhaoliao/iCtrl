import os
import platform


def makedir_if_not_exists(path):
    if not os.path.exists(path):
        os.mkdir(path)


# setup profile path
if platform.system() == "Windows":
    PROFILE_PATH = os.path.join(os.environ['LOCALAPPDATA'], "ictrl")
elif platform.system() == "Darwin" or 'Linux':
    PROFILE_PATH = os.path.join(os.path.expanduser("~"), ".ictrl")
else:
    raise SystemError(f"Operating System: {platform.system()} not supported")

makedir_if_not_exists(PROFILE_PATH)
USER_PROFILE_PATH = os.path.join(PROFILE_PATH, "user_profile.json")
PRIVATE_KEY_PATH = os.path.join(PROFILE_PATH, "private_keys")
makedir_if_not_exists(PRIVATE_KEY_PATH)

# setup font path for Favicon
if platform.system() == "Windows":
    FONT_PATH = 'arial.ttf'
elif platform.system() == "Darwin":
    FONT_PATH = '/System/Library/Fonts/Supplemental/Arial Unicode.ttf'
elif platform.system() == "Linux":
    FONT_PATH = 'NotoSansMono-CondensedBlack.ttf'
