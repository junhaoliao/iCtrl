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

from flask import request, abort

from .. import api, profiles
import logging
logger = logging.getLogger(__name__)

# TODO: review the need to remove the argument readings from the APIs, once we finish debugging

@api.route('/userid')
def index():
    user = profiles.get_user()
    logger.info(f"User: Fetching user ID for user: {user.id}")
    return f'{user.id}'


@api.route('/register', methods=['POST', 'GET'])
def register():
    try:
        if request.method == 'GET':
            username = request.args['username']
            password = request.args['password']
            email = request.args['email']
            logger.debug(f"User: Received registration via GET for user: {username}")
        else:
            username = request.json['username']
            password = request.json['password']
            email = request.json['email']
            logger.debug(f"User: Received registration via POST for user: {username}")

        profiles.add_user(username, password, email)
        logger.info(f"User: User registered successfully: {username}")
    except KeyError as e:
        abort(403, f'{e} is missing')

    return 'Registration Successful'


@api.route('/login', methods=['POST', 'GET'])
def login():
    try:
        if request.method == 'GET':
            username = request.args['username']
            password = request.args['password']
            logger.debug(f"User: Received login via GET for user: {username}")
        else:
            username = request.json['username']
            password = request.json['password']
            logger.debug(f"User: Received login via POST for user: {username}")

        profiles.login(username, password)
        logger.info(f"User: User logged in successfully: {username}")
    except KeyError as e:
        abort(403, f'{e} is missing')

    return 'logged in'


@api.route('/logout')
def logout():
    profiles.logout()
    logger.info("User: User logged out successfully")
    return f'logged out'


@api.route('/resend_activation', methods=['POST'])
def resend():
    try:
        username = request.json['username']
        profiles.send_activation_email(username)
        logger.info(f"User: Activation email resent to user: {username}")
    except KeyError as e:
        abort(403, f'{e} is missing')
    return 'sent'


@api.route('/activate', methods=['GET'])
def activate():
    try:
        userid = request.args['userid']
        code = request.args['code']
        logger.debug(f"User: Attempting to activate user: {userid}")
        if profiles.activate_user(userid, code):
            logger.info(f"User: User activated successfully: {userid}")
            return 'Your account has been activated. '
    except KeyError as e:
        abort(403, f'{e} is missing')

    return 'Failed to activate. ' \
           'Your activation link might have been expired or replaced. Please visit ' \
           '<a href="https://ictrl.ca">https://ictrl.ca</a> ' \
           'to login / register. '
