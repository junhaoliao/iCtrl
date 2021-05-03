import copy
import json


class UGConnProfile:
    """ Connection Profile that stores all available servers for some lab
    >>> eecg_profile = UGConnProfile()
    >>> EECG_MACHINE_NUMS = list(range(51, 76)) + list(range(132, 181)) + list(range(201, 252))
    >>> for num in EECG_MACHINE_NUMS:
    ...     eecg_profile["servers"].append("ug%d.eecg.toronto.edu"% num)
    >>> eecg_profile["vnc_manual"] = True
    >>> eecg_profile.save_profile("./profile/connections/eecg.json")
    >>> test_profile = UGConnProfile()
    >>> test_profile.load_profile("./profile/connections/eecg.json")
    >>> print(test_profile["vnc_manual"])
    True
    >>> print(test_profile["servers"][0])
    ug51.eecg.toronto.edu
    >>> print(test_profile["servers"][-1])
    ug251.eecg.toronto.edu
    >>> print(test_profile["vnc_listening_port"])
    0
    >>> ecf_profile = UGConnProfile()
    >>> ECF_MACHINE_NUMS = list(range(2, 5))      + \
                            list(range(6, 43))    + \
                            list(range(44, 103))  + \
                            list(range(104, 120)) + \
                            list(range(121, 130)) + \
                            list(range(131, 140)) + \
                            list(range(142, 147)) + \
                            list(range(148, 160)) + \
                            list(range(161, 181)) + \
                            list(range(182, 186))
    >>> ecf_profile["servers"].append("remote.ecf.utoronto.ca")
    >>> for num in ECF_MACHINE_NUMS:
    ...     ecf_profile["servers"].append("p%d.ecf.utoronto.ca"% num)
    >>> ecf_profile["vnc_manual"] = False
    >>> ecf_profile["vnc_listening_port"] = 1000
    >>> ecf_profile.save_profile("./profile/connections/ecf.json")
    >>> test_profile.load_profile("./profile/connections/ecf.json")
    >>> print(test_profile["vnc_manual"])
    False
    >>> print(test_profile["servers"][0])
    remote.ecf.utoronto.ca
    >>> print(test_profile["servers"][-1])
    p185.ecf.utoronto.ca
    >>> print(test_profile["vnc_listening_port"])
    1000
    """
    version = 1  # in case the schema changes in the future
    _empty_conn_profile = {
        "version": version,

        "servers": [],
        "vnc_manual": False,

        "vnc_listening_port": 0
    }

    def __init__(self):
        self._profile = copy.deepcopy(UGConnProfile._empty_conn_profile)

    def __setitem__(self, key, value):
        self._profile[key] = value

    def __getitem__(self, key):
        return self._profile[key]

    def load_profile(self, file_path):
        self._profile = copy.deepcopy(UGConnProfile._empty_conn_profile)
        try:
            with open(file_path, "r") as infile:
                json_data = json.load(infile)

                if "version" not in json_data or json_data["version"] != UGConnProfile.version:
                    print("Connection Profile version mismatch. ")
                    return

                # TODO: make sure the profile file is not modified in an attempt to crash the script
                self._profile = json_data
        except Exception as e:
            self._profile = copy.deepcopy(UGConnProfile._empty_conn_profile)
            print("Exception happens when trying to load connection profile. Using default profile. ")
            # raise e

    def save_profile(self, file_path):
        try:
            with open(file_path, 'w') as outfile:
                json_data = json.dumps(self._profile, indent=4)
                outfile.write(json_data)
        except Exception:
            # need to handle any write permission issues, once observed
            raise Exception
