import base64
import json

from globals import *


# TODO: add a function to send back errors to the client
#  can catch the exception in handler_main and send the message over

def send_msg(key, value=None):
    srv_msg_json = json.dumps({
        key: value
    })
    IPC_SEND.send_string(srv_msg_json)


def handle_sync(value):
    print("handle_sync:", value)
    send_msg("sync_ack", USER_PROFILE.query_sync())


def handle_query_profiles(value):
    print("handle_query_profiles:", value)
    send_msg("profiles", USER_PROFILE.query_profiles())


def handle_new_session(value):
    print("handle_new_session:", value)
    session = value["session"]
    if type(session) is not str:
        raise TypeError(f"handle_login: Invalid type({session})={type(session)}")

    profile = value["profile"]
    if type(profile) is not str:
        raise TypeError(f"handle_login: Invalid type({profile})={type(profile)}")

    USER_PROFILE.add_new_session(session_name=session, conn_profile=profile)
    CONN[session] = UGConnection()

def handle_login(value):
    """
    :param value: the value of the message
    e.g.
    {"session": "EECG1", "server":"ug250.eecg.toronto.edu", "username": "", "passwd": "", "save_key": false}
    :return: None
    """
    print("handle_login:", value)

    session = value["session"]
    if type(session) is not str:
        raise TypeError(f"handle_login: Invalid type({session})={type(session)}")
    elif session not in CONN:
        raise ValueError(f"handle_login: Invalid session={session}")

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
        try:
            CONN[session].connect(hostname=server, username=username, passwd=passwd)
            send_msg("login_ack", session)
        except Exception as e:
            send_msg("login_ack", "Failed: " + str(e))

    else:
        # TODO: support login with keys
        pass

    # TODO: send back login_ack


def handle_shell(value):
    session = value
    if type(session) is not str:
        raise TypeError(f"handle_shell: Invalid type({session})={type(session)}")
    elif session not in CONN:
        raise ValueError(f"handle_shell: Invalid session={session}")

    CONN[value].invoke_shell(session, IPC_SEND)


def handle_send(value):
    print(value)

    session = value["s"]
    if type(session) is not str:
        raise TypeError(f"handle_send: Invalid type({session})={type(session)}")
    elif session not in CONN:
        raise ValueError(f"handle_send: Invalid session={session}")

    data = value["d"]

    CONN[session].shell_send_data(data)


def handle_sftp_visit(value):
    session = value["session"]
    if type(session) is not str:
        raise TypeError(f"handle_sftp_visit: Invalid type({session})={type(session)}")
    elif session not in CONN:
        raise ValueError(f"handle_sftp_visit: Invalid session={session}")

    remote_path = value["path"]
    if type(remote_path) is not str:
        raise TypeError(f"handle_sftp_visit: Invalid type({remote_path})={type(remote_path)}")

    remote_cwd, file_list = CONN[session].sftp_ls(remote_path)
    send_msg("sftp_cwd", {
        "session": session,
        "dir": remote_cwd,
        "files": file_list
    })


def get_transfer_parameters(value):
    session = value["session"]
    if type(session) is not str:
        raise TypeError(f"get_transfer_parameters: Invalid type({session})={type(session)}")
    elif session not in CONN:
        raise ValueError(f"get_transfer_parameters: Invalid session={session}")

    local_path = value["local"]
    if type(local_path) is not str:
        raise TypeError(f"get_transfer_parameters: Invalid type({local_path})={type(local_path)}")
    # TODO: revisit the need to check whether the local path exists or not

    remote_path = value["remote"]
    if type(remote_path) is not str:
        raise TypeError(f"get_transfer_parameters: Invalid type({remote_path})={type(remote_path)}")

    return session, local_path, remote_path


def handle_sftp_download(value):
    session, local_path, remote_path = get_transfer_parameters(value)
    CONN[session].sftp.get(remote_path, local_path)


def handle_sftp_upload(value):
    session, local_path, remote_path = get_transfer_parameters(value)
    CONN[session].sftp.put(local_path, remote_path)
