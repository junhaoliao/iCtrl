from enum import IntEnum, auto, unique


@unique
class ConnectionType(IntEnum):
    GENERAL = auto()
    VNC = auto()
    TERM = auto()
    SFTP = auto()


# 31: 32(space) starts to be the first commonly used code in ASCII
STEP_DONE = 31
ERROR_GENERAL = 100


@unique
class VNCError(IntEnum):
    GENERAL = ERROR_GENERAL + 20
    PASSWD_MISSING = auto()


@unique
class SSHError(IntEnum):
    GENERAL = 200
    HOST_UNREACHABLE = auto()
    AUTH_MISSING = auto()
    AUTH_WRONG = auto()


class ICtrlError:
    VNC = VNCError
    SSH = SSHError


@unique
class VNCStep(IntEnum):
    SSH_AUTH = 0
    CHECK_LOAD = auto()
    PARSE_PASSWD = auto()
    LAUNCH_VNC = auto()
    CREATE_TUNNEL = auto()
    DONE = STEP_DONE


@unique
class TermStep(IntEnum):
    SSH_AUTH = 0
    CHECK_LOAD = auto()
    LAUNCH_SHELL = auto()
    DONE = STEP_DONE


class ICtrlStep:
    VNC = VNCStep
    Term = TermStep
