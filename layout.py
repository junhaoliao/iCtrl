import PySimpleGUI as sg

import machines
from path_names import *

FONT_HELVETICA_16 = ("Helvetica", 16)
FONT_HELVETICA_16_BOLD = ("Helvetica", 16, "bold")
FONT_ARIAL_12 = ("Arial", 12)
FONT_ARIAL_12_BOLD = ("Arial", 12, "bold")

COLOR_REFRESH_BUTTON = ("white", "#FF7F1D")
COLOR_USED_BY_ME_BUTTON = ("#00619F", "#FFE74D")
COLOR_BUSY_BUTTON = ("white", "#F5577C")
COLOR_FREE_BUTTON = ("white", "#88B04B")

if platform.system() == "Windows":
    sg.theme('Default1')
elif platform.system() == "Darwin":
    sg.theme('LightGrey1')
layout = [
    [
        sg.Column(
            [
                [
                    sg.Image(
                        UG_REMOTE_ICON_PATH
                    )
                ]
            ],
            justification="center"
        )
    ],
    [sg.HSeparator(pad=(1, 16))],
    [
        sg.Text("UG Machine #",
                font=FONT_HELVETICA_16, size=(12, 1)),
        sg.Text("ug",
                font=FONT_HELVETICA_16),
        sg.Combo(machines.MACHINES,
                 font=FONT_HELVETICA_16,
                 key="-MACHINE_NUM-"),
        sg.Text(".eecg.toronto.edu",
                font=FONT_HELVETICA_16),
    ],
    [sg.HSeparator(pad=(1, 16))],
    [
        sg.Text("Username",
                font=FONT_HELVETICA_16, size=(12, 1)),
        sg.Input(font=FONT_HELVETICA_16, size=(24, 1),
                 key="-USERNAME-"),
    ],
    [
        sg.Text("UG Password",
                font=FONT_HELVETICA_16, size=(12, 1)),
        sg.Input(font=FONT_HELVETICA_16, size=(24, 1),
                 password_char='*',
                 key="-UG_PASSWD-"),
    ],
    [
        sg.Text("Reset Profile",
                font=FONT_HELVETICA_16, size=(12, 1)),
        sg.Radio('No', "RESET", default=False,
                 font=FONT_HELVETICA_16,
                 enable_events=True,
                 key="-RESET_NO-"),
        sg.Radio('Yes', "RESET", default=True,
                 font=FONT_HELVETICA_16,
                 enable_events=True,
                 key="-RESET_YES-")
    ],
    [
        sg.Column(
            [
                [
                    sg.Text("VNC Password",
                            font=FONT_HELVETICA_16, size=(12, 1)),
                    sg.Input(size=(24, 1), font=FONT_HELVETICA_16, password_char='*',
                             key="-VNC_PASSWD-"),
                ]
            ],
            pad=(0,0),
            key="-VNC_PASSWD_COL-"
        )
    ],
    [sg.HSeparator(pad=(1, 16))],
    [
        sg.Column(
            [
                [
                    sg.Button("Select Port",
                              font=FONT_ARIAL_12_BOLD,
                              button_color=("#3c4043", "#f8f9fa"),
                              key="-SELECT_PORT-"),
                    sg.Button("I'm Feeling Lucky",
                              font=FONT_ARIAL_12_BOLD,
                              button_color=("white", "#4285f4"),
                              key="-RANDOM_PORT-"),
                ]
            ],
            justification='center'
        )

    ]
]


def disable_all_components(window):
    window["-MACHINE_NUM-"](disabled=True)
    window["-USERNAME-"](disabled=True)
    window["-UG_PASSWD-"](disabled=True)
    window["-RESET_NO-"](disabled=True)
    window["-RESET_YES-"](disabled=True)
    window["-VNC_PASSWD-"](disabled=True)
    window["-SELECT_PORT-"](disabled=True)
    window["-RANDOM_PORT-"](disabled=True)


def enable_all_components(window):
    window["-MACHINE_NUM-"](disabled=False)
    window["-USERNAME-"](disabled=False)
    window["-UG_PASSWD-"](disabled=False)
    window["-RESET_NO-"](disabled=False)
    window["-RESET_YES-"](disabled=False)
    window["-VNC_PASSWD-"](disabled=False)
    window["-SELECT_PORT-"](disabled=False)
    window["-RANDOM_PORT-"](disabled=False)
