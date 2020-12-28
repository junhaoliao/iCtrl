import json
from urllib.error import URLError
from urllib.request import urlopen

LATEST_RELEASE_URL = "https://api.github.com/repos/junhaoliao/UG_Remote/releases/latest"


def compare_version(current_ver, result):
    version_mismatch = False
    try:
        file = urlopen(LATEST_RELEASE_URL)
        json_data = json.loads(file.read())
        latest_ver = json_data["tag_name"].split(".")

        for i in range(3):
            if current_ver[i] < int(latest_ver[i]):
                version_mismatch = True
                break
    except URLError:
        print("The updater is unable to access GitHub API for version comparison. ")
    except (IndexError, ValueError):
        version_mismatch = True

    result[0] = version_mismatch
