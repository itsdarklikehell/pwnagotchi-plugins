import logging
import requests
import pwnagotchi.ui.components as components
import pwnagotchi.ui.view as view
import pwnagotchi.ui.fonts as fonts
import pwnagotchi.plugins as plugins
import pwnagotchi

class WeatherForecast(plugins.Plugin):
    __author__ = 'Your Name'
    __version__ = '1.0.0'
    __license__ = 'GPL3'
    __description__ = 'A plugin that displays the weather forecast on the pwnagotchi screen'

    def on_loaded(self):
        logging.info("Weather Forecast Plugin loaded.")

    def on_ui_setup(self, ui):
        # add a LabeledValue element to the UI with the given label and value
        # the position and font can also be specified
        ui.add_element('weather_forecast', components.LabeledValue(color=view.BLACK, label='', value='',
                                                                   position=(120, 80), label_font=fonts.Small, text_font=fonts.Small))

    def on_ui_update(self, ui):
        location = "Enter your location here"

        # replace "API_KEY" with your own API key from OpenWeatherMap
        api_key = "API_KEY"
        weather_url = f"https://api.openweathermap.org/data/2.5/weather?q={location}&units=metric&appid={api_key}"
        forecast_url = f"https://api.openweathermap.org/data/2.5/forecast?q={location}&units=metric&appid={api_key}"

        try:
            # make a request to the weather API
            weather_response = requests.get(weather_url).json()
            forecast_response = requests.get(forecast_url).json()

            # get the current temperature and weather description
            current_temp = weather_response['main']['temp']
            current_description = weather_response['weather'][0]['description']

            # get the forecast for the next 24 hours
            forecast = forecast_response['list']
            forecast_temp = forecast[0]['main']['temp']
            forecast_description = forecast[0]['weather'][0]['description']

            # update the value of the 'weather_forecast' element with the current temperature and weather description
            ui.set('weather_forecast', f"{current_temp}°C {current_description}\n{forecast_temp}°C {forecast_description}")
        except:
            # if there is an error making the request or parsing the response, display an error message
            ui.set('weather_forecast', "Error getting weather forecast")
