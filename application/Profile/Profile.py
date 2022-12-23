#  Copyright (c) 2022 iCtrl Developers
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

#
#  Permission is hereby granted, free of charge, to any person obtaining a copy
#   of this software and associated documentation files (the "Software"), to
#   deal in the Software without restriction, including without limitation the
#   rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
#   sell copies of the Software, and to permit persons to whom the Software is
#   furnished to do so, subject to the following conditions:
#
#
#
#  Permission is hereby granted, free of charge, to any person obtaining a copy
#   of this software and associated documentation files (the "Software"), to
#   deal in the Software without restriction, including without limitation the
#   rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
#   sell copies of the Software, and to permit persons to whom the Software is
#   furnished to do so, subject to the following conditions:
#
#
from abc import ABCMeta, abstractmethod


class Profile(metaclass=ABCMeta):
    @abstractmethod
    def login(self, username, password):
        pass

    @staticmethod
    @abstractmethod
    def logout():
        pass

    @abstractmethod
    def query(self):
        pass

    @abstractmethod
    def add_user(self, username, password, email):
        pass

    @abstractmethod
    def activate_user(self, userid, code):
        pass

    @abstractmethod
    def get_user(self):
        pass

    @abstractmethod
    def add_session(self, host, username, conn):
        pass

    @abstractmethod
    def save_profile(self):
        pass

    @abstractmethod
    def delete_session(self, session_id):
        pass

    @abstractmethod
    def change_host(self, session_id, new_host):
        pass

    @abstractmethod
    def get_session_info(self, session_id):
        pass

    def set_session_nickname(self, session_id, nickname):
        pass

    @abstractmethod
    def send_activation_email(self, username):
        pass
