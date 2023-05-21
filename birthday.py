from pwnagotchi.ui.components import LabeledValue
from pwnagotchi.ui.view import BLACK
import pwnagotchi.ui.fonts as fonts
import pwnagotchi.plugins as plugins
import pwnagotchi
import logging
import datetime
import math

month = (7)
day = (3)
class Christmas(plugins.Plugin):
    __author__ = 'https://github.com/LoganMD'
    __version__ = '1.3.5'
    __license__ = 'GPL3'
    __description__ = 'Birth Day Counter for pwnagotchi'

    def on_loaded(self):
        logging.info("Birth Day Counter Plugin loaded.")

    def on_ui_setup(self, ui):
        emenable = False
        
        with open('/etc/pwnagotchi/config.toml', 'r') as f:
            config = f.read().splitlines()

        if "main.plugins.memtemp.enabled = true" in config:
            memenable = True
            logging.info(
                "Birth Day Counter Plugin: memtemp is enabled")
                
        if ui.is_waveshare_v2():
            pos = (160, 95) if memenable else (160, 95)
            ui.add_element('birthday', LabeledValue(color=BLACK, label='', value='birthday\n',
                                                     position=pos,
                                                     label_font=fonts.Small, text_font=fonts.Small))

    def on_ui_update(self, ui):
        now = datetime.datetime.now()
        birthday = datetime.datetime(now.year, month, day)
        if now > birthday:
            birthday = birthday.replace(year=now.year + 1)

        difference = (birthday - now)

        days = difference.days
        hours = difference.seconds // 3600
        minutes = (difference.seconds % 3600) // 60

        if now.month == {month} and now.day == {day}:
            ui.set('birthday', "Happy bd!")
        elif days == 0:
            ui.set('birthday', "(%dH)" % (hours))
        else:
            ui.set('birthday', "(%dD)" % (days))
