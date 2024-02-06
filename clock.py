from pwnagotchi.ui.components import LabeledValue
from pwnagotchi.ui.view import BLACK
import pwnagotchi.ui.fonts as fonts
import pwnagotchi.plugins as plugins
import pwnagotchi
import logging
import datetime
import os
import toml
import yaml


class PwnClock(plugins.Plugin):
    __author__ = "https://github.com/LoganMD"
    __version__ = "1.0.2"
    __license__ = "GPL3"
    __description__ = "Clock/Calendar for pwnagotchi"

    def on_loaded(self):
        if "date_format" in self.options:
            self.date_format = self.options["date_format"]
        else:
            self.date_format = "%m/%d/%y"

        logging.info("Pwnagotchi Clock Plugin loaded.")

    def on_ui_setup(self, ui):
        try:
            memenable = False
            logging.info("Pwnagotchi Clock Plugin setup started.")
            config_is_toml = (
                True if os.path.exists("/etc/pwnagotchi/config.toml") else False
            )
            config_path = (
                "/etc/pwnagotchi/config.toml"
                if config_is_toml
                else "/etc/pwnagotchi/config.yml"
            )
            with open(config_path) as f:
                data = (
                    toml.load(f)
                    if config_is_toml
                    else yaml.load(f, Loader=yaml.FullLoader)
                )

                if "memtemp" in data["main"]["plugins"]:
                    if "enabled" in data["main"]["plugins"]["memtemp"]:
                        if data["main"]["plugins"]["memtemp"]["enabled"]:
                            memenable = True
                            logging.info("Pwnagotchi Clock Plugin: memtemp is enabled")
            # if ui.is_waveshare_v2():
            pos = (130, 80) if memenable else (20, 40)
            ui.add_element(
                "clock",
                LabeledValue(
                    color=BLACK,
                    label="",
                    value="-/-/-\n-:--",
                    position=pos,
                    label_font=fonts.Small,
                    text_font=fonts.Small,
                ),
            )
        except Exception as wtf:
            logging.error("[clock] %s" % repr(wtf))

    def on_unload(self, ui):
        with ui._lock:
            ui.remove_element("clock")

    def on_ui_update(self, ui):
        try:
            now = datetime.datetime.now()
            # Format the date and time as desired
            time_rn = now.strftime("%Y-%m-%d %H:%M")
            ui.set("clock", time_rn)
        except Exception as wtf:
            logging.error("[clock] %s" % repr(wtf))
