import logging
import RPi.GPIO as GPIO
import subprocess
import time
import pwnagotchi.ui.faces as faces
import pwnagotchi.plugins as plugins


class TouchCounter:

    def __init__(self):
        self.count = 0
        self.last_timestamp = time.time()
        self.wait_timestamp = False

    def reset(self):
        self.count = 0
        self.last_timestamp = time.time()

    def wait(self, seconds):
        self.wait_timestamp = time.time() + seconds

    def press(self):
        t = time.time()

        if self.wait_timestamp:
            if self.wait_timestamp > t:
                return 0
            else:
                self.wait_timestamp = False

        if t - self.last_timestamp < 1:
            self.count += 1
            self.last_timestamp = t
        else:
            self.reset()

        return self.count


class WaveshareV3Touch(plugins.Plugin):
    __author__ = "SgtStroopwafel, sliim@mailoo.org"
    __version__ = "1.0.0"
    __license__ = "GPL3"
    __description__ = "Experimental plugin for Waveshare V3 2.13inch Touch e-Paper HAT."
    """
    Product: https://www.amazon.fr/gp/product/B09H4HZHXF
    Resources: https://www.waveshare.com/wiki/2.13inch_Touch_e-Paper_HAT
    Examples: https://github.com/waveshareteam/Touch_e-Paper_HAT/
    """

    def __init__(self):
        self.touch = TouchCounter()
        self.agent = None

    def callback(self, gpio):
        logging.info("CALLBACK %d" % gpio)
        if self.touch.press() >= 5:
            if self.agent:
                self.agent.view().set("status", "HiHiHiii")
                self.agent.view().set("face", faces.EXCITED)
                self.agent.view().update(force=True)
            self.touch.reset()
            self.touch.wait(5)

    def on_ready(self, agent):
        self.agent = agent

    def on_loaded(self):
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(17, GPIO.OUT)
        GPIO.setup(25, GPIO.OUT)
        GPIO.setup(8, GPIO.OUT)
        GPIO.setup(24, GPIO.IN)
        GPIO.setup(22, GPIO.OUT)
        GPIO.setup(27, GPIO.IN)
        GPIO.add_event_detect(27, GPIO.RISING, callback=self.callback, bouncetime=200)
        GPIO.add_event_detect(24, GPIO.RISING, callback=self.callback, bouncetime=200)
        logging.info("Waveshare V3 Touch plugin loaded.")

    def on_unload(self, ui):
        GPIO.output(17, 0)
        GPIO.output(25, 0)
        GPIO.output(8, 0)
        GPIO.output(22, 0)
        GPIO.cleanup()
