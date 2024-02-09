import os
import logging
import re
import subprocess
from io import TextIOWrapper
from pwnagotchi import plugins
from pwnagotchi.utils import StatusFile
import requests
import pwnagotchi.ui.components as components
import pwnagotchi.ui.view as view
import pwnagotchi.ui.fonts as fonts
import pwnagotchi.plugins as plugins
import pwnagotchi
import pwnagotchi.ui.fonts as fonts
import pwnagotchi.plugins as plugins
import datetime
import toml
import yaml
import json


class WeatherForecast(plugins.Plugin):
    __author__ = "(edited by: itsdarklikehell bauke.molenaar@gmail.com), Bauke Molenaar"
    __version__ = "1.0.0"
    __license__ = "GPL3"
    __description__ = (
        "A plugin that displays the weather forecast on the pwnagotchi screen."
    )
    __name__ = "WeatherForecast"
    __help__ = "A plugin that displays the weather forecast on the pwnagotchi screen."
    __dependencies__ = {
        "pip": ["scapy"],
    }
    __defaults__ = {
        "enabled": False,
    }

    def on_loaded(self):
        logging.info(f"[{self.__class__.__name__}] plugin loaded")

    def on_ui_setup(self, ui):
        config_is_toml = (
            True if os.path.exists("/etc/pwnagotchi/config.toml") else False
        )
        config_path = (
            "/etc/pwnagotchi/config.toml"
            if config_is_toml
            else "/etc/pwnagotchi/config.yml"
        )
        with open(config_path) as f:
            data = (
                toml.load(f) if config_is_toml else yaml.load(
                    f, Loader=yaml.FullLoader)
            )

        # add a LabeledValue element to the UI with the given label and value
        # the position and font can also be specified
        ui.add_element(
            "weather_forecast",
            components.LabeledValue(
                color=view.BLACK,
                label="",
                value="",
                position=(120, 80),
                label_font=fonts.Small,
                text_font=fonts.Small,
            ),
        )

    def on_ui_update(self, ui):
        location = "Leeuwarden"

        # replace "API_KEY" with your own API key from OpenWeatherMap
        api_key = "3d34a7f2abb93ca1fd5a5e4aa28db151"
        weather_url = f"https://api.openweathermap.org/data/2.5/weather?q={location}&units=metric&appid={api_key}"
        forecast_url = f"https://api.openweathermap.org/data/2.5/forecast?q={location}&units=metric&appid={api_key}"

        try:
            # make a request to the weather API
            weather_response = requests.get(weather_url).json()
            forecast_response = requests.get(forecast_url).json()

            # get the current temperature and weather description
            current_temp = weather_response["main"]["temp"]
            current_description = weather_response["weather"][0]["description"]

            # get the forecast for the next 24 hours
            forecast = forecast_response["list"]
            forecast_temp = forecast[0]["main"]["temp"]
            forecast_description = forecast[0]["weather"][0]["description"]

            # update the value of the 'weather_forecast' element with the current temperature and weather description
            ui.set(
                "weather_forecast",
                f"{current_temp}°C {current_description}\n{forecast_temp}°C {forecast_description}",
            )
        except:
            # if there is an error making the request or parsing the response, display an error message
            ui.set("weather_forecast", "Error getting weather forecast")

    def on_unload(self, ui):
        with ui._lock:
            try:
                ui.remove_element("weather_forecast")
                logging.info(f"[{self.__class__.__name__}] plugin unloaded")
            except Exception as e:
                logging.error(f"[{self.__class__.__name__}] unload: %s" % e)

    def on_webhook(self, path, request):
        logging.info(f"[{self.__class__.__name__}] webhook pressed")
