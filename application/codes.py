#  Copyright (c) 2021-2022 iCtrl Developers
# 
#  Permission is hereby granted, free of charge, to any person obtaining a copy
#   of this software and associated documentation files (the "Software"), to
#   deal in the Software without restriction, including without limitation the
#   rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
#   sell copies of the Software, and to permit persons to whom the Software is
#   furnished to do so, subject to the following conditions:
# 
#  The above copyright notice and this permission notice shall be included in
#   all copies or substantial portions of the Software.
# 
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#   IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#   FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#   AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#   LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
#   FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
#   IN THE SOFTWARE.

from enum import IntEnum, auto, unique


@unique
class ConnectionType(IntEnum):
    GENERAL = auto()
    VNC = auto()
    TERM = auto()
    SFTP = auto()
    AUDIO = auto()


# 31: 32(space) starts to be the first commonly used code in ASCII
STEP_DONE = 31
ERROR_GENERAL = 100


@unique
class VNCError(IntEnum):
    GENERAL = ERROR_GENERAL + 20
    PASSWD_MISSING = auto()
    QUOTA_EXCEEDED = auto()


@unique
class SSHError(IntEnum):
    GENERAL = 200
    HOST_UNREACHABLE = auto()
    AUTH_MISSING = auto()
    AUTH_WRONG = auto()
    OVER_LOADED = auto()


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
