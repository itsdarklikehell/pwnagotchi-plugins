import os
import logging

import pwnagotchi
import pwnagotchi.plugins as plugins


class handshaker(plugins.Plugin):
    __author__ = "SgtStroopwafel, Allordacia"
    __version__ = "1.0.1"
    __license__ = "MIT"
    __description__ = "A plugin to help access important pwnagotchi information when the device cannot be accessed via SSH."
    __name__ = "handshaker"
    __help__ = "A plugin to help access important pwnagotchi information when the device cannot be accessed via SSH."
    __dependencies__ = {
        "apt": ["none"],
        "pip": ["scapy"],
    }
    __defaults__ = {
        "enabled": False,
    }

    def __init__(self):
        self.handshakes = 0
        self.ready = False
        logging.info(f"[{self.__class__.__name__}] plugin init")
        self.title = ""

    def on_loaded(self):
        data_path = "/root/handshakes"
        self.load_data(data_path)
        logging.info(f"[{self.__class__.__name__}] plugin loaded")
        logging.info(
            f"[{self.__class__.__name__}] Loaded %d handshakes", self.handshakes
        )

    def on_ready(self, agent):
        logging.info(f"[{self.__class__.__name__}] plugin ready")
        # sync the data_path to the /boot/handshakes folder
        os.system("rsync -a --delete /root/handshakes/ /boot/handshakes/")
        logging.info(
            f"[{self.__class__.__name__}] Synced %d handshakes", self.handshakes
        )

        # copy /var/log/pwnagotchi.log to /boot/pwnagotchi-start.log
        os.system("cp /var/log/pwnagotchi.log /boot/pwnagotchi-start.log")
        logging.info(
            f"[{self.__class__.__name__}] Copied pwnagotchi.log to pwnagotchi-start.log"
        )

        # check if the /boot/custom_plugins folder exists. If it does, mv its contents to /home/pi/custom_plugins then delete the folder
        if os.path.exists("/boot/custom_plugins"):
            os.system("mv /boot/custom_plugins/* /home/pi/custom_plugins/")
            os.system("rm -rf /boot/custom_plugins")
            logging.info(
                f"[{self.__class__.__name__}] Moved custom_plugins to /home/pi/custom_plugins"
            )
            # Copy /etc/pwnagotchi/config.toml to /boot/config.toml
            os.system("cp /etc/pwnagotchi/config.toml /boot/config.toml")
            logging.info(
                f"[{self.__class__.__name__}] Copied config.toml to /boot/config.toml"
            )

    def on_unload(self, agent):
        logging.info(f"[{self.__class__.__name__}] plugin unloaded")
        os.system("cp /var/log/pwnagotchi.log /boot/pwnagotchi-end.log")
        logging.info(
            f"[{self.__class__.__name__}] Copied pwnagotchi.log to pwnagotchi-end.log"
        )

    def on_webhook(self, path, request):
        logging.info(f"[{self.__class__.__name__}] webhook pressed")
        pass
