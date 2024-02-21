###
# main.plugins.weather.enabled = true
# main.plugins.weather.api_key = ""
# https://home.openweathermap.org/api_keys
# main.plugins.weather.areacode = "postal or zip"
# main.plugins.weather.countrycode = "countrycode"
# main.plugins.weather.gpson = true or false
# but if you want gps for weather you'll need gps.py or gps_more.py

import os, logging, re, pwnagotchi, toml, json, requests, urllib.request, shutil
from pwnagotchi import plugins, config
import pwnagotchi.ui.components as components
import pwnagotchi.ui.view as view
import pwnagotchi.ui.fonts as fonts
import pwnagotchi.plugins as plugins
from pwnagotchi.ui.components import Text
from pwnagotchi.bettercap import Client
from PIL import ImageDraw, ImageOps, Image

agent = Client('localhost', port=8081, username="pwnagotchi", password="pwnagotchi");

class WeatherIcon(pwnagotchi.ui.components.Widget):
    def __init__(self, value="", position=(0, 0), color=0, png=False):
        super().__init__(position, color)
        self.value = value

    def draw(self, canvas, drawer):
        if self.value is not None:
            self.image = Image.open(self.value)
            self.image = self.image.convert('RGBA')
            self.pixels = self.image.load()
            for y in range(self.image.size[1]):
                for x in range(self.image.size[0]):
                    if self.pixels[x,y][3] < 255:    # check alpha
                        self.pixels[x,y] = (255, 255, 255, 255)
            if self.color == 255:
                self._image = ImageOps.colorize(self.image.convert('L'), black = "white", white = "black")
            else:
                self._image = self.image
            self.image = self._image.convert('1')
            canvas.paste(self.image, self.xy)    

class WeatherForecast(plugins.Plugin):
    __author__ = 'NeonLightning'
    __version__ = '1.4.0'
    __license__ = 'GPL3'
    __description__ = 'A plugin that displays the weather forecast on the pwnagotchi screen.'
    __name__ = 'WeatherForecast'

    def _is_internet_available(self):
        try:
            urllib.request.urlopen('https://www.google.com', timeout=1)
            return True
        except urllib.request.URLError:
            return False
        
    def on_loaded(self):
        self.previous_seticon = None
        self.areacode = None
        self.country = None
        self.lat = None
        self.lon = None
        self.cords = None
        self.weather_response = None
        self.plugin_dir = os.path.dirname(os.path.realpath(__file__))
        self.icon_path = os.path.join(self.plugin_dir, "weather", "display.png")
        self.api_key = config['main']['plugins']['weather']['api_key']
        self.areacode = config['main']['plugins']['weather']['areacode']
        self.country = config['main']['plugins']['weather']['countrycode']
        self.gpson = config['main']['plugins']['weather']['gpson']
        self.geo_url = f"http://api.openweathermap.org/geo/1.0/zip?zip={self.areacode},{self.country}&appid={self.api_key}"

    def on_ready(self, agent):
        self.timer = 12
        if self._is_internet_available():
                self._update_lat_lon()
                self.weather_response = requests.get(self.weather_url).json()
                logging.info("Weather Ready")

    def _update_lat_lon(self):
        if self.gpson == True:
            if config['main']['plugins']['gps']['enabled'] or config['main']['plugins']['gps_more']['enabled']:
                try:
                    info = agent.session()
                    coords = info.get("gps", {})
                    if all([coords.get("Latitude"), coords.get("Longitude")]):
                        self.lat = coords["Latitude"]
                        self.lon = coords["Longitude"]
                except Exception as err:
                    logging.warn(f"Failed to get GPS coordinates: {err}")
            else:
                pass
        else:
            logging.debug("weather update location gps disabled")
            try:
                geo_response = requests.get(self.geo_url).json()
                self.lat = geo_response.get('lat')
                self.lon = geo_response.get('lon')
            except Exception as err:
                logging.error(f"Error fetching latitude:{self.lat} and longitude:{self.lon} error:{err}")
        self.weather_url = f"https://api.openweathermap.org/data/2.5/weather?lat={self.lat}&lon={self.lon}&appid={self.api_key}"
        logging.debug (f"weather url: {self.weather_url}")
        if self._is_internet_available():
            self.weather_response = requests.get(self.weather_url).json()

    def on_ui_setup(self, ui):
        ui.add_element('icon', WeatherIcon(value=self.icon_path, png=True, position=(147, 35)))        
        ui.add_element('feels', components.LabeledValue(color=view.BLACK, label='', value='',
                                                                   position=(90, 85), label_font=fonts.Small, text_font=fonts.Small))
        ui.add_element('main', components.LabeledValue(color=view.BLACK, label='', value='',
                                                            position=(90, 100), label_font=fonts.Small, text_font=fonts.Small))
        self._update_lat_lon()
        logging.debug("Weather ui set")
    
    def on_epoch(self, agent, epoch, epoch_data):
        if self._is_internet_available():
            if self.timer >= 12:
                self.weather_response = requests.get(self.weather_url).json()
                self.timer = 0
                logging.info("Weather Updated")
            else:
                self.timer += 1

    def on_ui_update(self, ui):
        if self.weather_response:
            try:
                tempk = self.weather_response['main']['feels_like']
                tempc = round(tempk - 273.15, 1)
                description = self.weather_response['weather'][0]['main']
                seticon = self.weather_response['weather'][0]['icon']
                source_path = os.path.join(self.plugin_dir, "weather", f"{seticon}.png")
                if seticon != self.previous_seticon:
                    if os.path.exists(source_path):
                        logging.debug(f"Weather Copying icon from {source_path}")
                        shutil.copy(source_path, os.path.join(self.plugin_dir, "weather", "display.png"))
                    else:
                        ui.set('main', 'WTHR: Icon Not Found')
                        logging.error(f"Weather ERROR: ICON NOT FOUND {source_path}")
                    self.previous_seticon = seticon
                ui.set('feels', f"TEMP:{tempc}°C")
                ui.set('main', f"WTHR:{description}")
            except Exception as e:
                ui.set('main', 'WTHR: Error')
                ui.set('feels', f'Temp: {e}')
                logging.exception(f"Weather ERROR: {e}")

    def on_unload(self, ui):
        with ui._lock:
            try:
                ui.remove_element('feels')
            except KeyError:
                pass
            try:
                ui.remove_element('main')
            except KeyError:
                pass
            try:
                ui.remove_element('icon')
                self.icon_path = os.path.join(self.plugin_dir, "weather", "circle.png")
                shutil.copy(self.icon_path, os.path.join(self.plugin_dir, "weather", "display.png"))
            except KeyError:
                pass
            logging.info("Weather Plugin unloaded")
