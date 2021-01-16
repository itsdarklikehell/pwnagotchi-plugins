from pwnagotchi.ui.components import LabeledValue
from pwnagotchi.ui.view import BLACK
import pwnagotchi.ui.fonts as fonts
import pwnagotchi.plugins as plugins
import pwnagotchi
import logging
import urllib.request
from urllib.error import HTTPError
from datetime import datetime, timezone, timedelta
import json


class MemTemp(plugins.Plugin):
    __author__ = 'https://github.com/jfrader'
    __version__ = '0.0.1'
    __license__ = 'GPL3'
    __description__ = 'A plugin that will display the bitcoin price'

    def on_loaded(self):
        logging.info("bitcoin plugin loaded.")

    def fetch_prices():
        timeslot_end = datetime.now(timezone.utc)
        timeslot_start = timeslot_end - timedelta(days=1)
        req = urllib.request.Request("https://production.api.coindesk.com/v2/price/values/BTC?start_date="
                                     "%s&end_date=%s&ohlc=false" % (timeslot_start.strftime("%Y-%m-%dT%H:%M"),
                                                                    timeslot_end.strftime("%Y-%m-%dT%H:%M")))
        data = urllib.request.urlopen(req).read()
        external_data = json.loads(data)
        prices = [entry[1] for entry in external_data['data']['entries']]
        return prices

    def on_ui_setup(self, ui):
        if ui.is_waveshare_v2():
            h_pos = (180, 80)
            v_pos = (180, 61)
        elif ui.is_waveshare_v1():
            h_pos = (170, 80)
            v_pos = (170, 61)
        elif ui.is_waveshare144lcd():
            h_pos = (53, 77)
            v_pos = (78, 67)
        elif ui.is_inky():
            h_pos = (140, 68)
            v_pos = (165, 54)
        elif ui.is_waveshare27inch():
            h_pos = (192, 138)
            v_pos = (216, 122)
        else:
            h_pos = (155, 76)
            v_pos = (180, 61)

        if self.options['orientation'] == "vertical":
            ui.add_element('bitcoin', LabeledValue(color=BLACK, label='', value=' btc/usd:$-',
                                                   position=v_pos,
                                                   label_font=fonts.Small, text_font=fonts.Small))
        else:
            # default to horizontal
            ui.add_element('bitcoin', LabeledValue(color=BLACK, label='', value='btc/usd:\n $-',
                                                   position=h_pos,
                                                   label_font=fonts.Small, text_font=fonts.Small))

    def on_unload(self, ui):
        with ui._lock:
            ui.remove_element('bitcoin')

    def on_ui_update(self, ui):
        prices = fetch_prices()
        current_price = prices[len(prices) - 1]
        if self.options['memtemp']['enabled'] == True:
            if self.options['orientation'] == "vertical":
                ui.set('bitcoin', ' btc/usd:${}'.format(current_price))
            else:
                # default to horizontal
                ui.set('bitcoin',
                       ' btc/usd:\n ${} '.format(current_price))
