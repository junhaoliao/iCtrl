import re

import PySimpleGUI as sg

import machines
import exceptions
import layout
import ug_connection
import ug_profile
from path_names import *


def login():
    sg.Popup("Logging in...",
             font=layout.FONT_HELVETICA_16,
             background_color="light yellow",
             no_titlebar=True,
             button_type=sg.POPUP_BUTTONS_NO_BUTTONS,
             non_blocking=True,
             auto_close=True,
             auto_close_duration=3)

    srv_num = values["-MACHINE_NUM-"]
    if srv_num not in machines.MACHINES:
        sg.Popup("User entered Machine # invalid. ",
                 button_type=sg.POPUP_BUTTONS_OK, button_color=('white', 'red'))
        return False
    username = values["-USERNAME-"]
    ug_passwd = values["-UG_PASSWD-"]
    try:
        myConn.connect(int(srv_num), username, ug_passwd)
    except (exceptions.NetworkError, exceptions.SSHAuthError) as e:
        sg.Popup(e, title=e.__class__.__name__,
                 button_type=sg.POPUP_BUTTONS_OK, button_color=('white', 'red'))
        return False

    # if successful login, hide the "logging in" popup
    window.force_focus()

    myProfile.username = username
    myProfile.ug_passwd = ug_passwd
    myProfile.last_srv = srv_num

    return True


def update_port_buttons(window_ports):
    for i in range(0, 10):
        for j in range(0, 10):
            port_num = i * 10 + j
            if port_num != 0:
                if port_num in myConn.ports_by_me_lst:
                    window_ports["-PORT%d-" % port_num](button_color=layout.COLOR_USED_BY_ME_BUTTON)
                    window_ports["-PORT%d-" % port_num].set_tooltip("Busy: Created by Me")
                elif port_num in myConn.used_ports_lst:
                    window_ports["-PORT%d-" % port_num](button_color=layout.COLOR_BUSY_BUTTON)
                    window_ports["-PORT%d-" % port_num].set_tooltip("Busy: Likely Used by Others")
                else:
                    window_ports["-PORT%d-" % port_num](button_color=layout.COLOR_FREE_BUTTON)
                    window_ports["-PORT%d-" % port_num].set_tooltip("Free")


def launch_vnc(port_num):
    sg.Popup(f"Launching VNC at Port {port_num:d} ...",
             font=layout.FONT_HELVETICA_16,
             background_color="light yellow",
             no_titlebar=True,
             button_type=sg.POPUP_BUTTONS_NO_BUTTONS,
             non_blocking=True,
             auto_close=True,
             auto_close_duration=5)

    myConn.create_vnc_tunnel(port_num)

    actual_port = 5900 + port_num
    import subprocess
    if platform.system() == 'Darwin':
        subprocess.Popen([VNC_VIEWER_PATH_MACOS, "--passwd=%s" % VNC_PASSWD_PATH, "localhost:%d" % actual_port])
    elif platform.system() == 'Windows':
        subprocess.call(["cmd", "/c", "start", "/max",
                         VNC_VIEWER_PATH_WIN64, "--passwd=%s" % VNC_PASSWD_PATH, "localhost:%d" % actual_port])
    else:
        print("System %snot supported" % platform.system())


def check_and_save_vnc_passwd(vnc_passwd_input):
    sg.Popup("Resetting VNC Password...",
             font=layout.FONT_HELVETICA_16,
             background_color="light yellow",
             no_titlebar=True,
             button_type=sg.POPUP_BUTTONS_NO_BUTTONS,
             non_blocking=True,
             auto_close=True,
             auto_close_duration=2)

    # TODO: not fully reliable, should check back later
    if "'" in vnc_passwd_input:
        sg.Popup("Error: VNC password cannot contain symbol (')",
                 title="VNC Password Criteria Unmet...",
                 button_type=sg.POPUP_BUTTONS_OK, button_color=('white', 'red'))
        return False
    elif len(vnc_passwd_input) < 6:
        sg.Popup("Error: VNC password should have length of 6 - 8",
                 title="VNC Password Criteria Unmet...",
                 button_type=sg.POPUP_BUTTONS_OK, button_color=('white', 'red'))
        return False
    elif len(vnc_passwd_input) > 8:
        sg.Popup("Warning: VNC password with length longer than 8 will be truncated",
                 title="VNC Password Criteria Warning...",
                 button_type=sg.POPUP_BUTTONS_OK, button_color=('white', 'orange'))
        return False

    try:
        myConn.set_and_save_vnc_passwd(vnc_passwd_input)
    except Exception as e:
        sg.Popup(e,
                 title="Unexpected Error %s" % e.__class__.__name__,
                 button_type=sg.POPUP_BUTTONS_OK, button_color=('white', 'red'))

    return True


# callback functions
def cb_select_port():
    print("Callback: cb_select_port")

    layout.disable_all_components(window)
    if not login():
        layout.enable_all_components(window)
        window.force_focus()
        return

    if values["-RESET_YES-"] and not check_and_save_vnc_passwd(values["-VNC_PASSWD-"]):
        layout.enable_all_components(window)
        window.force_focus()
        return

    myConn.update_ports()
    layout_port = []
    for i in range(10):
        row = []
        for j in range(10):
            port_num = i * 10 + j
            if port_num == 0:
                port_but = sg.Button("⟳",
                                     font=layout.FONT_HELVETICA_16_BOLD, size=(3, 1),
                                     button_color=layout.COLOR_REFRESH_BUTTON,
                                     tooltip="Kill all VNC servers launched by me",
                                     key="-REFRESH-")
            elif port_num in myConn.ports_by_me_lst:
                port_but = sg.Button(str(port_num).zfill(2),
                                     font=layout.FONT_HELVETICA_16_BOLD, size=(3, 1),
                                     button_color=layout.COLOR_USED_BY_ME_BUTTON,
                                     tooltip="Busy: Created by Me",
                                     key="-PORT%d-" % port_num)
            elif port_num in myConn.used_ports_lst:
                port_but = sg.Button(str(port_num).zfill(2),
                                     font=layout.FONT_HELVETICA_16_BOLD, size=(3, 1),
                                     button_color=layout.COLOR_BUSY_BUTTON,
                                     tooltip="Busy: Likely Used by Others",
                                     key="-PORT%d-" % port_num)
            else:
                port_but = sg.Button(str(port_num).zfill(2),
                                     font=layout.FONT_HELVETICA_16_BOLD, size=(3, 1),
                                     button_color=layout.COLOR_FREE_BUTTON,
                                     tooltip="Free",
                                     key="-PORT%d-" % port_num)
            row.append(port_but)
        layout_port.append(row)

    port_num = None

    window_ports = sg.Window("Select a Port", layout=layout_port)
    window_ports.finalize()
    while True:
        event_ports, values_ports = window_ports.read()
        if event_ports == sg.WIN_CLOSED or event_ports == 'Exit':
            break
        elif event_ports == "-REFRESH-":
            sg.Popup("Killing all VNC servers launched by me...",
                     font=layout.FONT_HELVETICA_16,
                     background_color="light yellow",
                     no_titlebar=True,
                     button_type=sg.POPUP_BUTTONS_NO_BUTTONS,
                     non_blocking=True,
                     auto_close=True,
                     auto_close_duration=2)
            myConn.killall_VNC_servers()
            myConn.update_ports()
            update_port_buttons(window_ports)
            window_ports.force_focus()
        elif "PORT" in event_ports:
            port_num = int(re.findall(r'\d+', event_ports)[0])
            break

    window_ports.close()

    if port_num is None:
        layout.enable_all_components(window)
        window.force_focus()
        return
    else:
        if len(myConn.ports_by_me_lst) > 0 and port_num not in myConn.ports_by_me_lst:
            killall = sg.popup_yes_no("You have already had an active VNC server on other ports.\n"
                                      "Do you want to kill the previous connection? ")
            if killall == "Yes":
                myConn.killall_VNC_servers()
            else:
                layout.enable_all_components(window)
                window.force_focus()
                return
        launch_vnc(port_num)
        myProfile.save_profile()


def cb_random_port():
    print("Callback: cb_random_port")

    layout.disable_all_components(window)
    if not login():
        layout.enable_all_components(window)
        window.force_focus()
        return

    if values["-RESET_YES-"] and not check_and_save_vnc_passwd(values["-VNC_PASSWD-"]):
        layout.enable_all_components(window)
        window.force_focus()
        return

    myConn.update_ports()
    if len(myConn.ports_by_me_lst) == 1:
        port_num = myConn.ports_by_me_lst[0]
        print("Using the last used port number %d" % port_num)
    else:
        myConn.killall_VNC_servers()
        from random import choice
        try:
            port_num = choice([i for i in range(1, 100) if i not in myConn.used_ports_lst])
            print("Randomly chose a port number %d" % port_num)
        except IndexError as e:  # hope it never happens...
            sg.Popup("OMG how come 99 people are using this machine!!\n"
                     "Change to another one please!! ",
                     title="Server too busy...",
                     button_type=sg.POPUP_BUTTONS_OK, button_color=('white', 'red'))
            return

    launch_vnc(port_num)
    myProfile.save_profile()


def cb_reset_no():
    window["-RESET_NO-"](myProfile.vnc_passwd_exist)
    window["-RESET_YES-"](not myProfile.vnc_passwd_exist)
    window["-VNC_PASSWD_COL-"](visible=not myProfile.vnc_passwd_exist)
    window["-VNC_PASSWD-"]("", disabled=myProfile.vnc_passwd_exist)


def cb_reset_yes():
    window["-RESET_NO-"](False)
    window["-RESET_YES-"](True)
    window["-VNC_PASSWD_COL-"](visible=True)
    window["-VNC_PASSWD-"](disabled=False)


myConn = ug_connection.UG_Connection()

myProfile = ug_profile.UG_Profile()
myProfile.load_profile()

# enable HiDPI awareness on Windows to fix blurry text
if platform.system() == "Windows":
    from ctypes import windll

    windll.shcore.SetProcessDpiAwareness(1)

window = sg.Window("UG Remote", layout.layout, element_padding=(38, 12))
window.finalize()

dispatch_dictionary = {
    "-SELECT_PORT-": cb_select_port,
    "-RANDOM_PORT-": cb_random_port,
    "-RESET_NO-": cb_reset_no,
    "-RESET_YES-": cb_reset_yes
}

if myProfile.loaded:
    # display srv, username and password if already loaded
    window["-MACHINE_NUM-"](myProfile.last_srv)
    window["-USERNAME-"](myProfile.username)
    window["-UG_PASSWD-"](myProfile.ug_passwd)

    # default not to reset vnc passwd if vnc passwd exist
    window["-RESET_NO-"](myProfile.vnc_passwd_exist)
    window["-RESET_YES-"](not myProfile.vnc_passwd_exist)
    window["-VNC_PASSWD_COL-"](visible=not myProfile.vnc_passwd_exist)

    event, values = window.read(timeout=0.001)
    login()

while True:
    event, values = window.read()
    if event == sg.WIN_CLOSED or event == 'Exit':
        break

    # Lookup event in function dictionary
    if event in dispatch_dictionary:
        func_to_call = dispatch_dictionary[event]  # get function from dispatch dictionary
        func_to_call()
    # else:  # should comment this out before publishing
    #     print(event, values)
    #     print('Event {} not in dispatch dictionary'.format(event))

window.close()
os._exit(0)
