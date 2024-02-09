import logging

import pwnagotchi.plugins as plugins
from pwnagotchi.ui.components import LabeledValue
from pwnagotchi.ui.view import BLACK
import pwnagotchi.ui.fonts as fonts


class Do_Assoc(plugins.Plugin):
    __author__ = "SgtStroopwafel, evilsocket@gmail.com"
    __version__ = "1.0.0"
    __license__ = "GPL3"
    __description__ = "Enable and disable ASSOC  on the fly. Enabled when plugin loads, disabled when plugin unloads."
    __name__ = "Do_Assoc"
    __help__ = "Enable and disable ASSOC  on the fly. Enabled when plugin loads, disabled when plugin unloads."
    __dependencies__ = {
        "apt": ["none"],
        "pip": ["scapy"],
    }
    __defaults__ = {
        "enabled": False,
    }

    def __init__(self):
        self.ready = False
        logging.debug(f"[{self.__class__.__name__}] plugin init")
        self.title = ""
        self._agent = None
        self._count = 0

    def on_webhook(self, path, request):
        pass

    # called when the plugin is loaded
    def on_loaded(self):
        self._count = 0
        logging.info(f"[{self.__class__.__name__}] plugin loaded")

    # called before the plugin is unloaded
    def on_unload(self, ui):
        if self._agent:
            self._agent._config["personality"]["associate"] = False
        ui.remove_element("assoc_count")
        logging.info(f"[{self.__class__.__name__}] plugin unloaded")

    # called when everything is ready and the main loop is about to start
    def on_ready(self, agent):
        agent._config["personality"]["associate"] = True
        self._agent = agent
        logging.info(f"[{self.__class__.__name__}] ready: enabled association")

    def on_association(self, agent, access_point):
        self._count += 1

    # called to setup the ui elements
    def on_ui_setup(self, ui):
        # add custom UI elements
        if "position" in self.options:
            pos = self.options["position"].split(",")
            pos = [int(x.strip()) for x in pos]
        else:
            pos = (0, 29)

        ui.add_element(
            "assoc_count",
            LabeledValue(
                color=BLACK,
                label="A",
                value="0",
                position=pos,
                label_font=fonts.BoldSmall,
                text_font=fonts.Small,
            ),
        )

        # called when the ui is updated

    def on_ui_update(self, ui):
        # update those elements
        ui.set("assoc_count", "%d" % (self._count))
