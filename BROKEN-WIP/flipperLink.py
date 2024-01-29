import logging
import os, sys, time, types, subprocess, signal
import subprocess
from threading import Lock

import bluetooth

import pwnagotchi.plugins as plugins
import pwnagotchi.ui.fonts as fonts
from pwnagotchi.ui.components import LabeledValue
from pwnagotchi.ui.view import BLACK
from pwnagotchi.utils import StatusFile


class FlipperLink(plugins.Plugin):
    __author__ = 'Allordacia'
    __version__ = '1.0.0'
    __license__ = 'MIT'
    __description__ = 'A plugin that will add functionality for pwnagotchi to connect to the Flipper Zero.'
    __name__ = 'FlipperLink'
    __help__ = """
    A plugin that will add functionality for pwnagotchi to connect to the Flipper Zero.
    """
    __dependencies__ = {
        'pip': ['scapy']
    }
    __defaults__ = {
        'enabled': False,
    }

    def __init__(self):
        self.running = False

    def on_loaded(self):
        self.flipper_connected = False
        self.flipper_connected = self.check_flipper()
        logging.info(self.flipper_connected)
        logging.info("FlipperLink plugin loaded.")

    def on_ready(self, agent):
        logging.info("FlipperLink plugin ready.")

    def on_ui_setup(self, ui):
        # Add elements to the UI
        ui.add_element('flipperlink', LabeledValue(color=BLACK, label='Flipper: ', value=self.flipper_connected,
                                           position=(2, ui.height() - 30),
                                           label_font=fonts.Bold, text_font=fonts.Medium))

    def on_unload(self, ui):
        with ui._lock:
            ui.remove_element('flipperlink')

    def on_ui_update(self, ui):
        # Update the UI

        if self.flipper_connected == True:
            ui.set('flipperlink', value='Connected')
        else:
            self.flipper_connected = self.check_flipper()
            if self.flipper_connected == True:
                ui.set('flipperlink', value='Connected')
            else:
                ui.set('flipperlink', value='Not Connected')

    def check_flipper(self):
        flipper_connected = False
        try:
            nearby_devices = bluetooth.discover_devices()
            for bdaddr in nearby_devices:
                if bdaddr == self.options['mac']:
                    flipper_connected = True
                    logging.info("Flipper device found with MAC address: %s", bdaddr)
                    break
        except bluetooth.BluetoothError as e:
            logging.error("Bluetooth error while searching for Flipper device: %s", e)
        except Exception as e:
            logging.error("Unexpected error while searching for Flipper device: %s", e)

        return flipper_connected




        return flipper_connected
