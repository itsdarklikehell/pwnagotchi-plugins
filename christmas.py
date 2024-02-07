from pwnagotchi.ui.components import LabeledValue
from pwnagotchi.ui.view import BLACK
from pwnagotchi.ui import fonts
from pwnagotchi import plugins
import logging
import datetime
import toml
import yaml


class Christmas(plugins.Plugin):
    __author__ = "https://github.com/LoganMD"
    __version__ = "2.0.0"
    __license__ = "GPL3"
    __description__ = "Christmas Countdown timer for pwnagotchi."
    __name__ = "Christmas"
    __help__ = "Christmas Countdown timer for pwnagotchi."
    __dependencies__ = {
        "apt": ["none"],
        "pip": ["datetime", "yaml", "toml"],
    }
    __defaults__ = {
        "enabled": False,
    }

    def __init__(self):
        self.ready = False
        logging.info(f"[{self.__class__.__name__}] plugin init")
        self.title = ""

    def on_loaded(self):
        logging.info(f"[{self.__class__.__name__}] plugin loaded")

    def on_ui_setup(self, ui):
        try:
            memenable = False
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
                            logging.info("[christmas] memtemp is enabled")
            # if ui.is_waveshare_v2():
            pos = (130, 80) if memenable else (200, 80)
            ui.add_element(
                "christmas",
                LabeledValue(
                    color=BLACK,
                    label="",
                    value="christmas\n",
                    position=pos,
                    label_font=fonts.Small,
                    text_font=fonts.Small,
                ),
            )
        except Exception as wtf:
            logging.error("[christmas] %s" % repr(wtf))

    def on_unload(self, ui):
        with ui._lock:
            ui.remove_element("christmas")
            logging.info(f"[{self.__class__.__name__}] plugin unloaded")

    def on_ui_update(self, ui):
        try:
            now = datetime.datetime.now()
            christmas = datetime.datetime(now.year, 12, 25)
            if now > christmas:
                christmas = christmas.replace(year=now.year + 1)

            difference = christmas - now

            days = difference.days
            hours = difference.seconds // 3600
            minutes = (difference.seconds % 3600) // 60

            if now.month == 12 and now.day == 25:
                ui.set("christmas", "merry\nchristmas!")
            elif days == 0:
                ui.set("christmas", "christmas\n%dH %dM" % (hours, minutes))
            else:
                ui.set("christmas", "christmas\n%dD %dH" % (days, hours))
        except Exception as wtf:
            logging.error("[christmas] %s" % repr(wtf))
