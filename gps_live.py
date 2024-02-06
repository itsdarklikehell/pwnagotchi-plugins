import logging
import pwnagotchi.plugins as plugins


class GPSLive(plugins.Plugin):
    __author__ = "sliim@mailoo.org"
    __version__ = "1.0.0"
    __license__ = "GPL3"
    __description__ = """
    Update GPS coordinates on each epoch.
    Requires gps plugin enabled.
    """

    def __init__(self):
        self.gps = None

    def on_loaded(self):
        try:
            logging.info("[gps_live] plugin loaded")
        except Exception as e:
            logging.error("gps_live.on_loaded: %s" % e)

    def on_ready(self, agent):
        try:
            self.gps = plugins.loaded["gps"]
            if not self.gps:
                logging.error("[gps_live] gps plugin not loaded!")
        except Exception as e:
            logging.error("gps_live.on_ready: %s" % e)

    def on_epoch(self, agent, epoch, data):
        try:
            if self.gps and self.gps.running:
                self.gps.coordinates = agent.session()["gps"]
        except Exception as e:
            logging.error("gps_live.on_epoch: %s" % e)

    def on_ui_update(self, ui):
        try:
            if self.gps and self.gps.running:
                coords = self.gps.coordinates
                if not coords or not all([coords["Latitude"], coords["Longitude"]]):
                    ui.set("latitude", "-")
                    ui.set("longitude", "-")
                    ui.set("altitude", "-")
        except Exception as e:
            logging.error("gps_live.on_ui_update: %s" % e)
