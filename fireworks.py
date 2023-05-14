import logging

from pwnagotchi import plugins
from pwnagotchi.ui import fonts
from pwnagotchi.ui.components import LabeledValue
from pwnagotchi.ui.view import BLACK

import random
import math
import time
import colorsys
import ledshim


class Fireworks(plugins.Plugin):
    __author__ = 'iggdawg'
    __version__ = '1.0.0'
    __name__ = 'fireworks'
    __license__ = 'MIT'
    __description__ = 'Uses Pimoroni shim to put on a light show '

    def on_loaded(self):
        logging.info("Fireworks locked and loaded")
        ledshim.clear()
        ledshim.show()

    # Bring in the cylon when we're waiting
    def on_wait(self, agent, t):
        FALLOFF = 1.9
        SCAN_SPEED = 4

        # ledshim.set_brightness(0.4)

        ledshim.set_clear_on_exit()
        ledshim.clear()
        ledshim.show()

        # Buffering start and end time to avoid hitting associations,
        # deauths, and handshakes since it can bug out the wait cycle
        time.sleep(1)

        start_time = time.time()
        while (time.time() - start_time) < (t - 2):
            delta = (time.time() - start_time)
            offset = (math.sin(delta * SCAN_SPEED) + 1) / 2
            hue = int(round(offset * 360))
            max_val = ledshim.NUM_PIXELS - 1
            offset = int(round(offset * max_val))
            for x in range(ledshim.NUM_PIXELS):
                sat = 1.0
                val = max_val - (abs(offset - x) * FALLOFF)
                val /= float(max_val)   # Convert to 0.0 to 1.0
                val = max(val, 0.0)     # Ditch negative values

                r, g, b = [255, 0, 0]
                ledshim.set_pixel(x, r, g, b, val / 4)

            ledshim.show()
            time.sleep(0.001)

        ledshim.clear()
        ledshim.show()

    # Sparkle teal when we associate
    def on_association(self, agent, access_point):

        ledshim.set_clear_on_exit()
        ledshim.clear()
        ledshim.show()

        num = 5

        while num >= 0:
            pixels = random.sample(range(ledshim.NUM_PIXELS),
                                   random.randint(1, 5))
            for i in range(ledshim.NUM_PIXELS):
                if i in pixels:
                    ledshim.set_pixel(i, 0, 255, 255)
                else:
                    ledshim.set_pixel(i, 0, 0, 0)
            ledshim.show()
            num -= 1
            time.sleep(0.02)

        ledshim.clear()
        ledshim.show()

    # Sparkle red when we deauth
    def on_deauthentication(self, agent, access_point, client_station):

        ledshim.set_clear_on_exit()
        ledshim.clear()
        ledshim.show()

        num = 5

        while num >= 0:
            pixels = random.sample(range(ledshim.NUM_PIXELS),
                                   random.randint(1, 5))
            for i in range(ledshim.NUM_PIXELS):
                if i in pixels:
                    ledshim.set_pixel(i, 255, 0, 0)
                else:
                    ledshim.set_pixel(i, 0, 0, 0)
            ledshim.show()
            num -= 1
            time.sleep(0.02)

        ledshim.clear()
        ledshim.show()

    # Taste the rainbow when we get a handshake
    def on_handshake(self, agent, filename, access_point, client_station):

        ledshim.set_clear_on_exit()
        ledshim.clear()
        ledshim.show()

        num = 20

        while num >= 0:
            pixels = random.sample(range(ledshim.NUM_PIXELS),
                                   random.randint(1, 5))
            for i in range(ledshim.NUM_PIXELS):
                if i in pixels:
                    ledshim.set_pixel(i, random.randint(0, 255),
                                      random.randint(0, 255),
                                      random.randint(0, 255))
                else:
                    ledshim.set_pixel(i, 0, 0, 0)
            ledshim.show()
            num -= 1
            time.sleep(0.001)

        ledshim.clear()
        ledshim.show()
