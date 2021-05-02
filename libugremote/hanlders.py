import base64
import json
import os

from globals import *
from paths import *


# TODO: add a function to send back errors to the client
#  can catch the exception in handler_main and send the message over

def send_msg(key, value=None):
    srv_msg_json = json.dumps({
        key: value
    })
    IPC_SEND.send_string(srv_msg_json)


def get_free_port():
    """ return a system assigned free port
    >>> _ = get_free_port()
    """
    import socket
    sock = socket.socket()
    sock.bind(("", 0))
    port = sock.getsockname()[1]
    sock.close()
    return port


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


def rm_private_key(session_name):
    private_key_path = USER_PROFILE["sessions"][session_name]["private_key_path"]
    if private_key_path != "":
        os.remove(private_key_path)
        USER_PROFILE["sessions"][session_name]["private_key_path"] = ""


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
    if type(passwd) is not str:
        raise TypeError(f"handle_login: Invalid type({passwd})={type(passwd)}")

    save_key = value["save_key"]
    if type(save_key) is not bool:
        raise TypeError(f"handle_login: Invalid type({save_key})={type(save_key)}")
    if not save_key:
        rm_private_key(session)

    # TODO: check the relation between save_key and passwd

    if passwd != "":
        try:
            CONN[session].connect(hostname=server, username=username, passwd=passwd)
            private_key_path = ""
            if save_key:
                import uuid
                private_key_path = PRIVATE_KEYS_PATH + uuid.uuid1().hex
                CONN[session].save_keys(private_key_path)
            USER_PROFILE.modify_session(session_name=session,
                                        username=username,
                                        last_server=server,
                                        private_key_path=private_key_path)
            USER_PROFILE.save_profile(USER_PROFILE_PATH)
            # should be successful at this stage
        except Exception as e:
            send_msg("login_ack", "Failed: " + str(e))
            raise e
    else:
        private_key_path = USER_PROFILE["sessions"][session]["private_key_path"]
        if "" == private_key_path:
            send_msg("login_ack", "Failed: " + "Please input a password")
            return
        elif username == USER_PROFILE["sessions"][session]["username"]:
            try:
                CONN[session].connect(hostname=server, username=username, key_filename=private_key_path)
                USER_PROFILE.modify_session(session_name=session,
                                            username=username,
                                            last_server=server,
                                            private_key_path=private_key_path)
                USER_PROFILE.save_profile(USER_PROFILE_PATH)
                # should be successful at this stage
            except Exception as e:
                send_msg("login_ack", "Failed: " + str(e))
                raise e

    send_msg("login_ack", session)


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


def handle_resize(value):
    session = value["s"]
    if type(session) is not str:
        raise TypeError(f"handle_send: Invalid type({session})={type(session)}")
    elif session not in CONN:
        raise ValueError(f"handle_send: Invalid session={session}")

    height = value["r"]
    width = value["c"]

    CONN[session].shell_change_size(width, height)


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


def handle_vnc(value):
    session = value["session"]
    if type(session) is not str:
        raise TypeError(f"handle_vnc: Invalid type({session})={type(session)}")
    elif session not in CONN:
        raise ValueError(f"handle_vnc: Invalid session={session}")

    vncpasswd = value["passwd"]
    if vncpasswd is not None and type(vncpasswd) is not str:
        raise TypeError(f"handle_login: Invalid type({vncpasswd})={type(vncpasswd)}")

    # FIXME: refactor this
    conn_profile_name = USER_PROFILE["sessions"][session]["conn_profile"]
    vnc_manual = USER_PROFILE._conn_profiles[conn_profile_name]["vnc_manual"]

    if not vnc_manual:
        # vncserver already listening on the server
        remote_vnc_port = USER_PROFILE._conn_profiles[conn_profile_name]["vnc_listening_port"]
    else:
        # FIXME: only override if xstartup missing
        # override xstartup
        CONN[session].exec_command_blocking("rm -f ~/.vnc/xstartup")
        CONN[session].sftp.put("./profile/xstartup", "./.vnc/xstartup")
        CONN[session].exec_command_blocking("chmod 555 ~/.vnc/xstartup")

        if vncpasswd is not None:
            CONN[session].exec_command_blocking(f"echo '{vncpasswd}'|vncpasswd -f > ~/.vnc/passwd")

        # fetch the vnc passwd from the server
        import uuid
        passwd_path = VNC_PASSWORD_PATH + uuid.uuid1().hex
        try:
            CONN[session].sftp.get("./.vnc/passwd", passwd_path)
        except FileNotFoundError as e:
            send_msg("vnc_auth", session)
            return

        ports_by_me = CONN[session].check_ports_by_me()
        print("ports_by_me", ports_by_me)
        only_port_by_me = None
        vnc_cmd = "vncserver"
        if len(ports_by_me) > 1:
            # something is wrong: there should be more than one vncserver launched by the user
            # kill all instead
            vnc_cmd += " -kill :'*'; vncserver"
        elif len(ports_by_me) == 1:
            only_port_by_me, = ports_by_me

        if len(ports_by_me) != 1:
            # if the previous session(s) can't be reused
            # relaunch the vncserver
            print(vnc_cmd)
            _, _, stdout, _ = CONN[session].exec_command_blocking(vnc_cmd)

            for vnc_prompt in stdout:
                match = re.search("at :(\d+)", vnc_prompt)
                if match:
                    only_port_by_me = int(match.group(1))
                    break

        remote_vnc_port = only_port_by_me + 5900

    local_port = get_free_port()

    CONN[session].create_forward_tunnel(local_port, remote_vnc_port)
    # FIXME: whether vnc passwd is needed or not should have nothing
    #  to do with whether the VNC server is already listeninhg
    if vnc_manual:
        os.system(
            f"open -n {TIGER_VNC_VIEWER_PATH_MACOS} --args --passwd={os.path.abspath(passwd_path)} localhost:{local_port}")
    else:
        os.system(
            f"open -n {TIGER_VNC_VIEWER_PATH_MACOS} --args localhost:{local_port}")
