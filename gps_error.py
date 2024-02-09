import logging
import pwnagotchi.plugins as plugins


class GPSError(plugins.Plugin):
    __author__ = "SgtStroopwafel, sliim@mailoo.org"
    __version__ = "1.0.0"
    __license__ = "GPL3"
    __description__ = (
        "Display error when GPS is not running. Requires gps plugin enabled."
    )
    __name__ = "GPSError"
    __help__ = "Display error when GPS is not running. Requires gps plugin enabled."
    __dependencies__ = {
        "apt": ["none"],
        "pip": ["scapy"],
    }
    __defaults__ = {
        "enabled": false,
    }

    def __init__(self):
        self.ready = False
        logging.debug(f"[{self.__class__.__name__}] plugin init")
        self.title = ""
        self.gps = None

    def on_loaded(self):
        try:
            logging.info(f"[{self.__class__.__name__}] plugin loaded")
        except Exception as e:
            logging.error("gps_error.on_loaded: %s" % e)

    def on_ready(self, agent):
        try:
            self.gps = plugins.loaded["gps"]
            if not self.gps:
                logging.info(f"[{self.__class__.__name__}] plugin not loaded!")
        except Exception as e:
            logging.error("gps_error.on_ready: %s" % e)

    def on_ui_update(self, ui):
        try:
            if not self.gps:
                ui.set("latitude", "Not loaded")
            elif not self.gps.running:
                ui.set("latitude", "Not running")
            elif not self.gps.coordinates:
                ui.set("latitude", "No data")
            elif not all(
                [
                    self.gps.coordinates["Latitude"],
                    self.gps.coordinates["Longitude"],
                    self.gps.coordinates["FixQuality"],
                ]
            ):
                ui.set("latitude", "Not fixed")
        except Exception as e:
            logging.error("gps_error.on_ui_update: %s" % e)

    def on_unload(self, ui):
        with ui._lock:
            logging.info(f"[{self.__class__.__name__}] plugin unloaded")

    def on_webhook(self, path, request):
        logging.info(f"[{self.__class__.__name__}] webhook pressed")
