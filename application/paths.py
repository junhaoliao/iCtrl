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

import logging
import os
import platform


logger = logging.getLogger(__name__)


def makedir_if_not_exists(path):
    if not os.path.exists(path):
        os.mkdir(path)
    logger.info('Created directory, path = %s', path)


# setup profile path
if platform.system() == "Windows":
    PROFILE_PATH = os.path.join(os.environ['LOCALAPPDATA'], "ictrl")
elif platform.system() == "Darwin" or 'Linux':
    PROFILE_PATH = os.path.join(os.path.expanduser("~"), ".ictrl")
else:
    logger.error("Operating System: %s not supported", platform.system())
    raise SystemError(f"Operating System: {platform.system()} not supported")

makedir_if_not_exists(PROFILE_PATH)
USER_PROFILE_PATH = os.path.join(PROFILE_PATH, "user_profile.json")
PRIVATE_KEY_PATH = os.path.join(PROFILE_PATH, "private_keys")
makedir_if_not_exists(PRIVATE_KEY_PATH)
