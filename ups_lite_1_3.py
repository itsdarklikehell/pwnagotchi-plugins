# Base on pwnagotchi ups_lite plugin, V1.3 implementation.
#
# Based on UPS Lite v1.3 from https://github.com/linshuqin329/UPS-Lite/tree/master/UPS-Lite_V1.3_CW2015
#
# functions to get UPS status - needs enable "i2c" in raspi-config
#
# https://github.com/linshuqin329/UPS-Lite
#
# To display external power supply status you need to bridge the necessary pins on the UPS-Lite board. See instructions in the UPS-Lite repo.
import logging
import struct

import RPi.GPIO as GPIO

import pwnagotchi
import pwnagotchi.plugins as plugins
import pwnagotchi.ui.fonts as fonts
from pwnagotchi.ui.components import LabeledValue
from pwnagotchi.ui.view import BLACK


class UPS:
    def __init__(self):
        # only import when the module is loaded and enabled
        import smbus

        # 0 = /dev/i2c-0 (port I2C0), 1 = /dev/i2c-1 (port I2C1)
        self._bus = smbus.SMBus(1)

    def quick_start(self):
        try:
            address = 0x62
            self._bus.write_word_data(address, 0x0A, 0x30)
        except Exception as e:
            logging.error("[UPS] Failed to wake up the CW2015: %s" % e)

    def voltage(self):
        try:
            address = 0x62
            read = self._bus.read_word_data(address, 0x02)
            swapped = struct.unpack("<H", struct.pack(">H", read))[0]
            return swapped * 0.305 / 1000
        except:
            return 0.0

    def capacity(self):
        try:
            address = 0x62
            read = self._bus.read_word_data(address, 0x04)
            swapped = struct.unpack("<H", struct.pack(">H", read))[0]
            return swapped / 256
        except:
            return 0.0

    def charging(self):
        try:
            GPIO.setmode(GPIO.BCM)
            GPIO.setup(4, GPIO.IN)
            return "+" if GPIO.input(4) == GPIO.HIGH else "-"
        except:
            return "?"


class UPSLite(plugins.Plugin):
    __author__ = "evilsocket@gmail.com"
    __version__ = "1.0.0"
    __license__ = "GPL3"
    __description__ = "A plugin that will add a voltage indicator for the UPS Lite v1.1"

    def __init__(self):
        self.ups = None

    def on_loaded(self):
        self.ups = UPS()
        self.ups.quick_start()
        logging.info("[ups_lite] plugin loaded")

    def on_ui_setup(self, ui):
        ui.add_element(
            "ups",
            LabeledValue(
                color=BLACK,
                label="UPS",
                value="0%/0V",
                position=(ui.width() / 2 + 15, 0),
                label_font=fonts.Bold,
                text_font=fonts.Medium,
            ),
        )

    def on_unload(self, ui):
        with ui._lock:
            ui.remove_element("ups")

    def on_ui_update(self, ui):
        capacity = self.ups.capacity()
        charging = self.ups.charging()
        ui.set("ups", "%2i%s" % (capacity, charging))
        if capacity <= self.options["shutdown"] and charging == "-":
            logging.info(
                "[ups_lite] Empty battery (<= %s%%): shuting down"
                % self.options["shutdown"]
            )
            ui.update(force=True, new_data={"status": "Battery exhausted, bye ..."})
            pwnagotchi.shutdown()

    def on_webhook(self, path, request):
        logging.info(f"[{self.__class__.__name__}] webhook pressed")
