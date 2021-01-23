import re
import webbrowser

import PySimpleGUI as sg

import ecf_connection
import eecg_connection
import exceptions
import layout
import machines
import ug_profile
from path_names import *

my_eecg_conn = eecg_connection.EECGConnection()
my_ecf_conn = ecf_connection.ECFConnection()
my_profile = ug_profile.UGProfile()
my_profile.load_profile()


def login_eecg(window, values):
    sg.Popup("Logging in...",
             font=layout.FONT_HELVETICA_16,
             background_color="light yellow",
             no_titlebar=True,
             button_type=sg.POPUP_BUTTONS_NO_BUTTONS,
             non_blocking=True,
             auto_close=True,
             auto_close_duration=3)

    srv_num = values["-EECG_MACHINE_NUM-"]
    if srv_num not in machines.MACHINES:
        sg.Popup("User entered an invalid Machine number. ",
                 button_type=sg.POPUP_BUTTONS_OK, button_color=('white', 'red'))
        return False
    username = values["-EECG_USERNAME-"]
    eecg_passwd = values["-EECG_PASSWD-"]
    try:
        my_eecg_conn.connect(int(srv_num), username, eecg_passwd)
    except (exceptions.NetworkError, exceptions.SSHAuthError) as e:
        sg.Popup(e, title=e.__class__.__name__,
                 button_type=sg.POPUP_BUTTONS_OK, button_color=('white', 'red'))
        return False

    # if successful login, hide the "logging in" popup
    window.force_focus()

    my_profile.set_eecg_profile(srv_num, username, eecg_passwd)

    return True


def login_ecf(window, values):
    sg.Popup("Logging in...",
             font=layout.FONT_HELVETICA_16,
             background_color="light yellow",
             no_titlebar=True,
             button_type=sg.POPUP_BUTTONS_NO_BUTTONS,
             non_blocking=True,
             auto_close=True,
             auto_close_duration=3)

    username = values["-ECF_USERNAME-"]
    ecf_passwd = values["-ECF_PASSWD-"]
    try:
        my_ecf_conn.connect(username, ecf_passwd)
    except (exceptions.NetworkError, exceptions.SSHAuthError) as e:
        sg.Popup(e, title=e.__class__.__name__,
                 button_type=sg.POPUP_BUTTONS_OK, button_color=('white', 'red'))
        return False

    # if successful login, hide the "logging in" popup
    window.force_focus()

    my_profile.set_ecf_profile(username, ecf_passwd)

    return True


def preselect_lab(window):
    if my_profile["last_lab"] == "ECF":
        window["ECF"].Select()

def preselect_viewer(window):
    window["-SELECT_VIEWER-"](my_profile["viewer"])

def prefill_eecg_profile(window):
    if my_profile["EECG"]["loaded"]:
        # display srv, username and password if already loaded
        window["-EECG_MACHINE_NUM-"](my_profile["EECG"]["last_srv"])
        window["-EECG_USERNAME-"](my_profile["EECG"]["username"])
        window["-EECG_PASSWD-"](my_profile["EECG"]["passwd"])

        # default not to reset vnc passwd if vnc passwd exist
        window["-EECG_RESET_NO-"](my_profile.eecg_vnc_passwd_exist)
        window["-EECG_RESET_YES-"](not my_profile.eecg_vnc_passwd_exist)
        window["-EECG_VNC_PASSWD_COL-"](visible=not my_profile.eecg_vnc_passwd_exist)

        event, values = window.read(timeout=1)
        login_eecg(window, values)


def prefill_ecf_profile(window):
    if my_profile["ECF"]["loaded"]:
        # display username and password if already loaded
        window["-ECF_USERNAME-"](my_profile["ECF"]["username"])
        window["-ECF_PASSWD-"](my_profile["ECF"]["passwd"])

        event, values = window.read(timeout=1)
        login_ecf(window, values)


def update_port_buttons(window_ports):
    for i in range(0, 10):
        for j in range(0, 10):
            port_num = i * 10 + j
            if port_num != 0:
                if port_num in my_eecg_conn.ports_by_me_lst:
                    window_ports["-PORT%d-" % port_num](button_color=layout.COLOR_EECG_USED_BY_ME_BUTTON)
                    window_ports["-PORT%d-" % port_num].set_tooltip("Busy: Created by Me")
                elif port_num in my_eecg_conn.used_ports_lst:
                    window_ports["-PORT%d-" % port_num](button_color=layout.COLOR_EECG_BUSY_BUTTON)
                    window_ports["-PORT%d-" % port_num].set_tooltip("Busy: Likely Used by Others")
                else:
                    window_ports["-PORT%d-" % port_num](button_color=layout.COLOR_EECG_FREE_BUTTON)
                    window_ports["-PORT%d-" % port_num].set_tooltip("Free")


VNC_MISSING_PROMPT = "Could not find any installed %s on your computer. \n" \
                     "You can follow the UG_Remote installer to install TigerVNC, \n" \
                     "or try setting %s as the Viewer under Misc before clicking \"Connect\", \n" \
                     "or you may still launch your favourite VNC viewer manually if you wish. \n\n" \
                     "The VNC Address is localhost:"
TIGER_VNC_MISSING_PROMPT = VNC_MISSING_PROMPT % ("TigerVNC", "RealVNC") + "%d"
REAL_VNC_MISSING_PROMPT = VNC_MISSING_PROMPT % ("RealVNC", "TigerVNC") + "%d"


def launch_vnc(viewer, lab, port_num):
    sg.Popup(f"Launching %s VNC at Port %d ..." % (lab, port_num),
             font=layout.FONT_HELVETICA_16,
             background_color="light yellow",
             no_titlebar=True,
             button_type=sg.POPUP_BUTTONS_NO_BUTTONS,
             non_blocking=True,
             auto_close=True,
             auto_close_duration=5)

    if lab == "EECG":
        my_eecg_conn.create_vnc_tunnel(port_num)
        actual_port = 5900 + port_num
    else:
        my_ecf_conn.create_vnc_tunnel()
        actual_port = 2000

    if platform.system() == "Darwin":
        if viewer == "TigerVNC" and TIGER_VNC_VIEWER_PATH_MACOS is None:
            sg.Popup(TIGER_VNC_MISSING_PROMPT % actual_port,
                     title="TigerVNC NOT Found",
                     keep_on_top=True,
                     button_type=sg.POPUP_BUTTONS_OK, button_color=('white', 'red'))
            return
        elif viewer == "RealVNC" and REAL_VNC_VIEWER_PATH_MACOS is None:
            sg.Popup(REAL_VNC_MISSING_PROMPT % actual_port,
                     title="RealVNC NOT Found",
                     keep_on_top=True,
                     button_type=sg.POPUP_BUTTONS_OK, button_color=('white', 'red'))
            return
    elif platform.system() == "Windows" and TIGER_VNC_VIEWER_PATH_WIN64 is None:
        if viewer == "TigerVNC" and TIGER_VNC_VIEWER_PATH_WIN64 is None:
            sg.Popup(TIGER_VNC_MISSING_PROMPT % actual_port,
                     title="TigerVNC NOT Found",
                     keep_on_top=True,
                     button_type=sg.POPUP_BUTTONS_OK, button_color=('white', 'red'))
            return
        elif viewer == "RealVNC" and REAL_VNC_VIEWER_PATH_WIN64 is None:
            sg.Popup(REAL_VNC_MISSING_PROMPT % actual_port,
                     title="RealVNC NOT Found",
                     keep_on_top=True,
                     button_type=sg.POPUP_BUTTONS_OK, button_color=('white', 'red'))
            return

    import subprocess
    # flush the outputs before launching TigerVNC Viewer
    sys.stdout.flush()
    sys.stderr.flush()
    if platform.system() == 'Darwin':
        if viewer == "TigerVNC":
            # not using subprocess for MacOS as TigerVNC has problem supporting HiDPI in some system versions
            os.system(
                "open -n %s --args --passwd=%s localhost:%d" % (
                    TIGER_VNC_VIEWER_PATH_MACOS, os.path.abspath(VNC_PASSWD_PATH), actual_port))
        else:
            # Set more arguments for RealVNC for compatibility issues
            # -FullColour : solve the distorted colour issue
            # -SecurityNotificationTimeout=0 : suppress the encryption warning
            # -WarnUnencrypted : suppress the encryption warning
            # -Scaling=Fit : scale to fit window
            os.system(
                "open -n %s --args "
                "-FullColour "
                "-SecurityNotificationTimeout=0 "
                "-WarnUnencrypted=FALSE "
                "-Scaling=AspectFit "
                "--passwd=%s localhost:%d" % (
                    REAL_VNC_VIEWER_PATH_MACOS, os.path.abspath(VNC_PASSWD_PATH), actual_port))
    elif platform.system() == 'Windows':
        # TODO: support launching with other VNC viewers on Windows

        subprocess.call(["cmd", "/c", "start", "/max",
                         TIGER_VNC_VIEWER_PATH_WIN64, "--passwd=%s" % VNC_PASSWD_PATH, "localhost:%d" % actual_port])
    else:
        print("System %snot supported" % platform.system())

    # flush the outputs before terminating for easier debugging
    sys.stdout.flush()
    sys.stderr.flush()

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
                 button_type=sg.POPUP_BUTTONS_OK,
                 button_color=('white', 'red'),
                 keep_on_top=True)
        return False
    elif len(vnc_passwd_input) < 6:
        sg.Popup("Error: VNC password should have length of 6 - 8",
                 title="VNC Password Criteria Unmet...",
                 button_type=sg.POPUP_BUTTONS_OK,
                 button_color=('white', 'red'),
                 keep_on_top=True)
        return False
    elif len(vnc_passwd_input) > 8:
        sg.Popup("Warning: VNC password with length longer than 8 will be truncated",
                 title="VNC Password Criteria Warning...",
                 button_type=sg.POPUP_BUTTONS_OK,
                 button_color=('white', 'orange'),
                 keep_on_top=True)
        return False

    try:
        my_eecg_conn.set_and_save_vnc_passwd(vnc_passwd_input)
    except exceptions.QuotaError as e:
        sg.Popup(e,
                 title="Unexpected Error %s" % e.__class__.__name__,
                 button_type=sg.POPUP_BUTTONS_OK,
                 button_color=('white', 'red'),
                 keep_on_top=True)
        return False

    return True


# callback functions
def cb_eecg_select_port(window, values):
    print("Callback: cb_eecg_select_port")

    layout.disable_eecg_components(window)
    if not login_eecg(window, values):
        layout.enable_eecg_components(window)
        window.force_focus()
        return

    if values["-EECG_RESET_YES-"] and not check_and_save_vnc_passwd(values["-EECG_VNC_PASSWD-"]):
        layout.enable_eecg_components(window)
        window.force_focus()
        return

    my_eecg_conn.update_ports()
    layout_port = []
    for i in range(10):
        row = []
        for j in range(10):
            port_num = i * 10 + j
            if port_num == 0:
                port_but = sg.Button("⟳",
                                     font=layout.FONT_HELVETICA_16_BOLD, size=(3, 1),
                                     button_color=layout.COLOR_EECG_REFRESH_BUTTON,
                                     tooltip="Kill all VNC servers launched by me",
                                     key="-EECG_REFRESH-")
            elif port_num in my_eecg_conn.ports_by_me_lst:
                port_but = sg.Button(str(port_num).zfill(2),
                                     font=layout.FONT_HELVETICA_16_BOLD, size=(3, 1),
                                     button_color=layout.COLOR_EECG_USED_BY_ME_BUTTON,
                                     tooltip="Busy: Created by Me",
                                     key="-PORT%d-" % port_num)
            elif port_num in my_eecg_conn.used_ports_lst:
                port_but = sg.Button(str(port_num).zfill(2),
                                     font=layout.FONT_HELVETICA_16_BOLD, size=(3, 1),
                                     button_color=layout.COLOR_EECG_BUSY_BUTTON,
                                     tooltip="Busy: Likely Used by Others",
                                     key="-PORT%d-" % port_num)
            else:
                port_but = sg.Button(str(port_num).zfill(2),
                                     font=layout.FONT_HELVETICA_16_BOLD, size=(3, 1),
                                     button_color=layout.COLOR_EECG_FREE_BUTTON,
                                     tooltip="Free",
                                     key="-PORT%d-" % port_num)
            row.append(port_but)
        layout_port.append(row)

    port_num = None

    window_ports = sg.Window("Select a Port", layout=layout_port).finalize()
    while True:
        event_ports, values_ports = window_ports.read()
        if event_ports == sg.WIN_CLOSED or event_ports == 'Exit':
            break
        elif event_ports == "-EECG_REFRESH-":
            sg.Popup("Killing all VNC servers launched by me...",
                     font=layout.FONT_HELVETICA_16,
                     background_color="light yellow",
                     no_titlebar=True,
                     button_type=sg.POPUP_BUTTONS_NO_BUTTONS,
                     non_blocking=True,
                     auto_close=True,
                     auto_close_duration=2)
            my_eecg_conn.killall_VNC_servers()
            my_eecg_conn.update_ports()
            update_port_buttons(window_ports)
            window_ports.force_focus()
        elif "PORT" in event_ports:
            port_num = int(re.findall(r'\d+', event_ports)[0])
            break

    window_ports.close()

    if port_num is None:
        layout.enable_eecg_components(window)
        window.force_focus()
        return
    else:
        if len(my_eecg_conn.ports_by_me_lst) > 0 and port_num not in my_eecg_conn.ports_by_me_lst:
            killall = sg.popup_yes_no("You have already had an active VNC server on other ports.\n"
                                      "Do you want to kill the previous connection? ")
            if killall == "Yes":
                my_eecg_conn.killall_VNC_servers()
            else:
                layout.enable_eecg_components(window)
                window.force_focus()
                return
        launch_vnc(values["-SELECT_VIEWER-"], "EECG", port_num)
        my_profile.save_profile("EECG", values["-SELECT_VIEWER-"])


def cb_eecg_random_port(window, values):
    print("Callback: cb_eecg_random_port")

    layout.disable_eecg_components(window)
    if not login_eecg(window, values):
        layout.enable_eecg_components(window)
        window.force_focus()
        return

    if values["-EECG_RESET_YES-"] and not check_and_save_vnc_passwd(values["-EECG_VNC_PASSWD-"]):
        layout.enable_eecg_components(window)
        window.force_focus()
        return

    my_eecg_conn.update_ports()
    if len(my_eecg_conn.ports_by_me_lst) == 1:
        port_num = my_eecg_conn.ports_by_me_lst[0]
        print("Using the last used port number %d" % port_num)
    else:
        my_eecg_conn.killall_VNC_servers()
        from random import choice
        try:
            port_num = choice([i for i in range(1, 100) if i not in my_eecg_conn.used_ports_lst])
            print("Randomly chose a port number %d" % port_num)
        except IndexError:  # hope it never happens...
            sg.Popup("OMG how come 99 people are using this machine!!\n"
                     "Change to another one please!! ",
                     title="Server too busy...",
                     button_type=sg.POPUP_BUTTONS_OK, button_color=('white', 'red'))
            return

    launch_vnc(values["-SELECT_VIEWER-"], "EECG", port_num)
    my_profile.save_profile("EECG", values["-SELECT_VIEWER-"])


# callback functions
def cb_eecg_check_loads(window, values):
    print("Callback: cb_eecg_check_loads")

    layout.disable_eecg_components(window)
    if not login_eecg(window, values):
        layout.enable_eecg_components(window)
        window.force_focus()
        return

    loads_by_user_count = []

    _, stdout, stderr = my_eecg_conn.client.exec_command("ruptime -aur")
    for line in stdout:
        if "up" in line:
            numbers = re.findall(r"[-+]?\d*\.\d+|\d+", line)
            loads_by_user_count.append([numbers[0], numbers[-4], numbers[-3], numbers[-2], numbers[-1]])

    layout_eecg_loads = [
        [
            sg.Text("Command",
                    font=layout.FONT_HELVETICA_16),
            sg.Input(default_text="ruptime -aur",
                     font=layout.FONT_HELVETICA_16,
                     disabled=True)
        ],
        [
            sg.Table(loads_by_user_count,
                     font=layout.FONT_HELVETICA_16,
                     headings=["Machine #", "User Count", "1-min Avg", "5-min Avg", "15-min Avg"],
                     select_mode=sg.TABLE_SELECT_MODE_BROWSE,
                     enable_events=True,
                     key="-EECG_LOADS_TABLE-")
        ],
        [
            sg.Column(
                [
                    [
                        sg.Button(
                            "Select",
                            font=layout.FONT_HELVETICA_16,
                            button_color=layout.COLOR_EECG_RANDOM_PORT_BUTTON,
                            key="-EECG_SELECT_MACHINE-"
                        )
                    ]
                ],
                justification="right"
            )
        ]
    ]

    chosen_machine_num = None

    window_loads = sg.Window("EECG Machine Loads", layout=layout_eecg_loads).finalize()
    while True:
        event_loads, values_loads = window_loads.read()
        if event_loads == sg.WIN_CLOSED or event_loads == 'Exit':
            break
        elif event_loads == "-EECG_SELECT_MACHINE-" and values_loads["-EECG_LOADS_TABLE-"]:
            chosen_machine_num = loads_by_user_count[values_loads["-EECG_LOADS_TABLE-"][0]][0]
            print(chosen_machine_num)
            break

    window_loads.close()

    if chosen_machine_num is not None:
        window["-EECG_MACHINE_NUM-"](chosen_machine_num)

    layout.enable_eecg_components(window)
    window.force_focus()


def cb_ecf_connect(window, values):
    print("Callback: cb_ecf_connect")

    layout.disable_ecf_components(window)
    if not login_ecf(window, values):
        layout.enable_ecf_components(window)
        window.force_focus()
        return

    launch_vnc(values["-SELECT_VIEWER-"], "ECF", 2000)
    my_profile.save_profile("ECF", values["-SELECT_VIEWER-"])


def cb_eecg_reset_no(window, **kwargs):
    window["-EECG_RESET_NO-"](my_profile.eecg_vnc_passwd_exist)
    window["-EECG_RESET_YES-"](not my_profile.eecg_vnc_passwd_exist)
    window["-EECG_VNC_PASSWD_COL-"](visible=not my_profile.eecg_vnc_passwd_exist)
    window["-EECG_VNC_PASSWD-"]("", disabled=my_profile.eecg_vnc_passwd_exist)


def cb_eecg_reset_yes(window, **kwargs):
    window["-EECG_RESET_NO-"](False)
    window["-EECG_RESET_YES-"](True)
    window["-EECG_VNC_PASSWD_COL-"](visible=True)
    window["-EECG_VNC_PASSWD-"](disabled=False)


def cb_switch_intf(window, values):
    if values["-LAB_INTF-"] == "EECG":
        window["-EECG_BUTTONS-"](visible=True)
        window["-ECF_CONNECT-"](visible=False)
    elif values["-LAB_INTF-"] == "ECF":
        window["-EECG_BUTTONS-"](visible=False)
        window["-ECF_CONNECT-"](visible=True)
    else:
        window["-EECG_BUTTONS-"](visible=False)
        window["-ECF_CONNECT-"](visible=False)


def cb_delete_all(**kwargs):
    delete_all = sg.popup_yes_no("Do you want to delete all stored credentials \n"
                                 "on this device and exit UG_Remote? ",
                                 title="Reset Confirmation")
    if delete_all == "Yes":
        try:
            os.remove(VNC_PASSWD_PATH)
            os.remove(PROFILE_FILE_PATH)
        except OSError:
            pass

        os._exit(0)


def cb_open_junhao_ca(**kwargs):
    webbrowser.open("https://junhao.ca")
