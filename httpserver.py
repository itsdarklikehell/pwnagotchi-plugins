"""Edit the config.toml

main.plugins.httpserver.enabled = true
"""

import logging
from http.server import SimpleHTTPRequestHandler, HTTPServer

import pwnagotchi.plugins as plugins
from pwnagotchi.ui.components import LabeledValue
from pwnagotchi.ui.view import BLACK
import pwnagotchi.ui.fonts as fonts


class MyHTTPRequestHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory="/root/handshakes", **kwargs)


class HttpServerPlugin(plugins.Plugin):
    __author__ = "Hades, SgtStroopwafel"
    __version__ = "1.0.0"
    __license__ = "GPL3"
    __description__ = "HTTP Server Plugin"
    __name__ = "HttpServerPlugin"
    __help__ = "HTTP Server Plugin"
    __dependencies__ = {
        "apt": ["none"],
        "pip": ["scapy"],
    }
    __defaults__ = {
        "enabled": false,
    }

    def __init__(self):
        logging.debug(f"[{self.__class__.__name__}] plugin init")

    def on_loaded(self):
        logging.info(f"[{self.__class__.__name__}] plugin loaded")
        self.start_http_server()

    def on_unload(self, ui):
        logging.info(f"[{self.__class__.__name__}] plugin unloaded")
        self.stop_http_server()

    def start_http_server(self):
        try:
            server_address = ("", 8000)
            self.httpd = HTTPServer(server_address, MyHTTPRequestHandler)
            logging.info(
                f"[{self.__class__.__name__}] Starting HTTP server on port 8000"
            )
            self.httpd.serve_forever()

        except Exception as e:
            logging.error(
                f"[{self.__class__.__name__}] Error starting HTTP server: {e}"
            )

    def stop_http_server(self):
        try:
            if hasattr(self, "httpd"):
                logging.error(f"[{self.__class__.__name__}] Shutting Down HTTP Server.")
                self.httpd.shutdown()

        except Exception as e:
            logging.error(
                f"[{self.__class__.__name__}] Error stopping HTTP server: {e}"
            )

    def on_webhook(self, path, request):
        logging.info(f"[{self.__class__.__name__}] webhook pressed")


# Instantiate the plugin
http_server_plugin = HttpServerPlugin()
