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

import pyDes
import logging.config

logger = logging.getLogger(__name__)

KEY = [232, 74, 214, 96, 196, 114, 26, 224]
CRYPT = pyDes.des(KEY)


def obfuscate_password(password):
    padded_raw = (password + '\0' * 8)[:8]
    return CRYPT.encrypt(padded_raw)


def decrypt_passwd(obfuscated):
    decrypted_bytes = CRYPT.decrypt(obfuscated)
    return decrypted_bytes.decode("ascii").rstrip('\0')


def vncpasswd(passwd_path, password=None):
    if password is None:
        obfuscated = read_password()
    else:
        obfuscated = obfuscate_password(password)

    with open(passwd_path, "wb") as passwd:
        passwd.write(obfuscated)
        logger.debug("Vnc Password: Write obfuscated password to {}".format(passwd_path))

    return obfuscated


def vncpasswd2plain(passwd_path):
    with open(passwd_path, "rb") as passwd:
        return decrypt_passwd(passwd.readline())


def read_password():
    from getpass import getpass
    while True:
        passwd = getpass("Password: ")
        if len(passwd) == 0:
            print("Password not changed")
            exit(1)
        elif len(passwd) < 6:
            print("Password must be at least 6 characters - try again")
            continue

        passwd2 = getpass("Verify: ")
        if passwd != passwd2:
            print("Passwords don't match - try again")
            continue
        return obfuscate_password(passwd)
