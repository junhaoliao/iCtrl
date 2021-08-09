import sys

from application import app

if __name__ == '__main__':
    try:
        port = sys.argv[1]
        host = '127.0.0.1'
    except IndexError:
        # TODO: change this to 80 in production mode
        port = 5000
        host = '0.0.0.0'
    app.run(host=host, port=port)
