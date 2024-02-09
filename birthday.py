import os
import json
import logging
import datetime
from dateutil.relativedelta import relativedelta

import pwnagotchi
import pwnagotchi.plugins as plugins
import pwnagotchi.ui.fonts as fonts
from pwnagotchi.ui.components import LabeledValue
from pwnagotchi.ui.view import BLACK


class Birthday(plugins.Plugin):
    __GitHub__ = ""
    __author__ = "(edited by: itsdarklikehell bauke.molenaar@gmail.com), nullm0ose"
    __version__ = "1.0."
    __license__ = "MIT"
    __description__ = "A plugin that shows the age and birthday of your Pwnagotchi."
    __name__ = "Birthday"
    __help__ = "A plugin that shows the age and birthday of your Pwnagotchi."
    __dependencies__ = {
        "apt": ["none"],
        "pip": ["none"],
    }
    __defaults__ = {
        "enabled": False,
    }

    def __init__(self):
        self.born_at = 0
        logging.debug(f"[{self.__class__.__name__}] plugin init")

    def on_loaded(self):
        data_path = "/root/brain.json"
        self.load_data(data_path)
        logging.info(f"[{self.__class__.__name__}] plugin loaded")

    def on_ui_setup(self, ui):
        if self.options["show_age"]:
            ui.add_element(
                "Age",
                LabeledValue(
                    color=BLACK,
                    label=" ♥ Age ",
                    value="",
                    position=(
                        int(self.options["age_x_coord"]),
                        int(self.options["age_y_coord"]),
                    ),
                    label_font=fonts.Bold,
                    text_font=fonts.Medium,
                ),
            )
        elif self.options["show_birthday"]:
            ui.add_element(
                "Birthday",
                LabeledValue(
                    color=BLACK,
                    label=" ♥ Born: ",
                    value="",
                    position=(
                        int(self.options["age_x_coord"]),
                        int(self.options["age_y_coord"]),
                    ),
                    label_font=fonts.Bold,
                    text_font=fonts.Medium,
                ),
            )

    def on_unload(self, ui):
        with ui._lock:
            try:
                ui.remove_element("Age")
            except Exception as e:
                logging.error(f"[{self.__class__.__name__}] unload: %s" % e)
        with ui._lock:
            try:
                ui.remove_element("Birthday")
            except Exception as e:
                logging.error(f"[{self.__class__.__name__}] unload: %s" % e)
        logging.info(f"[{self.__class__.__name__}] plugin unloaded")

    def on_ui_update(self, ui):
        if self.options["show_age"]:
            age = self.calculate_age()
            age_labels = []
            if age[0] == 1:
                age_labels.append(f"{age[0]}Yr")
            elif age[0] > 1:
                age_labels.append(f"{age[0]}Yrs")
            if age[1] > 0:
                age_labels.append(f"{age[1]}m")
            if age[2] > 0:
                if age[0] < 1:
                    age_labels.append(f"{age[2]} days")
                else:
                    age_labels.append(f"{age[2]}d")
            age_string = " ".join(age_labels)
            ui.set("Age", age_string)
        elif self.options["show_birthday"]:
            born_date = datetime.datetime.fromtimestamp(self.born_at)
            birthday_string = born_date.strftime("%b %d '%y")
            ui.set("Birthday", birthday_string)

    def load_data(self, data_path):
        if os.path.exists(data_path):
            with open(data_path) as f:
                data = json.load(f)
                self.born_at = data["born_at"]

    def calculate_age(self):
        born_date = datetime.datetime.fromtimestamp(self.born_at)
        today = datetime.datetime.now()
        age = relativedelta(today, born_date)
        return age.years, age.months, age.days

    def on_webhook(self, path, request):
        logging.info(f"[{self.__class__.__name__}] webhook pressed")
