from pwnagotchi.ui.components import LabeledValue
from pwnagotchi.ui.view import BLACK
import pwnagotchi.ui.fonts as fonts
import pwnagotchi.plugins as plugins
import pwnagotchi
import logging
import os


class DisplayAircrack(plugins.Plugin):
    __author__ = "SgtStroopwafel, @7h30th3r0n3"
    __version__ = "1.0.0"
    __license__ = "GPL3"
    __description__ = "A plugin to display if aircrack is runing or not"
    __name__ = "DisplayAircrack"
    __help__ = "A plugin to display if aircrack is runing or not"
    __dependencies__ = {
        "apt": ["aircrack-ng"],
        "pip": ["scapy"],
    }
    __defaults__ = {
        "enabled": False,
    }

    def __init__(self):
        self.ready = False
        logging.debug(f"[{self.__class__.__name__}] plugin init")
        self.title = ""

    def on_loaded(self):
        logging.info(f"[{self.__class__.__name__}] plugin loaded")

    def on_ui_setup(self, ui):
        ui.add_element(
            "aircrack-ng-status",
            LabeledValue(
                color=BLACK,
                label="",
                value="",
                position=(ui.width() // 2 - 10, 0),
                label_font=fonts.Bold,
                text_font=fonts.Medium,
            ),
        )

    def on_unload(self, ui):
        with ui._lock:
            try:
                ui.remove_element("aircrack-ng-status")
                logging.info(f"[{self.__class__.__name__}] plugin unloaded")
            except Exception as e:
                logging.error(f"[{self.__class__.__name__}] unload: %s" % e)

    def on_ui_update(self, ui):
        # Check if aircrack-ng is running and update status display
        if "aircrack-ng" in os.popen("ps -A").read():
            ui.set("aircrack-ng-status", "(1)")
        else:
            ui.set("aircrack-ng-status", "(0)")

    def on_webhook(self, path, request):
        logging.info(f"[{self.__class__.__name__}] webhook pressed")
        pass
