# Based on the GPS plugin from https://github.com/evilsocket
#
# Requires https://github.com/MartijnBraam/gpsd-py3
import json
import logging

import pwnagotchi.plugins as plugins
import pwnagotchi.ui.fonts as fonts
from pwnagotchi.ui.components import LabeledValue
from pwnagotchi.ui.view import BLACK
import pwnagotchi
import gpsd

class GPSD:
    def __init__(self, gpsdhost, gpsdport):
        gpsd.connect(host=gpsdhost, port=gpsdport)
        self.running = True
        self.coords = {
            "Latitude": None,
            "Longitude": None,
            "Altitude": None,
            "Date": None
        }

    def update_gps(self):
        if self.running:
            packet = gpsd.get_current()
            if packet.mode >= 2:
                    self.coords = {
                        "Latitude": packet.lat,
                        "Longitude": packet.lon,
                        "Altitude": packet.alt if packet.mode > 2 else None,
                        "Date": packet.time
                    }
        return self.coords

class gpsd_coord(plugins.Plugin):
    __author__ = "tom@dankmemes2020.com"
    __version__ = "1.0.0"
    __license__ = "GPL3"
    __description__ = "Talk to GPSD and save coordinates whenever a handshake is captured."

    def __init__(self):
        self.gpsd = None

    def on_loaded(self):
        self.gpsd = GPSD(self.options['gpsdhost'], self.options['gpsdport'])
        logging.info("[gpsd] plugin loaded")

    def on_ready(self, agent):
        if (self.options["gpsdhost"]):
            logging.info(f"enabling bettercap's gps module for {self.options['gpsdhost']}:{self.options['gpsdport']}")
            try:
                agent.run("gps off")
            except Exception:
                logging.info(f"bettercap gps was already off")
                pass

            agent.run("set gps.device 127.0.0.1:2947; set gps.baudrate 9600; gps on")
            logging.info("bettercap set and on")
            self.running = True
        else:
            logging.warning("no GPS detected")

    def on_handshake(self, agent, filename, access_point, client_station):
        coords = self.gpsd.update_gps()
        if coords and all([
            # avoid 0.000... measurements
            coords["Latitude"], coords["Longitude"]
        ]):
            gps_filename = filename.replace(".pcap", ".gps.json")
            logging.info(f"[gpsd] saving GPS to {gps_filename} ({coords})")
            with open(gps_filename, "w+t") as fp:
                json.dump(coords, fp)
        else:
            logging.info("[gpsd] not saving GPS: no fix")

    def on_ui_setup(self, ui):
        # add coordinates for other displays
        if ui.is_waveshare_v2():
            lat_pos = (127, 75)
            lon_pos = (122, 84)
            alt_pos = (127, 94)
        elif ui.is_waveshare_v1():
            lat_pos = (130, 70)
            lon_pos = (125, 80)
            alt_pos = (130, 90)
        elif ui.is_inky():
            lat_pos = (127, 60)
            lon_pos = (127, 70)
            alt_pos = (127, 80)
        elif ui.is_waveshare144lcd():
            # guessed values, add tested ones if you can
            lat_pos = (67, 73)
            lon_pos = (62, 83)
            alt_pos = (67, 93)
        elif ui.is_dfrobot_v2:
            lat_pos = (127, 75)
            lon_pos = (122, 84)
            alt_pos = (127, 94)
        elif ui.is_waveshare27inch():
            lat_pos = (6,120)
            lon_pos = (1,135)
            alt_pos = (6,150)
        else:
            # guessed values, add tested ones if you can
            lat_pos = (127, 51)
            lon_pos = (127, 56)
            alt_pos = (102, 71)

        label_spacing = 0

        ui.add_element(
            "latitude",
            LabeledValue(
                color=BLACK,
                label="lat:",
                value="-",
                position=lat_pos,
                label_font=fonts.Small,
                text_font=fonts.Small,
                label_spacing=label_spacing,
            ),
        )
        ui.add_element(
            "longitude",
            LabeledValue(
                color=BLACK,
                label="long:",
                value="-",
                position=lon_pos,
                label_font=fonts.Small,
                text_font=fonts.Small,
                label_spacing=label_spacing,
            ),
        )
        ui.add_element(
            "altitude",
            LabeledValue(
                color=BLACK,
                label="alt:",
                value="-",
                position=alt_pos,
                label_font=fonts.Small,
                text_font=fonts.Small,
                label_spacing=label_spacing,
            ),
        )

    def on_unload(self, ui):
        with ui._lock:
            ui.remove_element('latitude')
            ui.remove_element('longitude')
            ui.remove_element('altitude')

    def on_ui_update(self, ui):
        coords = self.gpsd.update_gps()
        if coords and all([
            # avoid 0.000... measurements
            coords["Latitude"], coords["Longitude"]
        ]):
            # last char is sometimes not completely drawn
            # using an ending-whitespace as workaround on each line
            ui.set("latitude", f"{coords['Latitude']:.4f} ")
            ui.set("longitude", f" {coords['Longitude']:.4f} ")
            ui.set("altitude", f" {coords['Altitude']:.1f}m ")
