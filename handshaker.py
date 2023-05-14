import os
import logging

import pwnagotchi
import pwnagotchi.plugins as plugins


class handshaker(plugins.Plugin):
    __author__ = 'Allordacia'
    __version__ = '1.0.1'
    __license__ = 'MIT'
    __description__ = 'A plugin to help access important pwnagotchi information when the device cannot be accessed via SSH'

    def __init__(self):
        self.handshakes = 0
        logging.info("[handshaker]: Initialized")

    def on_loaded(self):
        data_path = '/root/handshakes'
        self.load_data(data_path)
        logging.info("[handshaker]: Loaded %d handshakes", self.handshakes)

    def on_ready(self, agent):
        logging.info("[handshaker]: Ready")
        # sync the data_path to the /boot/handshakes folder
        os.system("rsync -a --delete /root/handshakes/ /boot/handshakes/")
        logging.info("[handshaker]: Synced %d handshakes", self.handshakes)

        # copy /var/log/pwnagotchi.log to /boot/pwnagotchi-start.log
        os.system("cp /var/log/pwnagotchi.log /boot/pwnagotchi-start.log")
        logging.info("[handshaker]: Copied pwnagotchi.log to pwnagotchi-start.log")

        # check if the /boot/custom_plugins folder exists. If it does, mv its contents to /home/pi/custom_plugins then delete the folder
        if os.path.exists("/boot/custom_plugins"):
            os.system("mv /boot/custom_plugins/* /home/pi/custom_plugins/")
            os.system("rm -rf /boot/custom_plugins")
            logging.info("[handshaker]: Moved custom_plugins to /home/pi/custom_plugins")
            # Copy /etc/pwnagotchi/config.toml to /boot/config.toml
            os.system("cp /etc/pwnagotchi/config.toml /boot/config.toml")
            logging.info("[handshaker]: Copied config.toml to /boot/config.toml")

    def on_unload(self, agent):
        logging.info("[handshaker]: Unloaded")
        os.system("cp /var/log/pwnagotchi.log /boot/pwnagotchi-end.log")
        logging.info("[handshaker]: Copied pwnagotchi.log to pwnagotchi-end.log")
