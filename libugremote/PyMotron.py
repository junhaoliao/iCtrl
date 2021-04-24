import sys
import threading
from globals import *
from hanlders import *


def bootstrap():
    IPC_RECV.bind("tcp://*:%d" % RECV_PORT)
    IPC_SEND.connect("tcp://127.0.0.1:%d" % SEND_PORT)


def handle_main(key, value):
    if key == "sync":
        handle_sync(value)
    elif key == "query_profiles":
        handle_query_profiles(value)
    elif key == "new_session":
        handle_new_session(value)
    elif key == "login":
        handle_login(value)
    elif key == "shell":
        handle_shell(value)
    elif key == "send":
        handle_send(value)
    elif key == "resize":
        handle_resize(value)
    elif key == "sftp_visit":
        handle_sftp_visit(value)
    elif key == "sftp_download":
        handle_sftp_download(value)
    elif key == "sftp_upload":
        handle_sftp_upload(value)
    else:
        raise ValueError(f"Unknown key={key}, value={value}")


def listen():
    while True:
        recv_data = IPC_RECV.recv()
        if not recv_data:
            break
        # print("recv_data=", recv_data)
        recv_parsed = json.loads(recv_data)
        for key, value in recv_parsed.items():
            handle_main(key, value)


def shutdown():
    IPC_RECV.close()
    IPC_SEND.close()


if __name__ == '__main__':
    print("PyMotron launching...")
    print("sys.argv=", sys.argv)
    try:
        RECV_PORT = int(sys.argv[1])
        SEND_PORT = int(sys.argv[2])
    except Exception as e:
        print("Exception:", e)
        print("Usage: PyMotron RECV_PORT SEND_PORT")
        exit(1)

    # sys.stdout.flush()
    bootstrap()

    # thread_listen = threading.Thread(target=listen)
    # thread_listen.join()
    listen()

    shutdown()
