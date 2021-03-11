import json
from urllib.error import URLError
from urllib.request import urlopen

CURRENT_VER = (5, 1, 0)
UGREMOTE_DOWNLOAD_PAGE = "https://junhaoliao.github.io/UG_Remote/"
LATEST_RELEASE_URL = "https://api.github.com/repos/junhaoliao/UG_Remote/releases/latest"


def compare_version(result):
    version_mismatch = False
    try:
        file = urlopen(LATEST_RELEASE_URL)
        json_data = json.loads(file.read())
        latest_ver = json_data["tag_name"].split(".")

        for i in range(3):
            if CURRENT_VER[i] < int(latest_ver[i]):
                version_mismatch = True
                break
            elif CURRENT_VER[i] > int(latest_ver[i]):
                break

    except URLError:
        print("The updater is unable to access GitHub API for version comparison. ")
    except (IndexError, ValueError):
        version_mismatch = True

    if version_mismatch:
        print("Updater: detected a new version: latest=" + str(latest_ver) + "cur=" + str(CURRENT_VER))
    else:
        print("Updater: No updates available: cur=" + str(CURRENT_VER))

    result[0] = version_mismatch
