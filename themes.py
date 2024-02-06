import pwnagotchi.plugins as plugins
import pwnagotchi
import logging
import os
from subprocess import Popen
from flask import Response


class Themes(plugins.Plugin):
    __author__ = "@alistar79"
    __version__ = "1.0.0"
    __license__ = "GPL3"
    __description__ = "Theme/script kicker plugin for pwnagotchi."
    __name__ = "Themes"
    __help__ = "Theme/script kicker plugin for pwnagotchi."
    __dependencies__ = {
        "pip": ["scapy"],
    }
    __defaults__ = {
        "enabled": False,
    }

    def __init__(self):
        logging.debug("Pwnagotchi [Themes] plugin created")

    def on_loaded(self):
        logging.info("Pwnagotchi [Themes] plugin loaded")

    def on_webhook(self, path, request):
"""
        Returns requested data
"""
        # defaults:
        response_header_contenttype = None
        response_header_contentdisposition = None
        response_mimetype = "application/json"
        if request.method == "GET":
            if path == "/" or not path:
                # returns the html template
                try:
                    response_data = bytes(self.get_html(), "utf-8")
                except Exception as error:
                    logging.error(f"[Themes] on_webhook / error: {error}")
                    return
                response_status = 200
                response_mimetype = "application/xhtml+xml"
                response_header_contenttype = "text/html"
            elif path.startswith("color"):
                try:
                    Popen("/root/flip_col.sh")
                    response_data = bytes(self.get_html(), "utf-8")
                    response_status = 200
                    response_mimetype = "application/xhtml+xml"
                    response_header_contenttype = "text/html"
                except Exception as error:
                    logging.error(f"[themes] on_webhook color error: {error}")
                    return
            elif path.startswith("faces"):
                try:
                    Popen("/root/flip_faces.sh")
                    response_data = bytes(self.get_html(), "utf-8")
                    response_status = 200
                    response_mimetype = "application/xhtml+xml"
                    response_header_contenttype = "text/html"
                except Exception as error:
                    logging.error(f"[themes] on_webhook faces error: {error}")
                    return
            elif path.startswith("led"):
                try:
                    Popen("/root/flip_led.sh")
                    response_data = bytes(self.get_html(), "utf-8")
                    response_status = 200
                    response_mimetype = "application/xhtml+xml"
                    response_header_contenttype = "text/html"
                except Exception as error:
                    logging.error(f"[themes] on_webhook led error: {error}")
                    return
            else:
                # unknown GET path
                response_data = bytes(
                    """<html>
                <head>
                <meta charset="utf-8"/>
                <style>body{font-size:1000%;}</style>
                </head>
                <body>4😋4</body>
                </html>""",
                    "utf-8",
                )
                response_status = 404
        else:
            # unknown request.method
            response_data = bytes(
                """<html>
                <head>
                <meta charset="utf-8"/>
                <style>body{font-size:1000%;}</style>
                </head>
                <body>4😋4 for bad boys</body>
                </html>""",
                "utf-8",
            )
            response_status = 404

        try:
            r = Response(
                response=response_data,
                status=response_status,
                mimetype=response_mimetype,
            )
            if response_header_contenttype is not None:
                r.headers["Content-Type"] = response_header_contenttype
            if response_header_contentdisposition is not None:
                r.headers["Content-Disposition"] = response_header_contentdisposition
            return r
        except Exception as error:
            logging.error(f"[Themes] on_webhook CREATING_RESPONSE error: {error}")
            return

    def get_html(self):
"""
        Returns the html page
"""
        try:
            template_file = (
                os.path.dirname(os.path.realpath(__file__)) + "/" + "themes.html"
            )
            html_data = open(template_file, "r").read()
        except Exception as error:
            logging.error(
                f"[Themes] error loading template file {template_file} - error: {error}"
            )
        return html_data
