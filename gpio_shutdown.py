from pwnagotchi import plugins
from RPi import GPIO
import logging
import pwnagotchi


class GPIOShutdown(plugins.Plugin):
    __author__ = "(edited by: itsdarklikehell bauke.molenaar@gmail.com), tomelleri.riccardo@gmail.com"
    __version__ = "2.0.0"
    __license__ = "GPL3"
    __description__ = "GPIO Shutdown plugin."
    __name__ = "GPIOShutdown"
    __help__ = "GPIO Shutdown plugin."
    __dependencies__ = {
        "pip": ["RPi.GPIO"],
    }
    __defaults__ = {
        "enabled": False,
        "gpio": 21,
    }

    def __init__(self):
        self.ready = False
        logging.debug(f"[{self.__class__.__name__}] plugin init")
        self.title = ""

    def shutdown(self, channel):
        logging.warn(
            f"[{self.__class__.__name__}] Received shutdown command from GPIO")
        pwnagotchi.shutdown()

    def on_loaded(self):
        logging.info(f"[{self.__class__.__name__}] plugin loaded")

        shutdown_gpio = self.options["gpio"]
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(shutdown_gpio, GPIO.IN, GPIO.PUD_UP)
        GPIO.add_event_detect(shutdown_gpio, GPIO.FALLING,
                              callback=self.shutdown)

        logging.info(
            f"[{self.__class__.__name__}] Added shutdown command to GPIO %d",
            shutdown_gpio,
        )

    def on_unload(self, ui):
        logging.info(f"[{self.__class__.__name__}] plugin unloaded")

    def on_webhook(self, path, request):
        logging.info(f"[{self.__class__.__name__}] webhook pressed")
