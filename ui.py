import PySimpleGUI as sg

from path_names import *

MACHINES = list(range(51, 76))
MACHINES.extend(range(132, 181))
MACHINES.extend(range(201, 252))
srv_usrname_passwd_col = [
    [
        sg.Text("UG Machine #", size=(12, 1), font='Helvetica 20'),
        sg.Text("ug", font='Helvetica 20'),
        sg.Combo(MACHINES, font='Helvetica 20', enable_events=True, key="-MACHINE_NUM-"),
        sg.Text(".eecg.toronto.edu", font='Helvetica 20'),
    ],
    [sg.HSeparator(pad=(1, 16))],
    [
        sg.Text("Username", size=(12, 1), font='Helvetica 20'),
        sg.Input(size=(24, 1), font='Helvetica 20', enable_events=True, key="-USERNAME-"),
    ],
    [
        sg.Text("UG Password", size=(12, 1), font='Helvetica 20'),
        sg.Input(size=(24, 1), font='Helvetica 20', password_char='*', enable_events=True,
                 key="-UG_PASSWD-"),
    ],
    [
        sg.Text("Reset Profile", size=(12, 1), font='Helvetica 20'),
        sg.Radio('No', "RESET", font='Helvetica 20', default=False, enable_events=True,
                 key="-DONT_RESET-"),
        sg.Radio('Yes, VNC Password:', "RESET", font='Helvetica 20', default=False,
                 enable_events=True,
                 key="-PLZ_RESET-"),

    ],
    [
        sg.Input(size=(37, 1), font='Helvetica 20', password_char='*', enable_events=True, key="-VNC_PASSWD-"),
    ],
]

port_column = []
for i in range(10):
    new_port_row = []
    for j in range(10):
        port_num = i * 10 + j
        if port_num == 0:
            port_but = sg.Button("", image_filename=REFRESH_BUTTON_ICON_PATH, image_size=(32, 32), size=(2, 1),
                                 font='Helvetica 16 bold', tooltip="Login and Refresh Ports Status",
                                 button_color=("white", "cyan"), enable_events=True, key="-REFRESH-")
        else:
            port_but = sg.Button(str(port_num), size=(2, 1), font='Helvetica 16 bold',
                                 enable_events=True, disabled=True, key="-PORT" + str(port_num) + "-")
        new_port_row.append(port_but)
    port_column.append(new_port_row)

# Full Layout
layout = [
    [
        sg.Column(srv_usrname_passwd_col),
        sg.VSeperator(key="-VSEP-"),
        sg.Column(port_column, key="-PRTCOL-"),
    ],
    [
        sg.Text("Status:%s" % (' ' * 100), auto_size_text=True, background_color="light grey", text_color="black",
                key="-STATUS-")
    ],
    [
        sg.Text(
            "TigerVNC Viewer - Copyright (C) 2009-2020 TigerVNC Team (incomplete, https://github.com/TigerVNC/tigervnc)",
            tooltip="Open Source Software Released under GNU GENERAL PUBLIC LICENSE V2",
            background_color="white",
            font='Helvetica 12',
            enable_events=True,
            text_color="black", key="-TVNC_COPYRIGHT-")
    ],
    [
        sg.Text("UG_Remote - Copyright (C) Junhao Liao 2020 (https://junhao.ca)",
                tooltip="Open Source Python Script. No warranty provided. ",
                background_color="white",
                font='Helvetica 12',
                enable_events=True,
                text_color="black", key="-JL_COPYRIGHT-")
    ]
]
