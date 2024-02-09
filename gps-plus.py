# This is a customized version of the builtin Pwnagotchi GPS plugin which
# includes the changes from https://github.com/evilsocket/pwnagotchi/pull/919
# but tweaked further to better fit my specific requirements.
#
# Author: evilsocket@gmail.com
# Contributors: crahan@n00.be
import json
import logging
import os
import pwnagotchi.plugins as plugins
import pwnagotchi.ui.fonts as fonts
from pwnagotchi.ui.components import LabeledValue
from pwnagotchi.ui.view import BLACK


class GPSPlus(plugins.Plugin):
    __author__ = "SgtStroopwafel, evilsocket@gmail.com"
    __version__ = "1.0.1-1"
    __license__ = "GPL3"
    __description__ = "Save GPS coordinates whenever an handshake is captured."
    __name__ = "GPSPlus"
    __help__ = "Save GPS coordinates whenever an handshake is captured."
    __dependencies__ = {
        "apt": ["none"],
        "pip": ["scapy"],
    }
    __defaults__ = {
        "enabled": False,
    }

    LINE_SPACING = 12
    LABEL_SPACING = 0

    def __init__(self):
        self.ready = False
        logging.debug(f"[{self.__class__.__name__}] plugin init")
        self.title = ""
        self.running = False
        self.coordinates = None

    def on_loaded(self):
        logging.info(f"[{self.__class__.__name__}] plugin loaded")
        logging.info(f"gps plugin loaded for {self.options['device']}")

    def on_ready(self, agent):
        if os.path.exists(self.options["device"]):
            logging.info(
                f"[{self.__class__.__name__}] enabling bettercap's gps module for {self.options['device']}"
            )
            try:
                agent.run("gps off")
            except Exception:
                pass

            agent.run(f"set gps.device {self.options['device']}")
            agent.run(f"set gps.baudrate {self.options['speed']}")
            agent.run("gps on")
            self.running = True
        else:
            logging.warn(f"[{self.__class__.__name__}] no GPS detected")

    def on_handshake(self, agent, filename, access_point, client_station):
        if self.running:
            info = agent.session()
            self.coordinates = info["gps"]
            gps_filename = filename.replace(".pcap", ".gps.json")

            if self.coordinates and all(
                [
                    # avoid 0.000... measurements
                    self.coordinates["Latitude"],
                    self.coordinates["Longitude"],
                ]
            ):
                logging.info(
                    f"[{self.__class__.__name__}] saving GPS to {gps_filename} ({self.coordinates})"
                )
                with open(gps_filename, "w+t") as fp:
                    json.dump(self.coordinates, fp)
            else:
                logging.info(
                    f"[{self.__class__.__name__}] not saving GPS. Couldn't find location."
                )

    def on_ui_setup(self, ui):
        try:
            # Configure line_spacing
            line_spacing = int(self.options["linespacing"])
        except Exception:
            # Set default value
            line_spacing = self.LINE_SPACING

        try:
            # Configure position
            pos = self.options["position"].split(",")
            pos = [int(x.strip()) for x in pos]
        except Exception:
            # Set position based on screen type
            if ui.is_waveshare_v2():
                pos = (122, 70)
            else:
                pos = (122, 50)

        ui.add_element(
            "gps_lat",
            LabeledValue(
                color=BLACK,
                label="lat:",
                value="-",
                position=(pos[0] + 5, pos[1]),
                label_font=fonts.Small,
                text_font=fonts.Small,
                label_spacing=self.LABEL_SPACING,
            ),
        )
        ui.add_element(
            "gps_long",
            LabeledValue(
                color=BLACK,
                label="long:",
                value="-",
                position=(pos[0], pos[1] + line_spacing),
                label_font=fonts.Small,
                text_font=fonts.Small,
                label_spacing=self.LABEL_SPACING,
            ),
        )
        ui.add_element(
            "gps_alt",
            LabeledValue(
                color=BLACK,
                label="alt:",
                value="-",
                position=(pos[0] + 5, pos[1] + (2 * line_spacing)),
                label_font=fonts.Small,
                text_font=fonts.Small,
                label_spacing=self.LABEL_SPACING,
            ),
        )

    def on_unload(self, ui):
        with ui._lock:
            ui.remove_element("gps_lat")
            ui.remove_element("gps_long")
            ui.remove_element("gps_alt")
            logging.info(f"[{self.__class__.__name__}] plugin unloaded")

    def on_webhook(self, path, request):
        logging.info(f"[{self.__class__.__name__}] webhook pressed")

    def on_ui_update(self, ui):
        if self.coordinates and all(
            [
                # avoid 0.000... measurements
                self.coordinates["Latitude"],
                self.coordinates["Longitude"],
            ]
        ):
            # last char is sometimes not completely drawn ¯\_(ツ)_/¯
            # using an ending-whitespace as workaround on each line
            ui.set("gps_lat", f"{self.coordinates['Latitude']:.4f} ")
            ui.set("gps_long", f"{self.coordinates['Longitude']:.4f} ")
            ui.set("gps_alt", f"{self.coordinates['Altitude']:.1f}m ")
