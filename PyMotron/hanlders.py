import base64
import json

from globals import *


# TODO: add a function to send back errors to the client
#  can catch the exception in handler_main and send the message over

def handle_sync(value):
    print("handle_sync:", value)
    srv_msg = {"sessions": USER_PROFILE.query_sessions()}
    srv_msg_json = json.dumps(srv_msg)
    IPC_SEND.send_string(srv_msg_json)


def handle_login(value):
    """
    :param value: the value of the message
    e.g.
    {"session_idx": 0, "server":"", "username": "", "passwd": "", "save_key": false}
    :return: None
    """
    print("handle_login:", value)

    session_idx = value["session_idx"]
    if type(session_idx) is not int:
        raise TypeError(f"handle_login: Invalid type({session_idx})={type(session_idx)}")
    elif session_idx < 0 or session_idx >= len(USER_PROFILE["sessions"]):
        raise IndexError(f"handle_login: Invalid session_idx={session_idx}")

    server = value["server"]
    if type(server) is not str:
        raise TypeError(f"handle_login: Invalid type({server})={type(server)}")
    # TODO: refactor the existing server validity checking logics into a function in class UGUserProfile
    # elif server not in USER_PROFILE["sessions"][session_idx]["servers"]:
    #     raise ValueError(f"handle_login: Invalid server={server}")

    username = value["username"]
    if type(username) is not str:
        raise TypeError(f"handle_login: Invalid type({username})={type(username)}")

    passwd = value["passwd"]
    if passwd is not None and type(passwd) is not str:
        raise TypeError(f"handle_login: Invalid type({passwd})={type(passwd)}")

    save_key = value["save_key"]
    if type(save_key) is not bool:
        raise TypeError(f"handle_login: Invalid type({save_key})={type(save_key)}")
    # TODO: make sure to handle the key saving

    # TODO: check the relation between save_key and passwd

    if passwd is not None:
        SESSION[session_idx].connect(hostname=server, username=username, passwd=passwd)
    else:
        # TODO: support login with keys
        pass

    # TODO: send back login_ack


def handle_shell(value):
    SESSION[0].invoke_shell(IPC_SEND)


def handle_interact(value):
    SESSION[0].shell_send_data(value)
