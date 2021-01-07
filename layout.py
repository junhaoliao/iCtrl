import PySimpleGUI as sg

import machines
from path_names import *

FONT_HELVETICA_16 = ("Helvetica", 16)
FONT_HELVETICA_16_BOLD = ("Helvetica", 16, "bold")
FONT_ARIAL_12 = ("Arial", 12)
FONT_ARIAL_12_BOLD = ("Arial", 12, "bold")

COLOR_EECG_REFRESH_BUTTON = ("white", "#FF7F1D")
COLOR_EECG_USED_BY_ME_BUTTON = ("#00619F", "#FFE74D")
COLOR_EECG_BUSY_BUTTON = ("white", "#F5577C")
COLOR_EECG_FREE_BUTTON = ("white", "#88B04B")
COLOR_EECG_SELECT_PORT_BUTTON = ("#3c4043", "#f8f9fa")
COLOR_EECG_RANDOM_PORT_BUTTON = ("white", "#4285f4")

COLOR_ECF_CONNECT_BUTTON = ("white", "#4285f4")

if platform.system() == "Windows":
    sg.theme('Default1')
elif platform.system() == "Darwin":
    sg.theme('LightGrey1')

eecg_layout = [
    [
        sg.Text("EECG Machine",
                font=FONT_HELVETICA_16, size=(14, 1)),
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
    [sg.HSeparator(pad=(0, 8), color="white")],
    [
        sg.Text("Username",
                font=FONT_HELVETICA_16, size=(14, 1)),
        sg.Input(font=FONT_HELVETICA_16, size=(20, 1), pad=(0, 0),
                 key="-EECG_USERNAME-"),
    ],
    [
        sg.Text("EECG Password",
                font=FONT_HELVETICA_16, size=(14, 1)),
        sg.Input(font=FONT_HELVETICA_16, size=(20, 1), pad=(0, 0),
                 password_char='*',
                 key="-EECG_PASSWD-"),
    ],
    [
        sg.Text("Reset VNC",
                font=FONT_HELVETICA_16, size=(14, 1)),
        sg.Radio('No', "RESET", default=False,
                 font=FONT_HELVETICA_16,
                 enable_events=True,
                 key="-EECG_RESET_NO-"),
        sg.Radio('Yes', "RESET", default=True,
                 font=FONT_HELVETICA_16,
                 enable_events=True,
                 key="-EECG_RESET_YES-")
    ],
    [
        sg.Column(
            [
                [
                    sg.Text("VNC Password",
                            font=FONT_HELVETICA_16, size=(14, 1)),
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
    [
        sg.Text("Username",
                font=FONT_HELVETICA_16, size=(14, 1)),
        sg.Input(font=FONT_HELVETICA_16, size=(20, 1),
                 key="-ECF_USERNAME-"),
    ],
    [
        sg.Text("ECF Password",
                font=FONT_HELVETICA_16, size=(14, 1)),
        sg.Input(font=FONT_HELVETICA_16, size=(20, 1),
                 password_char='*',
                 key="-ECF_PASSWD-"),
    ],
    # [sg.HSeparator(pad=(1, 16), color="white")],
]

eecg_buttons = sg.Column(
    [
        [
            sg.Button("Select Port",
                      font=FONT_ARIAL_12_BOLD,
                      button_color=COLOR_EECG_SELECT_PORT_BUTTON,
                      key="-EECG_SELECT_PORT-"),
            sg.Button("I'm Feeling Lucky",
                      font=FONT_ARIAL_12_BOLD,
                      button_color=COLOR_EECG_RANDOM_PORT_BUTTON,
                      key="-EECG_RANDOM_PORT-")
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
                    sg.Text(
                        "To lear all stored credentials",
                        font=FONT_HELVETICA_16,
                    )
                ],
                [
                    sg.Button("Delete all profiles",
                              font=FONT_ARIAL_12_BOLD,
                              button_color=("white", "red"),
                              key="-DELETE_ALL-"
                              )
                ]
            ],
            font=FONT_HELVETICA_16,
            # border_width=0
        )
    ],
    [
        sg.Frame(
            " About ",
            [
                [
                    sg.Text(
                        "UG_Remote\n"
                        "Copyright (C) 2020-2021 Junhao Liao",
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
                        enable_events=True,
                        key="-OPEN_WEBSITE-"
                    )
                ]
            ],
            font=FONT_HELVETICA_16,
            size=(200, 200)
        )
    ]

]

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
            selected_title_color="#1a73e8",
            selected_background_color="#e2e4e7",
            tab_location="center",
            enable_events=True,
            border_width=0,
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


def disable_eecg_components(window):
    window["-EECG_MACHINE_NUM-"](disabled=True)
    window["-EECG_USERNAME-"](disabled=True)
    window["-EECG_PASSWD-"](disabled=True)
    window["-EECG_RESET_NO-"](disabled=True)
    window["-EECG_RESET_YES-"](disabled=True)
    window["-EECG_VNC_PASSWD-"](disabled=True)
    window["-EECG_SELECT_PORT-"](disabled=True)
    window["-EECG_RANDOM_PORT-"](disabled=True)


def enable_ecf_components(window):
    window["-ECF_USERNAME-"](disabled=False)
    window["-ECF_PASSWD-"](disabled=False)
    window["-ECF_CONNECT-"](disabled=False)


def disable_ecf_components(window):
    window["-ECF_USERNAME-"](disabled=True)
    window["-ECF_PASSWD-"](disabled=True)
    window["-ECF_CONNECT-"](disabled=True)
