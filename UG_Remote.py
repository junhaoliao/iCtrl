import sys
import os

import base64
import json
import re
import threading
import PySimpleGUI as sg
import paramiko

import forward_and_launch as fl

from path_names import *

ssh_authenticated = False
global_set_vncpasswd = False
profile_loaded = False
saved_username = None
saved_password = None
last_srv = None


def save_profile(username=None, ug_passwd=None, last_srv=None, only_update_srv=False):
    if only_update_srv:
        with open(PROFILE_FILE_PATH, "r+") as infile:
            json_data = json.load(infile)
            json_data['last_srv'] = last_srv
    else:
        with open(PROFILE_FILE_PATH, 'w') as outfile:
            json_data = json.dumps(
                {
                    'saved_username': username,
                    'saved_password': base64.b64encode(ug_passwd.encode('ascii')).decode('ascii'),
                    'last_srv': last_srv,
                }
            )
            outfile.write(json_data)

try:
    with open(PROFILE_FILE_PATH, "r") as infile:
        json_data = json.load(infile)
        saved_username = json_data['saved_username']
        saved_password = json_data['saved_password']
        saved_password = base64.b64decode(saved_password).decode('ascii')
        last_srv = json_data['last_srv']
        profile_loaded = True
except (FileNotFoundError, json.decoder.JSONDecodeError):
    global_set_vncpasswd = True
    profile_loaded = False

global_used_vncports_lst = []
global_ports_by_me_lst = []

def update_used_ports(window, username, ug_passwd, srv_num, vnc_passwd_input=None):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.WarningPolicy())
    try:
        client.connect('ug%i.eecg.toronto.edu' % srv_num, username=username, password=ug_passwd)
    except OSError:
        window["-STATUS-"].update("Status: UG Server %s unreachable. Please check you network or use another server." %srv_num)
        return

    # save username and passwd
    global ssh_authenticated
    ssh_authenticated = True
    if global_set_vncpasswd:
        print("trying to reset vnc passwd")
        reset_cmd_lst = [
            "killall Xtigervnc",
            "rm -rf ~/.vnc",
            "mkdir ~/.vnc",
            "echo '%s'| vncpasswd -f > ~/.vnc/passwd" % vnc_passwd_input,
            "chmod 600 ~/.vnc/passwd",
        ]
        _,stdout,stderr = client.exec_command(";".join(reset_cmd_lst))
        print(";".join(reset_cmd_lst))
        for line in stdout:
            print(line)
        for line in stderr:
            print(line)
        _,stdout,_ = client.exec_command("echo '%s'| vncpasswd -f"%vnc_passwd_input)
        with open(VNC_PASSWD_PATH, "wb") as vnc_passwd_file:
            vnc_passwd_file.write(stdout.read())

    save_profile(username=username, ug_passwd=ug_passwd, last_srv=srv_num)

    # formulate the vnc port scanning cmd
    scan_vncport_cmd_lst = []
    for port in range(5900, 5999):
        scan_vncport_cmd_lst.append('sh -c "nc -z -nv 127.0.0.1 ' + str(port) + ' 2>&1" | grep \'open\|succeeded\'')
    scan_vncport_cmd = ";".join(scan_vncport_cmd_lst)

    # send out the vnc port scanning cmd
    _, stdout, _ = client.exec_command(scan_vncport_cmd)

    # list containing used vnc ports
    used_vncports_lst = []
    for line in stdout:
        if "open" in line:  # on other machines
            line = line.replace('(UNKNOWN) [127.0.0.1] ', '')  # remove prefix
            line = line.replace(' (?) open', '')  # remove suffix
        elif "succeeded" in line:  # on ug250 and ug251
            line = line.replace('Connection to 127.0.0.1 ', '')  # remove prefix
            line = line.replace(' port [tcp/*] succeeded!', '')  # remove suffix
        else:
            print("Unexpected output: ", line)

        this_used_port = int(line) - 5900
        used_vncports_lst.append(this_used_port)

    # use the API by vncserver to see what ports are created by me
    _, stdout, _ = client.exec_command('vncserver -list')

    ports_by_me_lst = []
    for line in stdout:
        x = re.findall(r'\d+', line)
        if len(x) != 0:
            ports_by_me_lst.append(int(x[0]))

    client.close()

    global global_used_vncports_lst
    global global_ports_by_me_lst
    global_used_vncports_lst = used_vncports_lst
    global_ports_by_me_lst = ports_by_me_lst

    for port_num in range(1, 100):
        port_but_key = "-PORT" + str(port_num) + "-"
        busy = (port_num in used_vncports_lst)
        by_me = (port_num in ports_by_me_lst)
        if by_me and busy:
            window[port_but_key].update(button_color=('black', 'yellow'), disabled=False)
            window[port_but_key].set_tooltip('Created by Me, Busy')
        elif busy:
            window[port_but_key].update(button_color=('white', 'red'), disabled=False)
            window[port_but_key].set_tooltip('Likely Used by Others, Busy')
        else:
            window[port_but_key].update(button_color=('white', 'green'), disabled=False)
            window[port_but_key].set_tooltip('Free')

    window["-STATUS-"].update("Status: Ports status refreshed. ")

    return

MACHINES = list(range(51, 76))
MACHINES.extend(range(132, 181))
MACHINES.extend(range(201, 252))
srv_usrname_passwd_col = [
    [
        sg.Text("UG Machine #", size=(12, 1), font='Helvetica 20'),
        sg.Text("ug", font='Helvetica 20'),
        sg.Combo(MACHINES, default_value=last_srv, font='Helvetica 20', enable_events=True, key="-MACHINE_NUM-"),
        sg.Text(".eecg.toronto.edu", font='Helvetica 20'),
    ],
    [sg.HSeparator(pad=(1, 16))],
    [
        sg.Text("Username", size=(12, 1), font='Helvetica 20'),
        sg.Input(size=(24, 1), default_text=saved_username, font='Helvetica 20', enable_events=True, key="-USERNAME-"),
    ],
    [
        sg.Text("UG Password", size=(12, 1), font='Helvetica 20'),
        sg.Input(size=(24, 1), default_text=saved_password, font='Helvetica 20', password_char='*', enable_events=True,
                 key="-UG_PASSWD-"),
    ],
    [
        sg.Text("Reset Profile", size=(12, 1), font='Helvetica 20'),
        sg.Radio('No', "RESET", font='Helvetica 20', default=profile_loaded, enable_events=True, key="-DONT_RESET-"),
        sg.Radio('Yes, VNC Password:', "RESET", font='Helvetica 20', default=not profile_loaded, enable_events=True, key="-PLZ_RESET-"),

    ],
    [
        sg.Input(size=(37, 1), font='Helvetica 20', password_char='*', enable_events=True, key="-VNC_PASSWD-",
                 visible=not profile_loaded),
    ],
]

port_column = []
for i in range(10):
    new_port_row = []
    for j in range(10):
        port_num = i * 10 + j
        if port_num == 0:
            port_but = sg.Button("", image_filename=REFRESH_BUTTON_ICON_PATH, image_size=(32,32),size=(2, 1), font='Helvetica 16 bold', tooltip="Login and Refresh Ports Status",
                                 button_color=("white","cyan"),enable_events=True, key="-REFRESH-")
        else:
            port_but = sg.Button(str(port_num), size=(2, 1), font='Helvetica 16 bold',
                                 enable_events=True, disabled=True, key="-PORT" + str(port_num) + "-")
        new_port_row.append(port_but)
    port_column.append(new_port_row)

# ----- Full layout -----
layout = [
    [
        sg.Column(srv_usrname_passwd_col),
        sg.VSeperator(key="-VSEP-"),
        sg.Column(port_column, key="-PRTCOL-"),
    ],
    [
        sg.Text("Status: ", size=(130, 1), background_color="light grey", text_color="black", key="-STATUS-")
    ]
]


def get_srv_usrname_passwd(sg_values):
    machine_num_str = sg_values["-MACHINE_NUM-"]
    username_str = sg_values["-USERNAME-"]
    passwd_str = sg_values["-UG_PASSWD-"]

    if machine_num_str == "":
        window["-STATUS-"].update("Status: machine number cannot be empty")
        return None
    elif username_str == "":
        window["-STATUS-"].update("Status: username cannot be empty")
        return None
    elif passwd_str == "":
        window["-STATUS-"].update("Status: password cannot be empty")
        return None

    # ensure the user doesn't input a machine number out of range
    try:
        machine_num = int(machine_num_str)
        if machine_num not in MACHINES:
            raise ValueError
    except ValueError:
        window["-STATUS-"].update("Status: machine number not supported")
        return None

    global_status = "".join(["ssh ", username_str, "@ug", str(machine_num), ".eecg.toronto.edu"])
    return machine_num, username_str, passwd_str


window = sg.Window("UG Remote", layout, size=(1080,520)).finalize()
if profile_loaded:
    update_used_ports(window, saved_username, saved_password, last_srv)

fl_thread = None

# TODO: not fully reliable, should check back later
def vnc_passwd_usable(vnc_passwd):
    if "'" in vnc_passwd:
        return False, "Error: VNC password cannot contain symbol (')"
    elif len(vnc_passwd) < 6:
        return False, "Error: VNC password should have length of 6 - 8"
    elif len(vnc_passwd) > 8:
        return True, "Warning: VNC password with length longer than 8 will be truncated"

    return True, None

def disable_port_buts(window):
    for elem_name in window.AllKeysDict:
        if isinstance(elem_name, str) and "-PORT" in elem_name:
            window[elem_name].update(disabled=True)


# Run the Event Loop
while True:
    event, values = window.read()
    print(event)
    if event == "Exit" or event == sg.WIN_CLOSED:
        break
    elif event == "-MACHINE_NUM-":
        inquiring_srv_num = values["-MACHINE_NUM-"]
        if ssh_authenticated:
            update_used_ports(window, saved_username, saved_password, inquiring_srv_num)
    elif event == "-REFRESH-":
        inquiring_srv_num = values["-MACHINE_NUM-"]

        srv_usrname_passwd = get_srv_usrname_passwd(values)
        if srv_usrname_passwd is None:
            print("user hasn't enter all fields")
        else:
            machine_num, username, passwd = srv_usrname_passwd
            input_vnc_passwd, usable = None, True
            if global_set_vncpasswd:
                input_vnc_passwd = values["-VNC_PASSWD-"]
                usable, errmsg = vnc_passwd_usable(input_vnc_passwd)
            if usable:
                update_used_ports(window, username, passwd, inquiring_srv_num, input_vnc_passwd)
            else:
                window["-STATUS-"].update(errmsg)

    elif "-PORT" in event:
        port_str = re.findall(r'\d+', event)
        port_num = None

        if port_str:
            port_num = int(port_str[0])
        else:
            raise IndexError("No such port exist from event: ", event)

        srv_usrname_passwd = get_srv_usrname_passwd(values)
        if srv_usrname_passwd is None:
            print("user hasn't enter all fields")
        else:
            machine_num, username, passwd = srv_usrname_passwd
            disable_port_buts(window)
            window["-REFRESH-"].update(disabled=True)
            window["-MACHINE_NUM-"].update(disabled=True)
            window["-USERNAME-"].update(disabled=True)
            window["-UG_PASSWD-"].update(disabled=True)
            window["-DONT_RESET-"].update(disabled=True)
            window["-PLZ_RESET-"].update(disabled=True)
            window["-VNC_PASSWD-"].update(disabled=True)

            window["-STATUS-"].update("Status: VNC session starting... To terminate, close this window. ")

            save_profile(only_update_srv=True, last_srv=machine_num)
            fl_thread = threading.Thread(target=fl.forward_and_launch, args=(machine_num, port_num, username, passwd))
            fl_thread.start()


    elif event == "-DONT_RESET-" or event == "-PLZ_RESET-":
        if values["-DONT_RESET-"]:
            if profile_loaded:
                global_set_vncpasswd = False
                window["-VNC_PASSWD-"].update(visible=False)
            else:
                global_set_vncpasswd = True
                window["-DONT_RESET-"].update(False)
                window["-PLZ_RESET-"].update(True)
                window["-STATUS-"].update("Status: Please reset your vnc password. ")
        else:
            global_set_vncpasswd = True
            profile_loaded = False
            disable_port_buts(window)
            window["-VNC_PASSWD-"].update(visible=True)


window.close()
os._exit(0)
