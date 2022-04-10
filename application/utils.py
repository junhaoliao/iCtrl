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

import os
import smtplib
import socket
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


def int_to_bytes(num):
    return bytes([num])


def find_free_port():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(('', 0))
        return sock.getsockname()[1]


def send_email(to_email, subject, body):
    sender_server = os.environ['SENDER_SERVER']
    sender_port = int(os.environ['SENDER_PORT'])
    sender_email = os.environ['SENDER_EMAIL']
    sender_password = os.environ['SENDER_PASSWD']

    msg = MIMEMultipart('alternative')
    msg['Subject'] = subject
    msg['From'] = sender_email
    msg['To'] = to_email
    html = MIMEText(body, 'html')
    msg.attach(html)

    server_ssl = smtplib.SMTP_SSL(sender_server, sender_port)
    server_ssl.ehlo()
    server_ssl.login(sender_email, sender_password)

    server_ssl.sendmail(sender_email, to_email, msg.as_string())
    server_ssl.close()


def validate_password(password):
    """
    Reference: https://www.geeksforgeeks.org/password-validation-in-python/
    """
    special_symbols = ['!', '@', '#', '$', '%', '^', '&', '*', '(', ')', '-', '+']

    reason = None
    if len(password) < 6:
        reason = 'Password length should be at least 6 characters'
    elif len(password) > 32:
        reason = 'Password length should not exceed 32 characters'
    elif not any(char.isdigit() for char in password):
        reason = 'Password should have at least one numeral'
    elif not any(char.isupper() for char in password):
        reason = 'Password should have at least one uppercase letter'
    elif not any(char.islower() for char in password):
        reason = 'Password should have at least one lowercase letter'
    elif not any(char in special_symbols for char in password):
        reason = f'Password should have at least one of the symbols [{"".join(special_symbols)}]'

    if reason is not None:
        return False, reason
    else:
        return True, None
