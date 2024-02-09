###
# main.plugins.weather.enabled = true
# main.plugins.weather.api_key = ""
# https://home.openweathermap.org/api_keys
# main.plugins.weather.areacode = "postal or zip"
# main.plugins.weather.countrycode = "countrycode"
# make sure you have the correct icons in (your plugin folder)/weather/
# (disabled for now)hmain.plugins.weather.gpson = true or false
# (disabled for now)but if you want gps for weather you'll need gps.py or gps_more.py

import logging
import pwnagotchi
import json
import requests
import urllib.request
import os
import shutil
import time
from pwnagotchi import plugins, config
import pwnagotchi.ui.components as components
import pwnagotchi.ui.view as view
import pwnagotchi.ui.fonts as fonts
import pwnagotchi.plugins as plugins
from pwnagotchi.ui.components import Text
from pwnagotchi.bettercap import Client
from PIL import ImageOps, Image

# agent = Client('localhost', port=8081, username="pwnagotchi", password="pwnagotchi");


class WeatherIcon(pwnagotchi.ui.components.Widget):
    def __init__(self, value="", position=(0, 0), color=0, png=False):
        super().__init__(position, color)
        self.value = value

    def draw(self, canvas, drawer):
        if self.value is not None:
            self.image = Image.open(self.value)
            self.image = self.image.convert("RGBA")
            self.pixels = self.image.load()
            for y in range(self.image.size[1]):
                for x in range(self.image.size[0]):
                    if self.pixels[x, y][3] < 255:  # check alpha
                        self.pixels[x, y] = (255, 255, 255, 255)
            if self.color == 255:
                self._image = ImageOps.colorize(
                    self.image.convert("L"), black="white", white="black"
                )
            else:
                self._image = self.image
            self.image = self._image.convert("1")
            canvas.paste(self.image, self.xy)


class WeatherForecast(plugins.Plugin):
    __GitHub__ = ""
    __author__ = "(edited by: itsdarklikehell bauke.molenaar@gmail.com), NeonLightning"
    __version__ = "1.5.0"
    __license__ = "GPL3"
    __description__ = (
        "A plugin that displays the weather forecast on the pwnagotchi screen."
    )
    __name__ = "WeatherForecast"
    __help__ = "A plugin that will add age and strength stats based on epochs and trained epochs"
    __dependencies__ = {
        "apt": ["none"],
        "pip": ["scapy"],
    }
    __defaults__ = {
        "enabled": False,
    }

    def _is_internet_available(self):
        try:
            urllib.request.urlopen("https://www.google.com", timeout=1)
            return True
        except urllib.request.URLError:
            return False

    def __init__(self):
        self.ready = False
        logging.debug(f"[{self.__class__.__name__}] plugin init")
        self.title = ""

    def on_loaded(self):
        logging.info(f"[{self.__class__.__name__}] plugin loaded")
        self.previous_seticon = None
        self.areacode = None
        self.country = None
        self.lat = None
        self.lon = None
        self.cords = None
        self.weather_response = None
        self.readyweathertimer = 0
        self.plugin_dir = os.path.dirname(os.path.realpath(__file__))
        self.icon_path = os.path.join(
            os.path.dirname(os.path.realpath(__file__)
                            ), "weather", "display.png"
        )
        logging.debug(f"weathericon: {self.icon_path}")
        self.api_key = config["main"]["plugins"]["weather"]["api_key"]
        self.areacode = config["main"]["plugins"]["weather"]["areacode"]
        self.country = config["main"]["plugins"]["weather"]["countrycode"]
        # self.gpson = config['main']['plugins']['weather']['gpson']
        self.gpson = False
        self.geo_url = f"http://api.openweathermap.org/geo/1.0/zip?zip={self.areacode},{self.country}&appid={self.api_key}"

    def on_ready(self, agent):
        if self._is_internet_available():
            self._update_lat_lon()
            self.weather_response = requests.get(self.weather_url).json()
        else:
            logging.info(f"[{self.__class__.__name__}] plugin not ready")
        logging.info(f"[{self.__class__.__name__}] plugin ready")

    def _update_lat_lon(self):
        if self.gpson == True:
            if (
                config["main"]["plugins"]["gps"]["enabled"]
                or config["main"]["plugins"]["gps_more"]["enabled"]
            ):
                try:
                    info = agent.session()
                    coords = info.get("gps", {})
                    if all([coords.get("Latitude"), coords.get("Longitude")]):
                        self.lat = coords["Latitude"]
                        self.lon = coords["Longitude"]
                except Exception as err:
                    logging.warn(
                        f"[{self.__class__.__name__}] Failed to get GPS coordinates: {err}"
                    )
            else:
                pass
        else:
            logging.debug("weather update location gps disabled")
            try:
                geo_response = requests.get(self.geo_url).json()
                self.lat = geo_response.get("lat")
                self.lon = geo_response.get("lon")
            except Exception as err:
                logging.error(
                    f"[{self.__class__.__name__}] Error fetching latitude:{self.lat} and longitude:{self.lon} error:{err}"
                )
        self.weather_url = f"https://api.openweathermap.org/data/2.5/weather?lat={self.lat}&lon={self.lon}&appid={self.api_key}"
        logging.debug(f"weather url: {self.weather_url}")
        if self._is_internet_available():
            self.weather_response = requests.get(self.weather_url).json()

    def on_ui_setup(self, ui):
        ui.add_element(
            "weathericon",
            WeatherIcon(value=self.icon_path, png=True, position=(147, 35)),
        )
        ui.add_element(
            "weatherfeels",
            components.LabeledValue(
                color=view.BLACK,
                label="",
                value="",
                position=(90, 85),
                label_font=fonts.Small,
                text_font=fonts.Small,
            ),
        )
        ui.add_element(
            "weather",
            components.LabeledValue(
                color=view.BLACK,
                label="",
                value="",
                position=(90, 100),
                label_font=fonts.Small,
                text_font=fonts.Small,
            ),
        )
        self._update_lat_lon()
        logging.debug("Weather ui set")

    def on_epoch(self, agent, epoch, epoch_data):
        if self._is_internet_available():
            if self.timer >= 12:
                self.weather_response = requests.get(self.weather_url).json()
                self.timer = 0
                logging.info(f"[{self.__class__.__name__}] Weather Updated")
            else:
                self.timer += 1

    def on_ui_update(self, ui):
        if self.weather_response:
            try:
                if "main" in self.weather_response:
                    tempk = self.weather_response["main"]["feels_like"]
                    tempc = round(tempk - 273.15, 1)
                    description = self.weather_response["weather"][0]["main"]
                    seticon = self.weather_response["weather"][0]["icon"]
                    source_path = os.path.join(
                        os.path.dirname(os.path.realpath(__file__)),
                        "weather",
                        f"{seticon}.png",
                    )
                    if seticon != self.previous_seticon:
                        if os.path.exists(source_path):
                            logging.debug(
                                f"[{self.__class__.__name__}] Weather Copying icon from {source_path}"
                            )
                            shutil.copy(
                                source_path,
                                os.path.join(
                                    os.path.dirname(
                                        os.path.realpath(__file__)),
                                    "weather",
                                    "display.png",
                                ),
                            )
                        else:
                            ui.set("main", "WTHR: Icon Not Found")
                            logging.error(
                                f"[{self.__class__.__name__}] Weather ERROR: ICON NOT FOUND {source_path}"
                            )
                        self.previous_seticon = seticon
                    ui.set("weatherfeels", f"TEMP:{tempc}°C")
                    ui.set("weather", f"WTHR:{description}")
            except Exception as e:
                ui.set("weather", "WTHR: Error")
                ui.set("weatherfeels", f"Temp: {e}")
                logging.exception(
                    f"[{self.__class__.__name__}] Weather ERROR: {e}")

    def on_unload(self, ui):
        with ui._lock:
            try:
                ui.remove_element("weatherfeels")
            except KeyError:
                pass
            try:
                ui.remove_element("weather")
            except KeyError:
                pass
            try:
                ui.remove_element("weathericon")
                self.icon_path = os.path.join(
                    os.path.dirname(os.path.realpath(__file__)
                                    ), "weather", "circle.png"
                )
                shutil.copy(
                    self.icon_path,
                    os.path.join(
                        os.path.dirname(os.path.realpath(__file__)),
                        "weather",
                        "display.png",
                    ),
                )
            except KeyError:
                pass
            logging.info(f"[{self.__class__.__name__}] plugin unloaded")

    def on_webhook(self, path, request):
        logging.info(f"[{self.__class__.__name__}] webhook pressed")
