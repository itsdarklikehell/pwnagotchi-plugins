import logging
import json
import toml
import _thread
import os
from datetime import datetime, timezone
from pwnagotchi import restart, plugins
from pwnagotchi.utils import save_config
from flask import abort
from flask import render_template_string
from flask import Response
import pwnagotchi.ui.fonts as fonts
from pwnagotchi.ui.components import LabeledValue
from pwnagotchi.ui.view import BLACK


def serializer(obj):
    if isinstance(obj, set):
        return list(obj)
    raise TypeError

class MyGPS(plugins.Plugin):
    __name__ = 'MyGPS'
    __author__ = 'inbux.development@gmail.com & Mikel Calvo <contact@mikelcalvo.net>'
    __version__ = '0.0.2'
    __license__ = 'MIT'
    __description__ = 'This plugin allows the user to receive GPS information from a connected phone using GPSLogger App. It also saves a JSON file with the GPS coordinates.' 

    LINE_SPACING = 10
    LABEL_SPACING = 0
    SAVE_FILE = "/home/pi/gpstracks/%Y/mygps_%Y%m%d.gps.json"

    def __init__(self):
        self.timestamp = 0
        self.lat = 0
        self.long = 0
        self.alt = 0

    def on_ready(self, agent):
        pass

    def on_internet_available(self, agent):
        pass

    def on_loaded(self):
        """
        Gets called when the plugin gets loaded
        """
        if "save_file" not in self.options:
            self.options['save_file'] = self.SAVE_FILE
        
        if "linespacing" not in self.options:
            self.options['linespacing'] = self.LINE_SPACING
        
        self.timestamp = datetime.utcnow()
        logging.info(f"[{self.__class__.__name__}] Plugin loaded.")

    def on_webhook(self, path, request):
        """
        Store current position
        """

        logging.debug(f"[{self.__class__.__name__}] Received webhook request: {path}, {request.args}")

        self.lat = float(request.args.get('lat', default=0))
        self.long = float(request.args.get('long', default=0))
        self.alt = float(request.args.get('alt', default=0))
        self.timestamp = request.args.get('time', default="0.0").split(".", 1)[0]

        if self.lat != 0:
            logging.info(f"[{self.__class__.__name__}] Received GPS data: LAT: {self.lat}, LONG: {self.long}, ALT: {self.alt}, Time: {self.timestamp}")

            try:
                response_text = 'success'
                save_file = self.options.get('save_file', self.SAVE_FILE)
                save_file = datetime.utcnow().strftime(save_file)
                save_dir = os.path.dirname(save_file)

                logging.debug(f"[{self.__class__.__name__}] Saving GPS data to {save_file}")

                os.makedirs(save_dir, exist_ok=True)
                coordinates = {
                    'latitude': self.lat,
                    'longitude': self.long,
                    'altitude': self.alt,
                    'timestamp': self.timestamp
                }
                with open(save_file, 'a+t') as fp:
                    fp.write(json.dumps(coordinates) + '\n')
                    response_text = 'success'
            except Exception as err:
                logging.error(f"[{self.__class__.__name__}] Error saving GPS data: {err}")
                response_text = f'Error: {err}'
        else:
            response_text = '<html><body><h1>Use the following URL for the <a href="https://gpslogger.app/" target="_blank">GPSLogger App</a>:</h1><h2>http://YOUR_PWNAGOTCHI_BLUETOOTH_IP:8080/plugins/mygps?lat=%LAT&long=%LON&alt=%ALT&time=%TIME</h2></body></html>'

        r = Response(response=response_text, status=200, mimetype='text/html')
        return r

    def on_handshake(self, agent, filename, access_point, client_station):

        gps_filename = filename.replace('.pcap', '.gps.json')

        data = {}
        data['Latitude'] = self.lat
        data['Longitude'] = self.long
        data['Altitude'] = self.alt
        data['Updated'] = self.timestamp;

        gps = json.dumps(data)

        if all([self.lat, self.long]):
            logging.info(f"[{self.__class__.__name__}] Saving GPS data to {gps_filename} ({gps})")
            with open(gps_filename, 'w+t') as f:
                f.write(gps)

    def on_ui_setup(self, ui):
        logging.debug(f"[{self.__class__.__name__}] UI setup started.")

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
            lat_pos = (pos[0] + 5, pos[1])
            lon_pos = (pos[0], pos[1] + line_spacing)
            alt_pos = (pos[0] + 5, pos[1] + (2 * line_spacing))
        except Exception:
            # Set default value based on display type
            if ui.is_waveshare_v2() or ui.is_waveshare_v3():
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
                logging.debug(f"[{self.__class__.__name__}] Display type not recognized.")

                # guessed values, add tested ones if you can
                lat_pos = (177, 124)
                lon_pos = (172, 137)
                alt_pos = (177, 150)

        logging.debug(f"[{self.__class__.__name__}] UI Position: LAT: {lat_pos}, LONG: {lon_pos}, ALT: {alt_pos}")
        logging.debug(f"[{self.__class__.__name__}] Line spacing: {line_spacing}")
        logging.debug(f"[{self.__class__.__name__}] Adding elements to the UI...")

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
        logging.debug(f"[{self.__class__.__name__}] UI setup completed.")

    def on_unload(self, ui):
        try:
            with ui._lock:
                ui.remove_element('latitude')
                ui.remove_element('longitude')
                ui.remove_element('altitude')
        except:
            pass

    def on_ui_update(self, ui):
        try:
            if all([self.lat, self.long, self.lat]):
                ui.set("latitude", "%.4f " % self.lat)
                ui.set("longitude", "%.4f " % self.long)
                ui.set("altitude", "%.2fm" % self.alt)
            else:
                ui.set("latitude", "???")
                ui.set("longitude", "???")
                ui.set("altitude", "???")
                self.lat = 0
                self.long = 0
                self.alt = 0
        except Exception as e:
            logging.error(f"[{self.__class__.__name__}] Error updating UI: {e}")
