import datetime
import threading
import webbrowser

import PySimpleGUI as sg

import callback
import layout
import updater
from path_names import *

# the version check should be non-blocking to speedup loading process
needs_update = [False]
if (
        datetime.datetime.now() - datetime.datetime.fromisoformat(callback.my_profile["last_checked_update"])
).days >= 1:
    update_thread = threading.Thread(target=updater.compare_version, args=(needs_update,))
    update_thread.start()
    print("Checking for updates... ")
else:
    print("Have checked for updates within a day. Not checking this time. ")

dispatch_dictionary = {
    "-EECG_SELECT_PORT-": callback.cb_eecg_select_port,
    "-EECG_RANDOM_PORT-": callback.cb_eecg_random_port,
    "-EECG_CHECK_LOADS-": callback.cb_eecg_check_loads,
    "-EECG_RESET_NO-": callback.cb_eecg_reset_no,
    "-EECG_RESET_YES-": callback.cb_eecg_reset_yes,
    "-ECF_CONNECT-": callback.cb_ecf_connect,
    "-LAB_INTF-": callback.cb_switch_intf,
    "-DELETE_ALL-": callback.cb_delete_all,
    "-COPYRIGHT-": callback.cb_open_junhao_ca,
    "-OPEN_WEBSITE-": callback.cb_open_junhao_ca
}

window = None
# enable HiDPI awareness on Windows to fix blurry text
if platform.system() == "Windows":
    from ctypes import windll

    windll.shcore.SetProcessDpiAwareness(1)
    window = sg.Window("UG_Remote", layout.layout, element_padding=(38, 12)).finalize()
elif platform.system() == "Darwin":
    window = sg.Window("UG_Remote", layout.layout, element_padding=(16, 10)).finalize()
else:
    Exception("System %s not supported yet. Please submit an issue on GitHub. " % platform.system())

callback.preselect_lab(window)
callback.prefill_eecg_profile(window)
callback.prefill_ecf_profile(window)

while True:
    event, values = window.read(timeout=1000)
    if event == sg.WIN_CLOSED or event == 'Exit':
        break

    if needs_update[0]:
        needs_update[0] = False
        # inserting the spaces and "LRM" character to expand the window title
        resp = sg.popup_ok_cancel("Found a new version.         ‎\n"
                                  "Do you want to update?",
                                  title="UG_Remote Updater",
                                  font=layout.FONT_HELVETICA_16,
                                  keep_on_top=True)
        if resp == "OK":
            webbrowser.open(updater.GITHUB_RELEASE_PAGE)

    # Lookup event in function dictionary
    if event in dispatch_dictionary:
        func_to_call = dispatch_dictionary[event]  # get function from dispatch dictionary
        func_to_call(window=window, values=values)
    # else:  # use for debugging only: should comment this out before publishing
    #     print(event, values)
    #     print('Event {} not in dispatch dictionary'.format(event))

    if not callback.my_eecg_conn.connected:
        layout.enable_eecg_components(window)
    if not callback.my_ecf_conn.connected:
        layout.enable_ecf_components(window)

window.close()
sys.stdout.flush()
sys.stderr.flush()
os._exit(0)
