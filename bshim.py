#!/usr/bin/env python

import signal
import buttonshim
import subprocess
import sys
import os
libdir = '/home/pi/src/e-Paper/RaspberryPi_JetsonNano/python/lib'
if os.path.exists(libdir):
    sys.path.append(libdir)
import logging
from waveshare_epd import epd2in13b_V3
import time
from PIL import Image,ImageDraw,ImageFont
import traceback
import pwnagotchi.plugins as plugins

class Buttonshim(plugins.Plugin):
    __author__ = 'chris@holycityhosting.com'
    __version__ = '0.0.1'
    __license__ = 'GPL3'
    __description__ = 'Pimoroni Button Shim GPIO Button control'

print("""
Button SHIM: Control Panel
Press Ctrl+C to exit.
""")

@buttonshim.on_hold(buttonshim.BUTTON_A, hold_time=2)
def button_a(button):
    buttonshim.set_pixel(0x94, 0x00, 0xd3)
    try:
        os.popen("sudo systemctl restart pwnagotchi.service")
        print("Pwnagotchi service restarted successfully...")
    except OSError as ose:
        print("Error while running the command", ose)
    pass
    buttonshim.set_pixel(0x00, 0x00, 0x00)

@buttonshim.on_hold(buttonshim.BUTTON_B, hold_time=2)
def button_b(button):
    buttonshim.set_pixel(0x94, 0x00, 0xd3)
    try:
        os.popen("sudo systemctl start pwnagotchi.service")
        print("Pwnagotchi service started successfully...")
    except OSError as ose:
        print("Error while running the command", ose)
    pass
    buttonshim.set_pixel(0x00, 0x00, 0x00)

@buttonshim.on_hold(buttonshim.BUTTON_C, hold_time=2)
def button_c(button):
    buttonshim.set_pixel(0x94, 0x00, 0xd3)
    try:
        os.popen("sudo systemctl stop pwnagotchi.service")
        print("Pwnagotchi service stopped successfully...")
    except OSError as ose:
        print("Error while running the command", ose)
    pass
    buttonshim.set_pixel(0x00, 0x00, 0x00)

@buttonshim.on_press(buttonshim.BUTTON_D)
def button_d(button, pressing):
    acstat = subprocess.call(["systemctl", "is-active", "--quiet", "pwnagotchi"])
    if(acstat == 0):
      buttonshim.set_pixel(0, 255, 0)
    else:
      buttonshim.set_pixel(255, 0, 0)

@buttonshim.on_hold(buttonshim.BUTTON_D, hold_time=2)
def button_d(button):
      buttonshim.set_pixel(0, 0, 0)

@buttonshim.on_hold(buttonshim.BUTTON_E, hold_time=2)
def button_e(button):
    buttonshim.set_pixel(0x94, 0x00, 0xd3)
    logging.basicConfig(level=logging.DEBUG)
    try:
        epd = epd2in13b_V3.EPD()
        logging.info("Screen clean...")
        epd.init()
        epd.Clear()
        epd.Clear()
#        logging.info("Sleep screen...")
#        epd.sleep()
#    except IOError as e:
#        logging.info(e)
    except KeyboardInterrupt:
        logging.info("ctrl + c:")
        epd2in13b_V3.epdconfig.module_exit()
    buttonshim.set_pixel(0x00, 0x00, 0x00)

#signal.pause()
