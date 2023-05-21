import json
import logging
import os
import time

import pwnagotchi.plugins as plugins
import pwnagotchi.ui.fonts as fonts
from pwnagotchi.ui.components import LabeledValue
from pwnagotchi.ui.view import BLACK


class GPS_More(plugins.Plugin):
    __author__ = "Sniffleupagus"
    __version__ = "1.0.1"
    __license__ = "GPL3"
    __description__ = "Save GPS coordinates whenever it seems reasonable. on epoch to get starting point, handshake to update."

    LINE_SPACING = 10
    LABEL_SPACING = 0

    def __init__(self):
        self.running = False
        self.coordinates = None
        self.agent = None

    def on_loaded(self):
        self.coordinates = None

        if "speed" not in self.options:
            self.options['speed'] = "9600"

        if "device" not in self.options:
            self.options['device'] = "/dev/ttyACM0"

        if 'keepGPSOn' not in self.options:
            self.options['keepGPSOn'] = True

        logging.info("[gps_more] plugin loaded")

    def on_ready(self, agent):
        self.agent = agent

        device = None
        for d in [self.options['device'], "/dev/ttyACM0", "/dev/ttyACM1"]:
            if ":" in d:
                device = d
                break
            if os.path.exists(d):
                device = d
                break
            else:
                logging.debug(f"gps_more unable to find device {d}")

        if device:
            logging.info(
                f"[gps_more] enabling bettercap's gps module for {device}"
            )
            try:
                agent.run("gps off")
            except Exception:
                logging.debug(f"gps_more bettercap gps module was already off")
                pass

            agent.run(f"set gps.device {device}")
            agent.run(f"set gps.baudrate {self.options['speed']}")
            agent.run("gps on")
            logging.info(f"gps_more bettercap gps module enabled on {device}")
            self.running = True


    def _update_coordinates(self, agent, context="[gps update]"):
        try:
            info = agent.session()
            coords = info["gps"]
            if coords and all([
                    coords["Latitude"], coords["Longitude"]
            ]):
                # valid coords
                self.coordinates = coords

                logging.info("%s gps update %s" % (context, repr(self.coordinates)))

                if "save_file" in self.options:
                    save_file = self.options['save_file'];
                else:
                    save_file = None

                # just for debugging
                if not save_file: save_file = "/root/gpstracks/%Y/gps_more%Y%m%d.gps.json"

                if save_file:
                    save_file = time.strftime(save_file)
                    save_dir = os.path.dirname(save_file)

                    if not os.path.exists(save_dir):
                        try:
                            os.makedirs(save_dir)
                        except Exception as err:
                            logging.warn("%s could not make save directory: %s: %s" % (context, save_dir, repr(err)))
                            save_dir = None  # mark none, so don't try writing to an impossible file

                    if save_dir:
                        if os.path.exists(save_file):
                            mode = "a+t"
                        else:
                            mode = "w+t"

                        try:
                            with open(save_file, mode) as fp:
                                fp.write(json.dumps(self.coordinates)+"\n")
                        except OSError as err:
                            logging.info("%s open %s failed: %s" % (context, save_file, repr(err)))

            return info
        except Exception as err:
            logging.warn("%s %s" % (context, repr(err)))
            return None

    def on_handshake(self, agent, filename, access_point, client_station):
        if self.running:
            try:
                #info = self._update_coordinates(agent)

                gps_filename = filename.replace(".pcap", ".gps.json")

                if self.coordinates and all([self.coordinates["Latitude"], self.coordinates["Longitude"]]):
                    logging.info(f"saving GPS to {gps_filename} ({self.coordinates})")
                    with open(gps_filename, "w+t") as fp:
                        json.dump(self.coordinates, fp)
                else:
                    logging.info("not saving GPS. Couldn't find location.")
            except Exception as err:
                logging.warn("[gps_more handshake] %s" % repr(err))

    def on_epoch(self, agent, epoch, epoch_data):
        # update during epochs until there is a good lock
        if not self.coordinates or not all([
            # try again if we have no coordinates
                self.coordinates["Latitude"], self.coordinates["Longitude"], self.coordinates["Altitude"]
        ]):
            info = self._update_coordinates(agent)
            logging.info("[gps_more] epoch %s" % repr(info['gps']))

    def on_bcap_gps_new(self, agent, event):
        try:
            coords = event['data']
            if coords and all([
                    coords["Latitude"], coords["Longitude"]
            ]):
                self.coordinates = coords
        except Exception as err:
            logging.warning("[gps more] gps.new err: %s, %s" % (repr(event), repr(err)))

    def on_ui_setup(self, ui):
        try:
            # Configure line_spacing
            line_spacing = int(self.options['linespacing'])
        except Exception:
            # Set default value
            line_spacing = self.LINE_SPACING

        try:
            # Configure position
            pos = self.options['position'].split(',')
            pos = [int(x.strip()) for x in pos]
            lat_pos = (pos[0] + 5, pos[1])
            lon_pos = (pos[0], pos[1] + line_spacing)
            alt_pos = (pos[0] + 5, pos[1] + (2 * line_spacing))
        except Exception:
            # Set default value based on display type
            if ui.is_waveshare_v2() or ui.is_waveshare_v3():
                logging.info("[GPS MORE] IS THIS KIND OF DISPLAY")

                lat_pos = (127, 78)
                lon_pos = (122, 87)
                alt_pos = (127, 97)
            elif ui.is_waveshare_v1():
                lat_pos = (130, 70)
                lon_pos = (125, 80)
                alt_pos = (130, 90)
            elif ui.is_inky():
                lat_pos = (127, 60)
                lon_pos = (122, 70)
                alt_pos = (127, 80)
            elif ui.is_waveshare144lcd():
                # guessed values, add tested ones if you can
                lat_pos = (67, 73)
                lon_pos = (62, 83)
                alt_pos = (67, 93)
            elif ui.is_dfrobot_v2():
                lat_pos = (127, 74)
                lon_pos = (122, 84)
                alt_pos = (127, 94)
            elif ui.is_waveshare27inch():
                lat_pos = (6, 120)
                lon_pos = (1, 135)
                alt_pos = (6, 150)
            else:
                # guessed values, add tested ones if you can
                lat_pos = (177, 124)
                lon_pos = (172, 137)
                alt_pos = (177, 150)

        ui.add_element(
            "latitude",
            LabeledValue(
                color=BLACK,
                label="lat:",
                value="-",
                position=lat_pos,
                label_font=fonts.Small,
                text_font=fonts.Small,
                label_spacing=self.LABEL_SPACING,
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
                label_spacing=self.LABEL_SPACING,
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
                label_spacing=self.LABEL_SPACING,
            ),
        )

    def on_unload(self, ui):
        with ui._lock:
            try:
                ui.remove_element('latitude')
                ui.remove_element('longitude')
                ui.remove_element('altitude')
                logging.info("gps_more unloaded")
            except Exception:
                logging.info("gps_more unload ui issues")

            try:
                if not self.options["keepGPSOn"]:
                    self.agent.run("gps off")
                    logging.info(f"[gps_more] disabled bettercap's gps module")
            except Exception as err:
                logging.info(f"gps_more bettercap gps module was already off {repr(err)}")
                self.running = False
                pass


    def on_ui_update(self, ui):
        if self.coordinates and all([
            # avoid 0.000... measurements
            self.coordinates["Latitude"], self.coordinates["Longitude"]
        ]):
            # last char is sometimes not completely drawn ¯\_(ツ)_/¯
            # using an ending-whitespace as workaround on each line
            ui.set("latitude", f"{self.coordinates['Latitude']:.4f} ")
            ui.set("longitude", f"{self.coordinates['Longitude']:.4f} ")
            ui.set("altitude", f"{self.coordinates['Altitude']:.1f}m ")

if __name__ == "__main__":
    gps = GPS_More()

    from pwnagotchi.bettercap import Client

    agent = Client('localhost', port=8081, username="pwnagotchi", password="pwnagotchi");

    sess = agent.session()

    print(repr(sess['gps']))

