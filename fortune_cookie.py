from pwnagotchi.ui.components import LabeledValue
from pwnagotchi.ui.view import BLACK
import pwnagotchi.ui.fonts as fonts
import pwnagotchi.plugins as plugins
import pwnagotchi
import logging
import random


class FortuneCookiePlugin(plugins.Plugin):
    __author__ = '@vanshksingh'
    __version__ = '1.0.0'
    __license__ = 'GPL3'
    __description__ = 'A plugin to display fortune cookie messages'

    def on_loaded(self):
        logging.info("FortuneCookiePlugin loaded")

    def on_ui_setup(self, ui):
        if ui.is_waveshare_v2():
            position = (0, 95)
        elif ui.is_waveshare_v3():
            position = (0, 95)
        elif ui.is_waveshare_v1():
            position = (0, 95)
        elif ui.is_waveshare144lcd():
            position = (0, 92)
        elif ui.is_inky():
            position = (0, 83)
        elif ui.is_waveshare27inch():
            position = (0, 153)
        else:
            position = (0, 91)

        if self.options['orientation'] == "vertical":
            ui.add_element('fortune-cookie', LabeledValue(color=BLACK, label='', value='',
                                                   position=position,
                                                   label_font=fonts.Bold, text_font=fonts.Small))
        else:
            # default to horizontal
            ui.add_element('fortune-cookie', LabeledValue(color=BLACK, label='', value='',
                                                   position=position,
                                                   label_font=fonts.Bold, text_font=fonts.Small))

    def on_unload(self, ui):
        with ui._lock:
            ui.remove_element('fortune-cookie')

    def on_ui_update(self, ui):
        fortunes = [
            "You will have a successful hacking session!",
            "Good fortune will come your way.",
            "Be prepared for a surprise in your network captures!",
            "Your Pwnagotchi is feeling lucky today.",
        ]

        if self.options['enabled']:
            fortune = random.choice(fortunes)
        else:
            fortune = 'Fortune Cookie Plugin is disabled'

        ui.set('fortune-cookie', fortune)
