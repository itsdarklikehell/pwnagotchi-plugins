from pwnagotchi.ui.components import LabeledValue
from pwnagotchi.ui.view import BLACK
import pwnagotchi.ui.fonts as fonts
import pwnagotchi.plugins as plugins
import pwnagotchi
import logging
import datetime

class PwnClock(plugins.Plugin):
    __author__ = 'originally https://github.com/LoganMD redone by NeonLightning'
    __version__ = '1.0.3'
    __license__ = 'GPL3'
    __description__ = 'Clock/Calendar for pwnagotchi'

    def on_loaded(self):
        logging.info("Pwnagotchi Clock Plugin loaded.")

    def on_ui_setup(self, ui):
        pos1 = (100, 0)
        ui.add_element('clock1', LabeledValue(color=BLACK, label='', value='-/-/-',
                                                position=pos1,
                                                label_font=fonts.Small, text_font=fonts.Small))
        pos2 = (100,95)
        ui.add_element('clock2', LabeledValue(color=BLACK, label='', value='-:--',
                                                position=pos2,
                                                label_font=fonts.Small, text_font=fonts.Small))
        
    def on_ui_update(self, ui):
        now = datetime.datetime.now()
        datenow = now.strftime("%m/%d/%y")
        timenow = now.strftime("%I:%M%p")
        ui.set('clock1', datenow)
        ui.set('clock2', timenow)

    def on_unload(self, ui):
        with ui._lock:
            ui.remove_element('clock1')
            ui.remove_element('clock2')
