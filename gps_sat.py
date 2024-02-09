import logging
import pwnagotchi.ui.fonts as fonts
import pwnagotchi.plugins as plugins
from pwnagotchi.ui.components import LabeledValue
from pwnagotchi.ui.view import BLACK


class GPSSat(plugins.Plugin):
    __author__ = "SgtStroopwafel, sliim@mailoo.org"
    __version__ = "1.0.0"
    __license__ = "GPL3"
    __description__ = "Display number of satellites. Requires gps plugin enabled."
    __name__ = "GPSSat"
    __help__ = "Display number of satellites. Requires gps plugin enabled."
    __dependencies__ = {
        "apt": ["none"],
        "pip": ["scapy"],
    }
    __defaults__ = {
        "enabled": False,
    }

    def __init__(self):
        self.ready = False
        logging.debug(f"[{self.__class__.__name__}] plugin init")
        self.title = ""
        self.gps = None

    def on_loaded(self):
        try:
            if (
                "position" not in self.options
                or not self.options["position"]
                or len(self.options["position"].split(",")) != 2
            ):
                self.options["position"] = "90,83"
            logging.info(f"[{self.__class__.__name__}] plugin loaded")
        except Exception as e:
            logging.error("gps_sat.on_loaded: %s" % e)

    def on_ready(self, agent):
        try:
            self.gps = plugins.loaded["gps"]
            if not self.gps:
                logging.error(
                    f"[{self.__class__.__name__}] gps plugin not loaded!")
        except Exception as e:
            logging.error("gps_sat.on_ready: %s" % e)

    def on_ui_setup(self, ui):
        try:
            pos = self.options["position"].split(",")
            ui.add_element(
                "sattelites",
                LabeledValue(
                    color=BLACK,
                    label="sat",
                    value="0",
                    position=(int(pos[0]), int(pos[1])),
                    label_font=fonts.Small,
                    text_font=fonts.Small,
                ),
            )
        except Exception as e:
            logging.error("gps_sat.on_ui_setup: %s" % e)

    def on_ui_update(self, ui):
        try:
            if self.gps and self.gps.coordinates:
                ui.set("sattelites", str(
                    self.gps.coordinates["NumSatellites"]))
        except Exception as e:
            logging.error("gps_sat.on_ui_update: %s" % e)

    def on_unload(self, ui):
        try:
            with ui._lock:
                ui.remove_element("sattelites")
                logging.info(f"[{self.__class__.__name__}] plugin unloaded")
        except Exception as e:
            logging.error("gps_sat.on_unload: %s" % e)

    def on_webhook(self, path, request):
        logging.info(f"[{self.__class__.__name__}] webhook pressed")
