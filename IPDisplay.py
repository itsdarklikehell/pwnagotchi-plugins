############################
# setup is simple
# main.plugins.IPDisplay.devices = [
#     'eth0',
#     'usb0',
#     'bnep0',
#     'wlan0',
#     'ect...'
# ]
# main.plugins.IPDisplay.position = "0, 82"

from pwnagotchi.ui.components import LabeledValue
from pwnagotchi.ui.view import BLACK
import pwnagotchi.ui.fonts as fonts
import pwnagotchi.plugins as plugins
import logging
import subprocess
import ipaddress


class IPDisplay(plugins.Plugin):
    __GitHub__ = ""
    __author__ = "(edited by: itsdarklikehell bauke.molenaar@gmail.com), NeonLightning(thank to NurseJackass and jayofelony)"
    __version__ = "1.0.0"
    __license__ = "GPL3"
    __description__ = "Display IP addresses on the Pwnagotchi UI"
    __name__ = "IPDisplay"
    __help__ = "Display IP addresses on the Pwnagotchi UI"
    __dependencies__ = {
        "apt": ["none"],
        "pip": ["scapy"],
    }
    __defaults__ = {
        "enabled": False,
    }

    def __init__(self):
        self.options = dict()
        self.device_list = ["bnep0", "usb0", "eth0"]
        self.device_index = 0
        self.ready = False
        logging.debug(f"[{self.__class__.__name__}] plugin init")
        self.title = ""

    def on_loaded(self):
        if "devices" in self.options:
            self.device_list = self.options["devices"]
        self.options["devices"] = self.device_list
        logging.info(f"[{self.__class__.__name__}] plugin loaded")

    def on_ready(self):
        self.ready = True
        logging.info(f"[{self.__class__.__name__}] plugin ready")

    def on_ui_setup(self, ui):
        pos1 = (0, 82)
        if "position" in self.options:
            pos1 = self.options["position"]
        ui.add_element(
            "ip1",
            LabeledValue(
                color=BLACK,
                label="",
                value="Initializing...",
                position=pos1,
                label_font=fonts.Small,
                text_font=fonts.Small,
            ),
        )

    def on_ui_update(self, ui):
        current_device = self.device_list[self.device_index]
        command = f"ip -4 addr show {current_device} | awk '/inet / {{print $2}}' | cut -d '/' -f 1 | head -n 1"
        netip = subprocess.getoutput(command).strip()
        if netip:
            try:
                ipaddress.ip_address(netip)
                ui.set("ip1", f"{current_device}:{netip}")
            except ValueError:
                logging.debug(
                    f"Invalid IP address found for {current_device}: {netip}")
        self.device_index = (self.device_index + 1) % len(self.device_list)

    def on_unload(self, ui):
        with ui._lock:
            self.ready = False
            ui.remove_element("ip1")
            logging.info(f"[{self.__class__.__name__}] plugin unloaded")

    def on_webhook(self, path, request):
        logging.info(f"[{self.__class__.__name__}] webhook pressed")
