import logging

import pwnagotchi
import pwnagotchi.plugins as plugins
import pwnagotchi.ui.faces as faces
from pwnagotchi.ui.components import LabeledValue
from pwnagotchi.ui.view import BLACK
import pwnagotchi.ui.fonts as fonts
from pwnagotchi.ui.hw.base import DisplayImpl


class LcdHat(plugins.Plugin):
    __author__ = "SgtStroopwafel, HannaDiamond"
    __version__ = "1.0.1"
    __license__ = "MIT"
    __description__ = "A plugin that will add age and strength stats based on epochs and trained epochs"
    __name__ = "Age"
    __help__ = "A plugin that will add age and strength stats based on epochs and trained epochs"
    __dependencies__ = {
        "apt": ["none"],
        "pip": ["scapy"],
    }
    __defaults__ = {
        "enabled": False,
    }

    def __init__(self, config):
        self.ready = False
        logging.debug(f"[{self.__class__.__name__}] plugin init")
        self.title = ""
        super(LcdHat, self).__init__(config, "lcdhat")
        self._display = None

    def layout(self):
        # font order: bold, bold_small, medium, huge, bold_big, small
        # fonts.setup(10, 8, 10, 28, 25, 9)
        fonts.setup(14, 12, 14, 32, 29, 13)
        self._layout["width"] = 240
        self._layout["height"] = 240
        self._layout["face"] = (60, 40)
        self._layout["name"] = (0, 78)
        self._layout["channel"] = (0, 18)
        self._layout["aps"] = (35, 18)
        self._layout["uptime"] = (153, 18)
        self._layout["line1"] = [0, 33, 240, 33]
        self._layout["line2"] = [0, 150, 240, 150]
        self._layout["line3"] = [0, 221, 240, 221]
        self._layout["friend_face"] = (10, 223)
        self._layout["friend_name"] = (60, 226)
        self._layout["shakes"] = (0, 152)
        self._layout["mode"] = (100, 36)
        self._layout["status"] = {
            "pos": (10, 98),
            "font": fonts.status_font(fonts.Medium),
            "max": 20,
        }

        return self._layout

    def initialize(self):
        logging.info("initializing lcdhat display")
        logging.info(self.config["color"])
        from pwnagotchi.ui.hw.libs.waveshare.lcdhat.epd import EPD

        self._display = EPD()
        self._display.init()
        self._display.clear()

    def render(self, canvas):
        self._display.display(canvas)

    def clear(self):
        self._display.clear()

    def on_loaded(self):
        logging.info(f"[{self.__class__.__name__}] plugin loaded")

    def on_unload(self, ui):
        with ui._lock:
            logging.info(f"[{self.__class__.__name__}] plugin unloaded")

    def on_webhook(self, path, request):
        logging.info(f"[{self.__class__.__name__}] webhook pressed")
