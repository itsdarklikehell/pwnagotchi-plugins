import logging
import os
from time import sleep

import pwnagotchi
from pwnagotchi import plugins
import pwnagotchi.agent
import pwnagotchi.plugins as plugins
import pwnagotchi.ui.fonts as fonts
from pwnagotchi.ui.components import LabeledValue
from pwnagotchi.ui.view import BLACK


class Counter(plugins.Plugin):
    __author__ = "SgtStroopwafel, 33197631+dadav@users.noreply.github.com (made the plugin this is based on) + Terminator"
    __version__ = "1.0.0"
    __license__ = "GPL3"
    __description__ = (
        "This will add some UI stuff to your Pwnagotchi to count assocs and deauths!"
    )
    __name__ = "Counter"
    __help__ = (
        "This will add some UI stuff to your Pwnagotchi to count assocs and deauths!"
    )
    __dependencies__ = {
        "apt": ["none"],
        "pip": ["scapy"],
    }
    __defaults__ = {
        "enabled": False,
    }

    def __init__(self):
        self.options = dict()
        self.running = False
        self.deauth_counter = 0
        self.assoc_counter = 0
        logging.info(f"[{self.__class__.__name__}] plugin init")

    def on_loaded(self):
        logging.info(f"[{self.__class__.__name__}] plugin loaded")
        self.running = True

    def on_unload(self, ui):
        self.running = False
        logging.info(f"[{self.__class__.__name__}] plugin unloaded")

    def on_ui_setup(self, ui):
        ui.add_element(
            "deauth",
            LabeledValue(
                color=BLACK,
                label="Deauths:       ",
                value=str(self.deauth_counter),
                position=(ui.width() / 2, ui.height() - 46),
                label_font=fonts.Bold,
                text_font=fonts.Medium,
            ),
        )
        ui.add_element(
            "assocs",
            LabeledValue(
                color=BLACK,
                label="Associations:  ",
                value=str(self.assoc_counter),
                position=(ui.width() / 2, ui.height() - 26),
                label_font=fonts.Bold,
                text_font=fonts.Medium,
            ),
        )

    def on_ready(self, agent):
        logging.info(f"[{self.__class__.__name__}] plugin ready")
        self.agent = agent

    def on_ui_update(self, ui):
        ui.set("deauth", str(self.deauth_counter))
        ui.set("assocs", str(self.assoc_counter))

    def on_deauthentication(self, agent, access_point, client_station):
        self.deauth_counter += 1

    def on_association(self, agent, access_point):
        self.assoc_counter += 1

    def on_webhook(self, path, request):
        logging.info(f"[{self.__class__.__name__}] webhook pressed")
        pass
