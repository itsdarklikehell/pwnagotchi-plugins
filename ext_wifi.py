import pwnagotchi.plugins as plugins
import pwnagotchi
import logging
import subprocess
import time


class ext_wifi(plugins.Plugin):
    __author__ = "SgtStroopwafel, chris@holycityhosting.com"
    __version__ = "1.0.0"
    __license__ = "GPL3"
    __description__ = "Activates external wifi adapter."
    __name__ = "ext_wifi"
    __help__ = "Activates external wifi adapter."
    __dependencies__ = {
        "pip": ["scapy"],
    }
    __defaults__ = {
        "enabled": False,
        "interface": "wlan0mon",
        "mode": "external",
    }

    def __init__(self):
        self.ready = False
        logging.info(f"[{self.__class__.__name__}] plugin init")
        self.title = ""
        self.status = ""
        self.network = ""

    def on_loaded(self):
        for opt in ["mode"]:
            if opt not in self.options or (
                opt in self.options and self.options[opt] is None
            ):
                logging.error(
                    f"Set WiFi adapter mode configuration for internal or external."
                )
                return
        _log("plugin loaded")
        logging.info(f"[{self.__class__.__name__}] plugin loaded")
        self.ready = 1
        mode = self.options["mode"]
        interface = self.options["interface"]
        if mode == "external":
            subprocess.run(
                "sed -i s/wlan0mon/{interface}/g /usr/bin/bettercap-launcher".format(
                    interface=interface
                ),
                shell=True,
            ).stdout
            subprocess.run(
                "sed -i s/wlan0mon/{interface}/g /usr/local/share/bettercap/caplets/pwnagotchi-auto.cap".format(
                    interface=interface
                ),
                shell=True,
            ).stdout
            subprocess.run(
                "sed -i s/wlan0mon/{interface}/g /usr/local/share/bettercap/caplets/pwnagotchi-manual.cap".format(
                    interface=interface
                ),
                shell=True,
            ).stdout
            subprocess.run(
                "sed -i s/wlan0mon/{interface}/g /etc/pwnagotchi/config.toml".format(
                    interface=interface
                ),
                shell=True,
            ).stdout
            subprocess.run(
                "sed -i s/wlan0mon/{interface}/g /usr/bin/pwnlib".format(
                    interface=interface
                ),
                shell=True,
            ).stdout
            _log("External adapter activated")
        else:
            subprocess.run(
                "sed -i s/{interface}/wlan0mon/g /usr/bin/bettercap-launcher".format(
                    interface=interface
                ),
                shell=True,
            ).stdout
            subprocess.run(
                "sed -i s/{interface}/wlan0mon/g /usr/local/share/bettercap/caplets/pwnagotchi-auto.cap".format(
                    interface=interface
                ),
                shell=True,
            ).stdout
            subprocess.run(
                "sed -i s/{interface}/wlan0mon/g /usr/local/share/bettercap/caplets/pwnagotchi-manual.cap".format(
                    interface=interface
                ),
                shell=True,
            ).stdout
            subprocess.run(
                "sed -i s/{interface}/wlan0mon/g /etc/pwnagotchi/config.toml".format(
                    interface=interface
                ),
                shell=True,
            ).stdout
            subprocess.run(
                "sed -i s/{interface}/wlan0mon/g /usr/bin/pwnlib".format(
                    interface=interface
                ),
                shell=True,
            ).stdout
            _log("Internal adapter activated")

    def on_unload(self, ui):
        with ui._lock:
            logging.info(f"[{self.__class__.__name__}] plugin unloaded")

    def on_webhook(self, path, request):
        logging.info(f"[{self.__class__.__name__}] webhook pressed")
        pass


def _run(cmd):
    result = subprocess.run(
        cmd,
        shell=True,
        stdin=None,
        stderr=None,
        stdout=subprocess.PIPE,
        executable="/bin/bash",
    )
    return result.stdout.decode("utf-8").strip()


def _log(message):
    logging.info(f"[{self.__class__.__name__}] %s" % message)
