from pwnagotchi.ui.components import LabeledValue
from pwnagotchi.ui.view import BLACK
import pwnagotchi.ui.fonts as fonts
import pwnagotchi.plugins as plugins
import logging
import os


class ShowPwd(plugins.Plugin):
    __GitHub__ = ""
    __author__ = "(edited by: itsdarklikehell bauke.molenaar@gmail.com), @jayofelony"
    __version__ = "1.0.1"
    __name__ = "Show Pwd"
    __license__ = "GPL3"
    __description__ = "A plugin to display recently cracked passwords"

    def __init__(self):
        self.options = dict()

    def on_loaded(self):
        logging.info(f"[{self.__class__.__name__}] plugin loaded")
        if "orientation" not in self.options:
            self.options["orientation"] = "horizontal"

    def on_ui_setup(self, ui):
        if self.options["orientation"] == "vertical":
            ui.add_element(
                "show_pwd",
                LabeledValue(
                    color=BLACK,
                    label="",
                    value="",
                    position=(180, 61),
                    label_font=fonts.Bold,
                    text_font=fonts.Small,
                ),
            )
        else:
            # default to horizontal
            ui.add_element(
                "show_pwd",
                LabeledValue(
                    color=BLACK,
                    label="",
                    value="",
                    position=(0, 91),
                    label_font=fonts.Bold,
                    text_font=fonts.Small,
                ),
            )

    def on_unload(self, ui):
        with ui._lock:
            ui.remove_element("show_pwd")

    def on_ui_update(self, ui):
        last_line = os.popen(
            "awk -F: '!seen[$3]++ {print $3 \" - \" $4}' /root/handshakes/wpa-sec.cracked.potfile | tail -n 1"
        )
        last_line = last_line.read().rstrip()
        ui.set("show_pwd", "%s" % last_line)

    def on_webhook(self, path, request):
        logging.info(f"[{self.__class__.__name__}] webhook pressed")
