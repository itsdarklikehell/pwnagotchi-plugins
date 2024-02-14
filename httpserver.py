import logging
from http.server import SimpleHTTPRequestHandler, HTTPServer

import pwnagotchi.plugins as plugins
from pwnagotchi.ui.components import LabeledValue
from pwnagotchi.ui.view import BLACK
import pwnagotchi.ui.fonts as fonts

class MyHTTPRequestHandler(SimpleHTTPRequestHandler):
    def __init__(self):
        super().__init__(directory="/root/handshakes")

class HttpServerPlugin(plugins.Plugin):
    __author__ = 'Hades'
    __version__ = '1.0.0'
    __license__ = 'GPL3'
    __description__ = 'HTTP Server Plugin'

    def on_loaded(self):
        logging.info("[HttpServerPlugin] Loaded")
        self.start_http_server()

    def on_unload(self, ui):
        self.stop_http_server()

    def start_http_server(self):
        try:
            server_address = ('', 8000)
            self.httpd = HTTPServer(server_address, MyHTTPRequestHandler)
            logging.info("[HttpServerPlugin] Starting HTTP server on port 8000")
            self.httpd.serve_forever()

        except Exception as e:
            logging.error(f"[HttpServerPlugin] Error starting HTTP server: {e}")

    def stop_http_server(self):
        try:
            if hasattr(self, 'httpd'):
                logging.error("[HttpServerPlugin] Shutting Down HTTP Server.")
                self.httpd.shutdown()

        except Exception as e:
            logging.error(f"[HttpServerPlugin] Error stopping HTTP server: {e}")

# Instantiate the plugin
http_server_plugin = HttpServerPlugin()