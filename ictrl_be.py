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

if __name__ == '__main__':
    from application import api, app, APP_HOST, APP_PORT
    from application.utils import local_auth

    if not app.debug:
        import os

        from flask import abort, request, send_from_directory


        @app.before_request
        def before_request():
            local_auth(headers=request.headers, abort_func=abort)

        # Reference: https://stackoverflow.com/questions/44209978/serving-a-front-end-created-with-create-react-app-with
        # -flask
        @app.route('/', defaults={'path': ''})
        @app.route('/<path:path>')
        def serve(path):
            if path != "" and os.path.exists(os.path.join(app.static_folder, path)):
                return send_from_directory(app.static_folder, path)
            else:
                return send_from_directory(app.static_folder, 'index.html')

    app.register_blueprint(api, url_prefix='/api')
    app.run(host=APP_HOST, port=APP_PORT, ssl_context="adhoc")
