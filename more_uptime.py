import logging
import os, time

import pwnagotchi.plugins as plugins
from pwnagotchi.ui.components import LabeledValue, Text
from pwnagotchi.ui.view import BLACK
import pwnagotchi.ui.fonts as fonts
import pwnagotchi.utils as utils


class More_Uptime(plugins.Plugin):
    __author__ = "SgtStroopwafel, evilsocket@gmail.com"
    __version__ = "1.0.0"
    __license__ = "GPL3"
    __description__ = "Enable and disable ASSOC  on the fly. Enabled when plugin loads, disabled when plugin unloads."
    __name__ = "More_Uptime"
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
        self._start = time.time()
        pass

    def on_webhook(self, path, request):
        logging.info(f"[{self.__class__.__name__}] webhook pressed")

    # called when the plugin is loaded
    def on_loaded(self):
        self._start = time.time()
        self._state = 0
        self._next = 0
        logging.info(f"[{self.__class__.__name__}] plugin loaded")
        pass

    # called before the plugin is unloaded
    def on_unload(self, ui):
        try:
            if ui.has_element("more_uptime"):
                ui.remove_element("more_uptime")
                logging.info(f"[{self.__class__.__name__}] plugin unloaded")
        except Exception as err:
            logging.warn(f"[{self.__class__.__name__}] %s" % repr(err))

    # called when everything is ready and the main loop is about to start
    def on_ready(self, agent):
        self._agent = agent

    # called to setup the ui elements
    def on_ui_setup(self, ui):
        try:
            # add custom UI elements
            if not "override" in self.options or not self.options["override"]:
                if "position" in self.options:
                    pos = self.options["position"].split(",")
                    pos = [int(x.strip()) for x in pos]
                else:
                    pos = (ui.width() - 58, 12)

                    ui.add_element(
                        "more_uptime",
                        Text(
                            color=BLACK,
                            value="up --:--",
                            position=pos,
                            font=fonts.Small,
                        ),
                    )
        except Exception as err:
            logging.warn(f"[{self.__class__.__name__}] ui setup: %s" % repr(err))

    HZ = os.sysconf(os.sysconf_names["SC_CLK_TCK"])

    def on_ui_update(self, ui):
        # update those elements
        try:
            if time.time() > self._next:
                self._next = int(time.time()) + 5
                self._state = (self._state + 1) % 3
            uptimes = open("/proc/uptime").read().split()
            label = "UP"
            if self._state == 2:
                # system uptime
                res = utils.secs_to_hhmmss(float(uptimes[0]))
                label = "UP"
            elif self._state == 1:
                # get time since pwnagotchi process started
                process_stats = open("/proc/self/stat").read().split()
                res = utils.secs_to_hhmmss(
                    float(uptimes[0]) - (int(process_stats[21]) / self.HZ)
                )
                label = "PR"
            else:
                # instance, since plugin loaded
                res = utils.secs_to_hhmmss(time.time() - self._start)
                label = "IN"
            logging.debug(f"[{self.__class__.__name__}] %s: %s" % (label, res))
            # hijack the stock uptime view, modify label as needed
            if "override" in self.options and self.options["override"]:
                try:
                    uiItems = ui._state._state
                    uiItems["uptime"].label = label
                except Exception as err:
                    logging.warn(
                        f"[{self.__class__.__name__}] label hijack err: %s", (repr(err))
                    )
                ui.set("uptime", res)
            else:
                ui.set("more_uptime", "%s %s" % (label, res))
        except Exception as err:
            logging.warn(
                f"[{self.__class__.__name__}] ui update: %s, %s"
                % (repr(err), repr(uiItems))
            )
