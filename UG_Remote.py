import sys
import os
if getattr(sys, 'frozen', False):
    sys.stdout = open(os.path.join(sys._MEIPASS, "error.log"), 'w')

import base64
import json
import re
import threading
import PySimpleGUI as sg
import paramiko

import forward_and_launch as fl


REFRESH_BUTTON_ICON_PATH = "Gnome-view-refresh-20x20.png"
PROFILE_FILE_PATH = "profile.json"
if getattr(sys, 'frozen', False):
    REFRESH_BUTTON_ICON_PATH = os.path.join(sys._MEIPASS, REFRESH_BUTTON_ICON_PATH)
    PROFILE_FILE_PATH = os.path.join(sys._MEIPASS, PROFILE_FILE_PATH)

ssh_authenticated = False
profile_loaded = False
saved_username = None
saved_password = None
last_srv = None


def save_profile(username=None, ug_passwd=None, last_srv=None, only_update_srv=False):
    if only_update_srv:
        with open(PROFILE_FILE_PATH, "r+") as infile:
            json_data = json.load(infile)
            json_data['last_srv'] = last_srv
            infile.write(json_data)
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
except FileNotFoundError:
    profile_loaded = False

global_used_vncports_lst = []
global_ports_by_me_lst = []

def update_used_ports(window, username, ug_passwd, srv_num):
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
        sg.Radio('No', "RESET", font='Helvetica 20', default=True, enable_events=True, key="-DONT_RESET-"),
        sg.Radio('Yes, VNC Password:', "RESET", font='Helvetica 20', enable_events=True, key="-PLZ_RESET-"),

    ],
    [
        sg.Input(size=(37, 1), font='Helvetica 20', password_char='*', enable_events=True, key="-VNC_PASSWD-",
                 visible=False),
    ],
]

port_column = []
for i in range(10):
    new_port_row = []
    for j in range(10):
        port_num = i * 10 + j
        if port_num == 0:
            port_but = sg.Button("", image_filename=REFRESH_BUTTON_ICON_PATH, border_width=0,size=(2, 1), font='Helvetica 16 bold', tooltip="Login and Refresh Ports Status",
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
        sg.Text("Status: ", size=(78, 1), background_color="light grey", text_color="black", key="-STATUS-")
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


window = sg.Window("UG Remote", layout).finalize()
if profile_loaded:
    update_used_ports(window, saved_username, saved_password, last_srv)

fl_thread = None



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
            update_used_ports(window, username, passwd, inquiring_srv_num)

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
            for elem_name in window.AllKeysDict:
                if isinstance(elem_name, str) and "-PORT" in elem_name:
                    window[elem_name].update(disabled=True)
                else:
                    pass
            window["-MACHINE_NUM-"].update(disabled=True)
            window["-USERNAME-"].update(disabled=True)
            window["-UG_PASSWD-"].update(disabled=True)
            window["-DONT_RESET-"].update(disabled=True)
            window["-PLZ_RESET-"].update(disabled=True)
            window["-VNC_PASSWD-"].update(disabled=True)

            save_profile(only_update_srv=True, last_srv=machine_num)
            fl_thread = threading.Thread(target=fl.forward_and_launch, args=(machine_num, port_num, username, passwd))
            fl_thread.start()


    elif event == "-DONT_RESET-" or event == "-PLZ_RESET-":
        if values["-DONT_RESET-"]:
            window["-VNC_PASSWD-"].update(visible=False)
        else:
            window["-VNC_PASSWD-"].update(visible=True)

window.close()
os._exit(0)
