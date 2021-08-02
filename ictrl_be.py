import sys

from application import app

if __name__ == '__main__':
    try:
        port = sys.argv[1]
    except IndexError:
        port = 5000
    app.run(host='0.0.0.0', port=port)
