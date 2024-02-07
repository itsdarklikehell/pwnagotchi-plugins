import logging
import json
import os
import pwnagotchi.plugins as plugins
import RPi.GPIO as GPIO
import time

LEDs = {"green": 17, "yellow": 22, "red": 27}


def Blink(LED, times=1):
    count = 0
    led_active = False
    led_state = GPIO.LOW
    if GPIO.input(LED) == GPIO.HIGH:
        led_state = GPIO.HIGH
    while count < times:
        if led_active:
            GPIO.output(LED, GPIO.LOW)
            led_active = False
        else:
            count += 1
            GPIO.output(LED, GPIO.HIGH)
            led_active = True
        time.sleep(0.5)
    GPIO.output(LED, led_state)


class BasicLight(plugins.Plugin):
    __author__ = "github.com/shir0tetsuo"
    __version__ = "1.0.0"
    __license__ = "GPL3"
    __description__ = "GPIO traffic-light signals."
    __name__ = "BasicLight"
    __help__ = "GPIO traffic-light signals."
    __dependencies__ = {
        "pip": ["none"],
    }
    __defaults__ = {
        "enabled": False,
    }

    def __init__(self):
        self.running = False
        logging.info(f"[{self.__class__.__name__}] plugin init")
        self.title = ""

    # Plugin load, switch Yellow high
    def on_loaded(self):
        global LEDs
        GPIO.setmode(GPIO.BCM)
        for LED in LEDs:
            Lnum = LEDs[LED]
            GPIO.setup(Lnum, GPIO.OUT)
        GPIO.output(LEDs["yellow"], GPIO.HIGH)
        GPIO.output(LEDs["green"], GPIO.LOW)
        logging.info(f"[{self.__class__.__name__}] plugin loaded")

    # On ready, switch Yellow low
    def on_ready(self, agent):
        global LEDs
        logging.info("Basic Lights ready.")
        GPIO.output(LEDs["yellow"], GPIO.LOW)
        GPIO.output(LEDs["green"], GPIO.HIGH)
        self.running = True

        ############

    # -X-
    def on_ai_training_start(self, agent, epochs):
        global LEDs
        GPIO.output(LEDs["green"], GPIO.LOW)

    # X--
    def on_ai_training_end(self, agent):
        global LEDs
        GPIO.output(LEDs["green"], GPIO.HIGH)

    # XX-
    def on_sleep(self, agent, t):
        global LEDs
        count_sleep = t
        flip = True
        while count_sleep > 0:
            if flip:
                GPIO.output(LEDs["yellow"], GPIO.HIGH)
                flip = False
            else:
                GPIO.output(LEDs["yellow"], GPIO.LOW)
                flip = True
            time.sleep(1)
            count_sleep -= 1
        GPIO.output(LEDs["yellow"], GPIO.LOW)

    # X-X
    def on_wait(self, agent, t):
        global LEDs
        Blink(LEDs["red"], 1)

    # -X- (B)
    def on_wifi_update(self, agent, access_points):
        global LEDs
        Blink(LEDs["yellow"], 1)

    # X-- (B)
    def on_handshake(self, agent, filename, access_point, client_station):
        global LEDs
        Blink(LEDs["yellow"], 3)

    # --X (B)
    def on_deauthentication(self, agent, access_point, client_station):
        global LEDs
        Blink(LEDs["red"], 3)

    def on_unload(self, ui):
        with ui._lock:
            logging.info(f"[{self.__class__.__name__}] plugin unloaded")
