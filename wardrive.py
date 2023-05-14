from pwnagotchi.ui.components import LabeledValue
from pwnagotchi.ui.view import BLACK
import pwnagotchi.ui.fonts as fonts
import pwnagotchi.plugins as plugins
import pwnagotchi
import logging
import datetime
import toml
import yaml
import json
from threading import Lock
import subprocess


class Wardrive(plugins.Plugin):
    __author__ = '@tjbishop'
    __version__ = '1.0.0'
    __license__ = 'GPL3'
    __description__ = 'Wardriving plugin for pwnagotchi'

    def __init__(self):
        self.data = None
        self.last_seen_ap = '---'
        self.lock = Lock()

    def on_loaded(self):
        self.coordinates = None
        if 'date_format' in self.options:
            self.date_format = self.options['date_format']
        else:
            self.date_format = "%m/%d/%y"

        logging.info("Pwnagotchi [Wardrive] Plugin loaded.")

    def on_ui_setup(self, ui):
        memenable = False
        config_is_toml = True if os.path.exists(
            '/etc/pwnagotchi/config.toml') else False
        config_path = '/etc/pwnagotchi/config.toml' if config_is_toml else '/etc/pwnagotchi/config.yml'
        with open(config_path) as f:
            data = toml.load(f) if config_is_toml else yaml.load(
                f, Loader=yaml.FullLoader)

            if 'memtemp' in data["main"]["plugins"]:
                if 'enabled' in data["main"]["plugins"]["memtemp"]:
                    if data["main"]["plugins"]["memtemp"]["enabled"]:
                        memenable = True
                        logging.info(
                            "Wardrive: memtemp is enabled")
        if ui.is_waveshare_v2():
            pos = (130, 85) if memenable else (200, 85)
            pos2 = (70, 70) if memenable else (195, 70)
            ui.add_element('clock', LabeledValue(color=BLACK, label='', value='-/-/-\n-:--',
                                                 position=pos,
                                                 label_font=fonts.Small, text_font=fonts.Small))
            ui.add_element('wardriver', LabeledValue(color=BLACK, label='', value='WARDRIV\'N',
                                                     position=pos2,
                                                     label_font=fonts.Small, text_font=fonts.Small))

    def on_unfiltered_ap_list(self, agent, data):
        with self.lock:
            info = agent.session()
            self.coordinates = info["gps"]
            data = sorted(data, key=lambda k: k['mac'])
            self.data = json.dumps(data)
            json_data = json.loads(self.data)
            geo_json_array = []
            if json_data:
                for ap_data in json_data:
                    geo_json_array.append({
                        "type": "Feature",
                        "geometry": {
                            "type": "Point",
                            "coordinates": [self.coordinates["Longitude"], self.coordinates["Latitude"]]
                        },
                        "properties": {
                            "title": ap_data['hostname'],
                            "ap_data": ap_data
                        }
                    })
                    self.last_seen_ap = ap_data['hostname'] or ap_data['vendor'] or ap_data['mac']
                geo_json = {"type": "FeatureCollection",
                            "features": geo_json_array}
                with open("/root/custom_plugins/wardrive.json", 'w+t') as fp:
                    json.dump(geo_json, fp)

    def on_internet_available(self, agent):
        if self.coordinates and all([
            self.coordinates["Latitude"], self.coordinates["Longitude"]
        ]):
            subprocess.call(['rclone', 'copy', '/root/custom_plugins/wardrive.json', 'Gdrive:'])
            logging.info("Pwnagotchi [Wardrive] Sync complete")

    def on_ui_update(self, ui):
        now = datetime.datetime.now()
        time_rn = now.strftime(self.date_format + "\n%I:%M %p")

        if self.coordinates and all([
            self.coordinates["Latitude"], self.coordinates["Longitude"]
        ]):
            ui.set("latitude", f"{self.coordinates['Latitude']:.4f} ")
            ui.set("longitude", f"{self.coordinates['Longitude']:.4f} ")
            ui.set("altitude", f"{self.coordinates['Altitude']:.1f}m ")

        ui.set('clock', time_rn)
        ui.set('wardriver', self.last_seen_ap)
