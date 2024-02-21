# Based on UPS Lite v1.1 from https://github.com/xenDE

import logging
import struct
import time

from pwnagotchi.ui.components import LabeledValue
from pwnagotchi.ui.view import BLACK
import pwnagotchi.ui.fonts as fonts
import pwnagotchi.plugins as plugins
import pwnagotchi

class UPS:
    def __init__(self):
        # only import when the module is loaded and enabled
        import smbus
        # 0 = /dev/i2c-0 (port I2C0), 1 = /dev/i2c-1 (port I2C1)
        self._bus = smbus.SMBus(1)

    def capacity(self):
        battery_level = 0
        try:
            battery_level = self._bus.read_byte_data(0x57, 0x2a)
            return battery_level
        except:
            return battery_level

    def status(self):
        stat02 = self._bus.read_byte_data(0x57, 0x02)
        stat03 = self._bus.read_byte_data(0x57, 0x03)
        stat04 = self._bus.read_byte_data(0x57, 0x04)
        return stat02, stat03, stat04

class PiSugar3(plugins.Plugin):
    __author__ = 'taiyonemo@protonmail.com edited by neonlightning'
    __version__ = '1.0.3'
    __license__ = 'GPL3'
    __description__ = 'A plugin that will add a percentage indicator for the PiSugar 3'

    def __init__(self):
        self.ups = None

    def on_loaded(self):
        self.ups = UPS()
        logging.info("[pisugar3] plugin loaded.")

    def on_ui_setup(self, ui):
        try:
            ui.add_element('bat', LabeledValue(color=BLACK, label='BAT :', value='0%', position=(ui.width() / 2 + 10, 0),
                                               label_font=fonts.Bold, text_font=fonts.Medium))
        except Exception as err:
            logging.warning("pisugar3 setup err: %s" % repr(err))

    def on_unload(self, ui):
        try:
            with ui._lock:
                ui.remove_element('bat')
        except Exception as err:
            logging.warning("pisugar3 unload err: %s" % repr(err))

    def on_ui_update(self, ui):
        capacity = self.ups.capacity()
        stats = self.ups.status()
        if stats[0] & 0x80:
            ui._state._state['bat'].label = "CHG :"
        else:
            ui._state._state['bat'].label = "BAT :"
        ui.set('bat', "%2i%%" % (capacity))

        if capacity <= self.options['shutdown']:
            logging.info('[pisugar3] Battery capacity low. Checking multiple times before shutdown.')
            capacities = [capacity]
            for _ in range(5):
                time.sleep(.5)
                capacity = self.ups.capacity()
                capacities.append(capacity)
            max_capacity = max(capacities)
            logging.info('[pisugar3] Maximum battery capacity: %2i%%' % max_capacity)
            if max_capacity <= self.options['shutdown']:
                logging.info('[pisugar3] Battery capacity reached threshold (<= %s%%): shutting down' % self.options['shutdown'])
                ui.update(force=True, new_data={'status': 'Battery exhausted, bye ...'})
                pwnagotchi.shutdown()
