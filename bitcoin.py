from pwnagotchi.ui.components import LabeledValue
from pwnagotchi.ui.view import BLACK
import pwnagotchi.ui.fonts as fonts
import pwnagotchi.plugins as plugins
import pwnagotchi
import logging
import requests


class Bitcoin(plugins.Plugin):
    __author__ = "(edited by: itsdarklikehell bauke.molenaar@gmail.com), https://github.com/jfrader"
    __version__ = "0.0.1"
    __license__ = "GPL3"
    __description__ = "A plugin that will display the bitcoin price."
    __name__ = "Bitcoin"
    __help__ = "A plugin that will display the bitcoin price."
    __dependencies__ = {
        "apt": ["none"],
        "pip": ["requests"],
    }
    __defaults__ = {
        "enabled": False,
        "api_url": "https://coindesk.com",
        "bitcoin_api_url": "https://api.coindesk.com/v1/bpi/currentprice.json/",
    }

    _last_price = "..."
    _has_internet = False

    def on_loaded(self):
        logging.info(f"[{self.__class__.__name__}] plugin loaded")

    def _fetch_price(self):
        logging.info(f"[{self.__class__.__name__}]  fetching bitcoin price")
        bitcoin_api_url = "https://api.coindesk.com/v1/bpi/currentprice.json/"
        try:
            response = requests.get(bitcoin_api_url)
            response_json = response.json()
            return response_json["bpi"]["USD"]["rate"]
        except requests.exceptions.RequestException as e:
            self._has_internet = False
            return " - "

    def on_ui_setup(self, ui):
        if ui.is_waveshare_v2():
            h_pos = (180, 80)
        elif ui.is_waveshare_v1():
            h_pos = (170, 80)
        elif ui.is_waveshare144lcd():
            h_pos = (53, 77)
        elif ui.is_inky():
            h_pos = (140, 68)
        elif ui.is_waveshare27inch():
            h_pos = (192, 138)
        else:
            h_pos = (155, 76)

        ui.add_element(
            "bitcoin",
            LabeledValue(
                color=BLACK,
                label="",
                value=" BTC/USD: \n $ ",
                position=h_pos,
                label_font=fonts.Small,
                text_font=fonts.Small,
            ),
        )

    def on_unload(self, ui):
        with ui._lock:
            try:
                ui.remove_element("bitcoin")
                logging.info(f"[{self.__class__.__name__}] plugin unloaded")
            except Exception as e:
                logging.error(f"[{self.__class__.__name__}] unload: %s" % e)

    def on_ui_update(self, ui):
        ui.set("bitcoin", self._last_price)

    def on_internet_available(self, ui):
        self._has_internet = True

    def on_sleep(self):
        if self._has_internet == True:
            price = self._fetch_price()
            self._last_price = " BTC/USD: \n $%s " % price

    def on_webhook(self, path, request):
        logging.info(f"[{self.__class__.__name__}] webhook pressed")
