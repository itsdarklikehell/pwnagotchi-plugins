from pwnagotchi.ui.components import LabeledValue
from pwnagotchi.ui.view import BLACK
import pwnagotchi.ui.fonts as fonts
import pwnagotchi.plugins as plugins
import pwnagotchi
import logging
import os


class DisplayPassword(plugins.Plugin):
    __author__ = '@7h30th3r0n3'
    __version__ = '1.0.0'
    __license__ = 'GPL3'
    __description__ = 'A plugin to display if aircrack is runing or not'

    def on_loaded(self):
        logging.info("[display-password] loaded")

    def on_ui_setup(self, ui):
        ui.add_element('aircrack-ng-status', LabeledValue(color=BLACK, label="", value='', position=(ui.width() // 2 - 10, 0), label_font=fonts.Bold, text_font=fonts.Medium))

    def on_unload(self, ui):
        with ui._lock:
            ui.remove_element('aircrack-ng-status')

    def on_ui_update(self, ui):
        #Check if aircrack-ng is running and update status display
        if "aircrack-ng" in os.popen("ps -A").read():
            ui.set('aircrack-ng-status', "(1)")
        else:
            ui.set('aircrack-ng-status', "(0)")
