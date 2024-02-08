import logging
import RPi.GPIO as GPIO
import subprocess
import pwnagotchi.plugins as plugins


class GPIOButtons(plugins.Plugin):
    __author__ = "SgtStroopwafel, ratmandu@gmail.com"
    __version__ = "1.0.0"
    __license__ = "GPL3"
    __description__ = "GPIO Button support plugin"
    __name__ = "GPIOButtons"
    __help__ = "GPIO Button support plugin"
    __dependencies__ = {
        "apt": ["none"],
        "pip": ["scapy"],
    }
    __defaults__ = {
        "enabled": False,
    }

    def __init__(self):
        self.ready = False
        logging.info(f"[{self.__class__.__name__}] plugin init")
        self.title = ""
        self.ports = {}
        self.commands = None

    def runCommand(self, channel):
        command = self.ports[channel]
        logging.info(
            f"[{self.__class__.__name__}] Button Pressed! Running command: {command}"
        )
        process = subprocess.Popen(
            command,
            shell=True,
            stdin=None,
            stdout=open("/dev/null", "w"),
            stderr=None,
            executable="/bin/bash",
        )
        process.wait()

    def on_loaded(self):
        logging.info("[{self.__class__.__name__}] plugin loaded")

        # get list of GPIOs
        gpios = self.options["gpios"]

        # set gpio numbering
        GPIO.setmode(GPIO.BCM)

        for gpio, command in gpios.items():
            gpio = int(gpio)
            self.ports[gpio] = command
            GPIO.setup(gpio, GPIO.IN, GPIO.PUD_UP)
            GPIO.add_event_detect(
                gpio, GPIO.FALLING, callback=self.runCommand, bouncetime=600
            )
            # set pimoroni display hat mini LED off/dim
            GPIO.setup(17, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
            GPIO.setup(22, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
            GPIO.setup(27, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
            logging.info("Added command: %s to GPIO #%d", command, gpio)

    def on_unload(self, ui):
        logging.info(f"[{self.__class__.__name__}] plugin unloaded")

    def on_webhook(self, path, request):
        logging.info(f"[{self.__class__.__name__}] webhook pressed")
        pass
