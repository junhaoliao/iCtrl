import PySimpleGUI as sg

import machines
import updater
from path_names import *

UG_REMOTE_ICON_BASE64 = b'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'

FONT_HELVETICA_12 = ("Helvetica", 12)
FONT_HELVETICA_16 = ("Helvetica", 16)
FONT_HELVETICA_16_BOLD = ("Helvetica", 16, "bold")
FONT_ARIAL_12 = ("Arial", 12)
FONT_ARIAL_12_BOLD = ("Arial", 12, "bold")

COLOR_EECG_REFRESH_BUTTON = ("white", "#FF7F1D")
COLOR_EECG_USED_BY_ME_BUTTON = ("#00619F", "#FFE74D")
COLOR_EECG_BUSY_BUTTON = ("white", "#F5577C")
COLOR_EECG_FREE_BUTTON = ("white", "#88B04B")
COLOR_EECG_SELECT_PORT_BUTTON = ("white", "#F5577C")
COLOR_EECG_CHECK_LOADS_BUTTON = ("white", "#88B04B")
COLOR_EECG_RANDOM_PORT_BUTTON = ("white", "#4285f4")

COLOR_ECF_CONNECT_BUTTON = ("white", "#4285f4")

if platform.system() == "Windows":
    sg.theme('Default1')
elif platform.system() == "Darwin":
    sg.theme('LightGrey1')

eecg_layout = [
    [sg.Text("", font=("Arial", 3))],
    [
        sg.Text("EECG Machine",
                font=FONT_HELVETICA_16, size=(16, 1),
                tooltip="Please select one with lighter loads. \n"
                        "You may check how many people are using this machine\n"
                        " by entering the credentials and clicking \"Select Port\""),
        sg.Text("ug",
                font=FONT_HELVETICA_16, pad=(0, 0)
                ),
        sg.Combo(machines.MACHINES,
                 font=FONT_HELVETICA_16, pad=(0, 0),
                 key="-EECG_MACHINE_NUM-"),
        sg.Text(".eecg.toronto.edu",
                font=FONT_HELVETICA_16, pad=(0, 0)
                ),
    ],
    [
        sg.Text("Username",
                font=FONT_HELVETICA_16, size=(16, 1),
                tooltip="Same as your UTORid"),
        sg.Input(font=FONT_HELVETICA_16, size=(20, 1), pad=(0, 0),
                 key="-EECG_USERNAME-"),
        sg.Text("", pad=(14, 0))
    ],
    [
        sg.Text("EECG Password",
                font=FONT_HELVETICA_16, size=(16, 1),
                tooltip="By default, it is your student number"),
        sg.Input(font=FONT_HELVETICA_16, size=(20, 1), pad=(0, 0),
                 password_char='*',
                 key="-EECG_PASSWD-"),
    ],
    [
        sg.Text("Reset VNC",
                font=FONT_HELVETICA_16, size=(16, 1),
                tooltip="You will need to setup a VNC password for initialization.\n"
                        "The password length should be between 6 and 8"),
        sg.Radio('No', "RESET", default=False,
                 font=FONT_HELVETICA_16,
                 tooltip="You will need to setup a VNC password for initialization.\n"
                         "The password length should be between 6 and 8",
                 enable_events=True,
                 key="-EECG_RESET_NO-"),
        sg.Radio('Yes', "RESET", default=True,
                 font=FONT_HELVETICA_16,
                 tooltip="You will need to setup a VNC password for initialization.\n"
                         "The password length should be between 6 and 8",
                 enable_events=True,
                 key="-EECG_RESET_YES-")
    ],
    [
        sg.Column(
            [
                [
                    sg.Text("New VNC Password",
                            font=FONT_HELVETICA_16, size=(16, 1),
                            tooltip="You will need to setup a VNC password for initialization.\n"
                                    "The password length should be between 6 and 8"),
                    sg.Input(font=FONT_HELVETICA_16, size=(20, 1), pad=(0, 0),
                             password_char='*',
                             key="-EECG_VNC_PASSWD-"),
                ]
            ],
            pad=(0, 0),
            key="-EECG_VNC_PASSWD_COL-"
        )
    ]
]

ecf_layout = [
    [sg.Text("", font=("Arial", 3))],
    [
        sg.Text("Username",
                font=FONT_HELVETICA_16, size=(16, 1),
                tooltip="Same as your UTORid"),
        sg.Input(font=FONT_HELVETICA_16, size=(20, 1), pad=(0, 0),
                 key="-ECF_USERNAME-"),
    ],
    [
        sg.Text("ECF Password",
                font=FONT_HELVETICA_16, size=(16, 1),
                tooltip="The one that must be 16 characters or longer"),
        sg.Input(font=FONT_HELVETICA_16, size=(20, 1), pad=(0, 0),
                 password_char='*',
                 key="-ECF_PASSWD-"),
    ],
]

eecg_buttons = sg.Column(
    [
        [
            sg.Button("Select Port",
                      font=FONT_ARIAL_12_BOLD,
                      button_color=COLOR_EECG_SELECT_PORT_BUTTON,
                      tooltip="Pick your favourite port",
                      key="-EECG_SELECT_PORT-"),
            sg.Button("Check Loads",
                      font=FONT_ARIAL_12_BOLD,
                      button_color=COLOR_EECG_CHECK_LOADS_BUTTON,
                      tooltip="Pick the lightest loaded machine by user count",
                      key="-EECG_CHECK_LOADS-"),
            sg.Button("Connect",
                      font=FONT_ARIAL_12_BOLD,
                      button_color=COLOR_EECG_RANDOM_PORT_BUTTON,
                      tooltip="Connect to the last session or create a new one",
                      key="-EECG_RANDOM_PORT-"),

        ]
    ],
    pad=(0, 0),
    justification="center",
    key="-EECG_BUTTONS-"
)

misc_layout = [
    [
        sg.Frame(
            " Reset ",
            [
                [
                    sg.Button("Delete all profiles",
                              font=FONT_ARIAL_12_BOLD,
                              button_color=("white", "red"),
                              key="-DELETE_ALL-"
                              )
                ]
            ],
            font=FONT_HELVETICA_16,
            element_justification="center",
        ),
        sg.Frame(
            " Viewer ",
            [
                [
                    sg.Combo(["TigerVNC", "RealVNC"],
                             font=FONT_HELVETICA_16,
                             readonly=True,
                             key="-SELECT_VIEWER-")
                ]
            ],
            font=FONT_HELVETICA_16,
            element_justification="center",
        )
    ],
    [
        sg.Frame(
            " About ",
            [
                [
                    sg.Text(
                        "UG_Remote v%d.%d.%d\n"
                        "Copyright (C) 2020-2021 Junhao Liao" % updater.CURRENT_VER,
                        font=FONT_HELVETICA_16,
                        enable_events=True,
                        key="-COPYRIGHT-"
                    )
                ],
                [
                    sg.Text(
                        "https://junhao.ca",
                        font=FONT_HELVETICA_16,
                        text_color="blue",
                        tooltip="Click to visit junhao.ca",
                        enable_events=True,
                        key="-OPEN_WEBSITE-"
                    )
                ]
            ],
            font=FONT_HELVETICA_16
        )
    ]
]

layout = [
    [
        sg.Column(
            [
                [
                    sg.Image(
                        data=UG_REMOTE_ICON_BASE64
                    )
                ]
            ],
            justification="center"
        )
    ],
    [
        sg.TabGroup(
            [
                [
                    sg.Tab('EECG', eecg_layout),
                    sg.Tab('ECF', ecf_layout),
                    sg.Tab("Misc", misc_layout)
                ]
            ],
            font=FONT_HELVETICA_16_BOLD,
            background_color="#eff0f4",
            title_color="#6c6c6e",
            tab_background_color="#eff0f4",
            selected_title_color="#4285f4",
            selected_background_color="#e2e4e7",
            tab_location="center",
            border_width=0,
            enable_events=True,
            key="-LAB_INTF-"
        )
    ],
    [
        sg.Column(
            [
                [
                    eecg_buttons,
                    sg.Button("Connect",
                              visible=False,
                              font=FONT_ARIAL_12_BOLD,
                              button_color=COLOR_ECF_CONNECT_BUTTON,
                              key="-ECF_CONNECT-"),
                ]
            ],
            pad=(0, 0),
            justification="center"
        )
    ]
]


def enable_eecg_components(window):
    window["-EECG_MACHINE_NUM-"](disabled=False)
    window["-EECG_USERNAME-"](disabled=False)
    window["-EECG_PASSWD-"](disabled=False)
    window["-EECG_RESET_NO-"](disabled=False)
    window["-EECG_RESET_YES-"](disabled=False)
    window["-EECG_VNC_PASSWD-"](disabled=False)
    window["-EECG_SELECT_PORT-"](disabled=False)
    window["-EECG_RANDOM_PORT-"](disabled=False)
    window["-EECG_CHECK_LOADS-"](disabled=False)


def disable_eecg_components(window):
    window["-EECG_MACHINE_NUM-"](disabled=True)
    window["-EECG_USERNAME-"](disabled=True)
    window["-EECG_PASSWD-"](disabled=True)
    window["-EECG_RESET_NO-"](disabled=True)
    window["-EECG_RESET_YES-"](disabled=True)
    window["-EECG_VNC_PASSWD-"](disabled=True)
    window["-EECG_SELECT_PORT-"](disabled=True)
    window["-EECG_RANDOM_PORT-"](disabled=True)
    window["-EECG_CHECK_LOADS-"](disabled=True)


def enable_ecf_components(window):
    window["-ECF_USERNAME-"](disabled=False)
    window["-ECF_PASSWD-"](disabled=False)
    window["-ECF_CONNECT-"](disabled=False)


def disable_ecf_components(window):
    window["-ECF_USERNAME-"](disabled=True)
    window["-ECF_PASSWD-"](disabled=True)
    window["-ECF_CONNECT-"](disabled=True)
