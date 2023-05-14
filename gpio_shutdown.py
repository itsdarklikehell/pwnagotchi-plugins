from pwnagotchi import plugins
from RPi import GPIO
import logging
import pwnagotchi


class GPIOShutdown(plugins.Plugin):
    __author__ = 'tomelleri.riccardo@gmail.com'
    __version__ = '2.0.0'
    __license__ = 'GPL3'
    __description__ = 'GPIO Shutdown plugin'
    __dependencies__ = {
        'pip': ['RPi.GPIO'],
    }
    __defaults__ = {
        'enabled': False,
        'gpio': 21,
    }

    def shutdown(self, channel):
        logging.warning('[gpioshutdown] Received shutdown command from GPIO')
        pwnagotchi.shutdown()

    def on_loaded(self):
        logging.info('[gpioshutdown] GPIO Shutdown plugin loaded')

        shutdown_gpio = self.options['gpio']
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(shutdown_gpio, GPIO.IN, GPIO.PUD_UP)
        GPIO.add_event_detect(shutdown_gpio, GPIO.FALLING, callback=self.shutdown)

        logging.info('[gpioshutdown] Added shutdown command to GPIO %d', shutdown_gpio)
