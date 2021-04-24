import zmq

from paths import *

from libugremote.ug_profile.UGUserProfile import *
from libugremote.ug_connection.UGConnection import *

RECV_PORT = -1
SEND_PORT = -1

ZMQ_CONTEXT = zmq.Context()
IPC_RECV = ZMQ_CONTEXT.socket(zmq.PULL)
IPC_SEND = ZMQ_CONTEXT.socket(zmq.PUSH)

CONN = {}
USER_PROFILE = UGUserProfile()
USER_PROFILE.load_profile(USER_PROFILE_PATH)
for loaded_session_name in USER_PROFILE["sessions"]:
    CONN[loaded_session_name] = UGConnection()
