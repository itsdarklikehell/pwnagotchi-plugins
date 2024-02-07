from pwnagotchi.ui.components import LabeledValue
from pwnagotchi.ui.view import BLACK
import pwnagotchi.plugins as plugins
import pwnagotchi.ui.fonts as fonts
import pwnagotchi
import logging


class DisplayVersion(plugins.Plugin):
    __author__ = "SgtStroopwafel, https://github.com/Teraskull/"
    __version__ = "1.0.0"
    __license__ = "GPL3"
    __description__ = (
        "A plugin that will add the Pwnagotchi version to the left of the current mode."
    )
    __name__ = "DisplayVersion"
    __help__ = (
        "A plugin that will add the Pwnagotchi version to the left of the current mode."
    )
    __dependencies__ = {
        "apt": ["none"],
        "pip": ["scapy"],
    }
    __defaults__ = {
        "enabled": False,
    }

    def __init__(self):
        self.ready = False
        logging.info(f"[{self.__class__.__name__}] plugin init")

    def on_loaded(self):
        logging.info(f"[{self.__class__.__name__}] plugin loaded")

    def on_ui_setup(self, ui):
        ui.add_element(
            "version",
            LabeledValue(
                color=BLACK,
                label="",
                value="v0.0.0",
                position=(185, 110),
                label_font=fonts.Small,
                text_font=fonts.Small,
            ),
        )

    def on_ui_update(self, ui):
        ui.set("version", f"v{pwnagotchi.__version__}")

    def on_unload(self, ui):
        with ui._lock:
            ui.remove_element("version")
            logging.info(f"[{self.__class__.__name__}] plugin unloaded")
