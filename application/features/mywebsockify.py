import websockify
from werkzeug.serving import generate_adhoc_ssl_context

from application.utils import local_auth
import logging.config

logger = logging.getLogger(__name__)

class MyProxyRequestHandler(websockify.ProxyRequestHandler):
    def auth_connection(self):
        super(MyProxyRequestHandler, self).auth_connection()
        if not local_auth(headers=self.headers, abort_func=self.server.server_close):
            # local auth failure
            return


class MySSLProxyServer(websockify.LibProxyServer):
    # noinspection PyPep8Naming
    def __init__(self, RequestHandlerClass=websockify.ProxyRequestHandler, ssl_context=None, **kwargs):
        super(MySSLProxyServer, self).__init__(RequestHandlerClass=RequestHandlerClass, **kwargs)

        if ssl_context is None:
            logger.debug("Generating self-signed SSL certificate")
            # no certificate provided, generate self-signing certificate
            ssl_context = generate_adhoc_ssl_context()
        self.socket = ssl_context.wrap_socket(self.socket, server_side=True)
