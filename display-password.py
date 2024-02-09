# display-password shows recently cracked passwords on the pwnagotchi display
#
#
###############################################################
#
# Inspired by, and code shamelessly yoinked from
# the pwnagotchi memtemp.py plugin by https://github.com/xenDE
#
###############################################################
from pwnagotchi.ui.components import LabeledValue
from pwnagotchi.ui.view import BLACK
import pwnagotchi.ui.fonts as fonts
import pwnagotchi.plugins as plugins
import pwnagotchi
import logging
import os


class DisplayPassword(plugins.Plugin):
    __author__ = "SgtStroopwafel, @nagy_craig"
    __version__ = "1.0.0"
    __license__ = "GPL3"
    __description__ = "A plugin to display recently cracked passwords"
    __name__ = "DisplayPassword"
    __help__ = "A plugin to display recently cracked passwords"
    __dependencies__ = {
        "apt": ["none"],
        "pip": ["scapy"],
    }
    __defaults__ = {
        "enabled": False,
        "orientation": "horizontal",
        "potfile": "/root/handshakes/wpa-sec.cracked.potfile",
    }

    def __init__(self):
        self.ready = False
        logging.debug(f"[{self.__class__.__name__}] plugin init")
        self.title = ""

    def on_loaded(self):
        logging.info(f"[{self.__class__.__name__}] plugin loaded")

    def on_ui_setup(self, ui):
        if ui.is_waveshare_v2():
            h_pos = (0, 95)
            v_pos = (180, 61)
        elif ui.is_waveshare_v1():
            h_pos = (0, 95)
            v_pos = (170, 61)
        elif ui.is_waveshare144lcd():
            h_pos = (0, 92)
            v_pos = (78, 67)
        elif ui.is_inky():
            h_pos = (0, 83)
            v_pos = (165, 54)
        elif ui.is_waveshare27inch():
            h_pos = (0, 153)
            v_pos = (216, 122)
        elif ui.is_waveshare35lcd():
            h_pos = (0, 150)
            v_pos = (200, 152)
        else:
            h_pos = (0, 91)
            v_pos = (180, 61)

        if self.options["orientation"] == "vertical":
            ui.add_element(
                "display-password",
                LabeledValue(
                    color=BLACK,
                    label="",
                    value="",
                    position=v_pos,
                    label_font=fonts.Bold,
                    text_font=fonts.Small,
                ),
            )
        else:
            # default to horizontal
            ui.add_element(
                "display-password",
                LabeledValue(
                    color=BLACK,
                    label="",
                    value="",
                    position=h_pos,
                    label_font=fonts.Bold,
                    text_font=fonts.Small,
                ),
            )

    def on_unload(self, ui):
        with ui._lock:
            try:
                ui.remove_element("display-password")
                logging.info(f"[{self.__class__.__name__}] plugin unloaded")
            except Exception as e:
                logging.error(f"[{self.__class__.__name__}] unload: %s" % e)

    def on_ui_update(self, ui):
        last_line = "tail -n 1 /root/handshakes/wpa-sec.cracked.potfile | awk -F: '{print $3 \" - \" $4}'"
        ui.set("display-password", "%s" % (os.popen(last_line).read().rstrip()))

    def on_webhook(self, path, request):
        logging.info(f"[{self.__class__.__name__}] webhook pressed")
        last_line = "tail -n 1 /root/handshakes/wpa-sec.cracked.potfile | awk -F: '{print $3 \" - \" $4}'"
        ui.set("display-password", "%s" % (os.popen(last_line).read().rstrip()))
