"""
Special thanks to Dal/FikolmijReturns
for his network-fix service.

The plugin set a service with the right
Region to unlock the channel 12 and 13
Used outside the US.

The plugin create these two files to run the service:
/etc/systemd/system/network-fix.service
/root/network-fix.sh

Steps list to use the plugin:
-----------------------------
-Set the /etc/pwnagotchi/config.toml with:
```
main.plugins.fix_region.enabled = true
main.plugins.fix_region.region = "NL"
```
-Go to the plugin page to enable the Fix_Region plugin.
-The pwnagotchi will restart itself.
-Now,the change is apply

To change for another region you need to:
-----------------------------------------
-Go to the plugin page to disable the Fix_Region plugin.
-Go to inside the Webcfg to change the region, save and restart.
--OR
--Change the region inside the config.toml file, and restart the pwnagotchi (service pwnagotchi restart)
-Go to the plugin page to enable the Fix_Region plugin.
-The pwnagotchi will restart itself.
-Now,the change is apply

-You can verify if it's working with this commands:
```
iw reg get
iwlist wlan0 channel
```
"""

import os
import pwnagotchi
from pwnagotchi import restart
import pwnagotchi.plugins as plugins
import logging
import _thread

NETFIX_SERV = """
[Unit]
Description=Custom iw Domain Set Script
After=default.target

[Service]
ExecStart=/root/network-fix.sh &

[Install]
WantedBy=default.target
"""
REGION = pwnagotchi.config["main"]["plugins"]["fix_region"]["region"]

NETFIX_SH = """
#!/bin/bash
iw reg set """

SERV_PATH = "/etc/systemd/system/network-fix.service"
SH_PATH = "/root/network-fix.sh"


class fix_region(plugins.Plugin):
    __author__ = "SgtStroopwafel, @V0rT3x https://github.com/V0r-T3x"
    __version__ = "1.0"
    __license__ = "GPL3"
    __description__ = "Let you change the iw region to unlock channel."
    __name__ = "Fix_Region"
    __help__ = "Let you change the iw region to unlock channel."
    __dependencies__ = {
        "apt": ["none"],
        "pip": ["scapy"],
    }
    __defaults__ = {
        "enabled": False,
    }

    def __init__(self):
        self.ready = False
        self.mode = "MANU"
        logging.info(f"[{self.__class__.__name__}] Region: " + REGION)

    def on_loaded(self):
        logging.info(f"[{self.__class__.__name__}] plugin loaded")

        if not os.path.exists(SH_PATH):
            file = open(SH_PATH, "w")
            file.write(NETFIX_SH + REGION)
            file.close()
            os.system("chmod +x " + SH_PATH)
        if not os.path.exists(SERV_PATH):
            file = open(SERV_PATH, "w")
            file.write(NETFIX_SERV)
            file.close()
            os.system("sudo iw reg set " + REGION)
            os.system("sudo systemctl enable network-fix")
            os.system("sudo systemctl start network-fix")
            try:
                _thread.start_new_thread(restart, (self.mode,))
            except Exception as ex:
                logging.error(ex)
                return "config error", 500

    def on_unload(self, ui):
        logging.info(f"[{self.__class__.__name__}] plugin unloaded")

        os.system("rm " + SERV_PATH)
        os.system("rm " + SH_PATH)
        os.system("sudo systemctl stop network-fix")
        os.system("sudo systemctl disable network-fix")

    def on_webhook(self, path, request):
        logging.info(f"[{self.__class__.__name__}] webhook pressed")
        pass
