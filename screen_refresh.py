from pwnagotchi import plugins
import logging


class ScreenRefresh(plugins.Plugin):
    __author__ = 'pwnagotchi [at] rossmarks [dot] uk'
    __version__ = '2.0.0'
    __license__ = 'GPL3'
    __description__ = 'Refresh he e-ink display after X amount of updates'
    __defaults__ = {
        'enabled': False,
        'refresh_interval': 50,
    }

    def __init__(self):
        self.update_count = 0

    def on_loaded(self):
        logging.info('[screenrefresh] Screen refresh plugin loaded')

    def on_ui_update(self, ui):
        self.update_count += 1
        if self.update_count == self.options['refresh_interval']:
            ui.init_display()
            ui.set('status', "Screen cleaned")
            logging.info('[screenrefresh] Screen refreshing')
            self.update_count = 0
