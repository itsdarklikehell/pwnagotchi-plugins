from pwnagotchi.ui.components import LabeledValue, Text
from pwnagotchi.ui.view import BLACK
import pwnagotchi.ui.fonts as fonts
import pwnagotchi.plugins as plugins
import pwnagotchi
import logging
import psutil

""" Add support waveshare v3 display and display disk usage
    Based on orig memtemp plugin by https://github.com/xenDE """


class MemTempAdv(plugins.Plugin):
    __author__ = "https://github.com/mavotronik/pwnagotchi-plugins"
    __version__ = "1.2.0"
    __license__ = "MIT"
    __description__ = "A plugin that will display memory/cpu/disk usage and temperature"
    __name__ = "MemTempAdv"
    __help__ = "A plugin that will display memory/cpu/disk usage and temperature"
    __dependencies__ = {
        "apt": ["none"],
        "pip": ["scapy"],
    }
    __defaults__ = {
        "enabled": False,
    }

    ALLOWED_FIELDS = {
        "mem": "mem_usage",
        "cpu": "cpu_load",
        "temp": "cpu_temp",
        "freq": "cpu_freq",
        "disk": "disk_usage",
    }

    DEFAULT_FIELDS = ["mem", "cpu", "temp", "disk"]
    LINE_SPACING = 10
    LABEL_SPACING = 0
    FIELD_WIDTH = 4

    def __init__(self):
        self.ready = False
        logging.info(f"[{self.__class__.__name__}] plugin init")
        self.title = ""

    def on_loaded(self):
        logging.info(f"[{self.__class__.__name__}] plugin laoded")

    def mem_usage(self):
        mem = psutil.virtual_memory()
        return f"{(int(mem.percent))}%"

    def disk_usage(self):
        disk_ = psutil.disk_usage("/")
        return f"{(int(disk_.percent))}%"

    def cpu_load(self):
        cpu = psutil.cpu_percent()
        return f"{(int(cpu))}%"

    def cpu_temp(self):
        if self.options["scale"] == "fahrenheit":
            temp = (pwnagotchi.temperature() * 9 / 5) + 32
            symbol = "f"
        elif self.options["scale"] == "kelvin":
            temp = pwnagotchi.temperature() + 273.15
            symbol = "k"
        else:
            # default to celsius
            temp = pwnagotchi.temperature()
            symbol = "c"
        return f"{temp}{symbol}"

    def cpu_freq(self):
        with open("/sys/devices/system/cpu/cpu0/cpufreq/scaling_cur_freq", "rt") as fp:
            return f"{round(float(fp.readline())/1000000, 1)}G"

    def pad_text(self, data):
        return " " * (self.FIELD_WIDTH - len(data)) + data

    def on_ui_setup(self, ui):
        try:
            # Configure field list
            self.fields = self.options["fields"].split(",")
            self.fields = [
                x.strip()
                for x in self.fields
                if x.strip() in self.ALLOWED_FIELDS.keys()
            ]
            self.fields = self.fields[:4]  # limit to the first 4 fields
        except Exception:
            # Set default value
            self.fields = self.DEFAULT_FIELDS

        try:
            # Configure line_spacing
            line_spacing = int(self.options["linespacing"])
        except Exception:
            # Set default value
            line_spacing = self.LINE_SPACING

        try:
            # Configure position
            pos = self.options["position"].split(",")
            pos = [int(x.strip()) for x in pos]
            if self.options["orientation"] == "vertical":
                v_pos = (pos[0], pos[1])
            else:
                h_pos = (pos[0], pos[1])
        except Exception:
            # Set default position based on screen type
            if ui.is_waveshare_v2():
                h_pos = (178, 84)
                v_pos = (197, 74)
            elif ui.is_waveshare_v1():
                h_pos = (170, 80)
                v_pos = (165, 61)
            elif ui.is_waveshare144lcd():
                h_pos = (53, 77)
                v_pos = (73, 67)
            elif ui.is_inky():
                h_pos = (140, 68)
                v_pos = (160, 54)
            elif ui.is_waveshare27inch():
                h_pos = (192, 138)
                v_pos = (211, 122)
            elif ui.is_waveshare_v3():
                h_pos = (178, 85)
                y_pos = (197, 75)
            else:
                h_pos = (155, 76)
                v_pos = (175, 61)

        if self.options["orientation"] == "vertical":
            # Dynamically create the required LabeledValue objects
            for idx, field in enumerate(self.fields):
                v_pos_x = v_pos[0]
                v_pos_y = v_pos[1] + ((len(self.fields) - 3) * -1 * line_spacing)
                ui.add_element(
                    f"memtemp_{field}",
                    LabeledValue(
                        color=BLACK,
                        label=f"{self.pad_text(field)}:",
                        value="-",
                        position=(v_pos_x, v_pos_y + (idx * line_spacing)),
                        label_font=fonts.Small,
                        text_font=fonts.Small,
                        label_spacing=self.LABEL_SPACING,
                    ),
                )
        else:
            # default to horizontal
            h_pos_x = h_pos[0] + ((len(self.fields) - 3) * -1 * 25)
            h_pos_y = h_pos[1]
            ui.add_element(
                "memtemp_header",
                Text(
                    color=BLACK,
                    value=" ".join([self.pad_text(x) for x in self.fields]),
                    position=(h_pos_x, h_pos_y),
                    font=fonts.Small,
                ),
            )
            ui.add_element(
                "memtemp_data",
                Text(
                    color=BLACK,
                    value=" ".join([self.pad_text("-") for x in self.fields]),
                    position=(h_pos_x, h_pos_y + line_spacing),
                    font=fonts.Small,
                ),
            )

    def on_unload(self, ui):
        logging.info(f"[{self.__class__.__name__}] plugin unloaded")
        with ui._lock:
            if self.options["orientation"] == "vertical":
                for idx, field in enumerate(self.fields):
                    ui.remove_element(f"memtemp_{field}")
            else:
                # default to horizontal
                ui.remove_element("memtemp_header")
                ui.remove_element("memtemp_data")

    def on_ui_update(self, ui):
        if self.options["orientation"] == "vertical":
            for idx, field in enumerate(self.fields):
                ui.set(f"memtemp_{field}", getattr(self, self.ALLOWED_FIELDS[field])())
        else:
            # default to horizontal
            data = " ".join(
                [
                    self.pad_text(getattr(self, self.ALLOWED_FIELDS[x])())
                    for x in self.fields
                ]
            )
            ui.set("memtemp_data", data)
