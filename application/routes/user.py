from flask import request, abort

from .. import api, profiles


# TODO: review the need to remove the argument readings from the APIs, once we finish debugging

@api.route('/userid')
def index():
    user = profiles.get_user()

    return f'{user.id}'


@api.route('/register', methods=['POST', 'GET'])
def register():
    try:
        if request.method == 'GET':
            username = request.args['username']
            password = request.args['password']
            email = request.args['email']
        else:
            username = request.json['username']
            password = request.json['password']
            email = request.json['email']

        profiles.add_user(username, password, email)
    except KeyError as e:
        abort(403, f'{e} is missing')

    return 'Registration Successful'


@api.route('/login', methods=['POST', 'GET'])
def login():
    try:
        if request.method == 'GET':
            username = request.args['username']
            password = request.args['password']
        else:
            username = request.json['username']
            password = request.json['password']

        profiles.login(username, password)
    except KeyError as e:
        abort(403, f'{e} is missing')

    return 'logged in'


@api.route('/logout')
def logout():
    profiles.logout()

    return f'logged out'


@api.route('/resend_activation', methods=['POST'])
def resend():
    try:
        email = request.json['username']
        profiles.send_activation_email(email)
    except KeyError as e:
        abort(403, f'{e} is missing')
    return 'sent'


@api.route('/activate', methods=['GET'])
def activate():
    try:
        userid = request.args['userid']
        code = request.args['code']

        if profiles.activate_user(userid, code):
            return 'Your account has been activated. '
    except KeyError as e:
        abort(403, f'{e} is missing')

    return 'Failed to activate. ' \
           'Your activation link might have been expired or replaced. Please visit ' \
           '<a href="https://ictrl.ca">https://ictrl.ca</a> ' \
           'to login / register. '
