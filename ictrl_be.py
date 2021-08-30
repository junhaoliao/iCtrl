if __name__ == '__main__':
    from application import api, app, APP_HOST, APP_PORT

    if not app.debug:
        import os

        from flask import send_from_directory


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
    app.run(host=APP_HOST, port=APP_PORT)
