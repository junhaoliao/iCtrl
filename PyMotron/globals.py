import zmq

from libugremote.ug_profile.UGUserProfile import *
from libugremote.ug_connection.UGConnection import *

RECV_PORT = -1
SEND_PORT = -1

ZMQ_CONTEXT = zmq.Context()
IPC_RECV = ZMQ_CONTEXT.socket(zmq.PULL)
IPC_SEND = ZMQ_CONTEXT.socket(zmq.PUSH)

SESSION = []
USER_PROFILE = UGUserProfile()
USER_PROFILE.load_profile("./profile/user_profile.json")
for session in USER_PROFILE["sessions"]:
    SESSION.append(UGConnection())