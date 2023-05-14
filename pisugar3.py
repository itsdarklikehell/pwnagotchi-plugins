# Based on UPS Lite v1.1 from https://github.com/xenDE

import logging
import struct

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

    def voltage(self):
        try:
            low = self._bus.read_byte_data(0x57, 0x23)
            high = self._bus.read_byte_data(0x57, 0x22)
            v = (((high << 8) + low)/1000)
            return v
        except:
            return 0.0

    def charge(self):
        is_charging = 0
        chg = ''
        try:
            is_charging = self._bus.read_byte_data(0x57, 0x02)
            #124 unplugged
            #252 plugged
            if is_charging >= 200 : chg = 'âš¡'
            return chg
        except:
            return chg
       
    def capacity(self):
        battery_level = 0
        # battery_v = self.voltage()
        try:
            battery_level = self._bus.read_byte_data(0x57, 0x2a)
            return battery_level
        except:
            return battery_level

class PiSugar3(plugins.Plugin):
    __author__ = 'taiyonemo@protonmail.com'
    __version__ = '1.0.0'
    __license__ = 'GPL3'
    __description__ = 'A plugin that will add a percentage indicator for the PiSugar 3'

    def __init__(self):
        self.ups = None

    def on_loaded(self):
        self.ups = UPS()
        logging.info("[pisugar3] plugin loaded.")

    def on_ui_setup(self, ui):
        ui.add_element('bat', LabeledValue(color='BLACK', label='BAT', value='0%/0V', position=(35, 0),
                                           label_font=fonts.Bold, text_font=fonts.Bold))

        ui.add_element('chg', LabeledValue(color='BLACK', label='', value='', position=(80, 0),
                                           label_font=fonts.Bold, text_font=fonts.Bold))


    def on_unload(self, ui):
        with ui._lock:
            ui.remove_element('bat')

    def on_ui_update(self, ui):
        capacity = self.ups.capacity()
        chg = self.ups.charge()
        ui.set('bat', "%2i%%" % capacity)
        ui.set('chg', "%s" % chg)
        if capacity <= self.options['shutdown']:
            logging.info('[pisugar3] Empty battery (<= %s%%): shuting down' % self.options['shutdown'])
            ui.update(force=True, new_data={'status': 'Battery exhausted, bye ...'})
            pwnagotchi.shutdown()
