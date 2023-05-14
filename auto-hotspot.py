from pwnagotchi.ui.components import LabeledValue
from pwnagotchi.ui.view import BLACK
import pwnagotchi.ui.fonts as fonts
import pwnagotchi.plugins as plugins
import pwnagotchi
import logging
import os
import subprocess
import requests
import time
from pwnagotchi.ai.reward import RewardFunction


READY = 0
STATUS = ""
NETWORK = ""


class AutoHotSpot(plugins.Plugin):
    __author__ = "@tjbishop"
    __version__ = "1.0.0"
    __license__ = "GPL3"
    __description__ = (
        "A plugin to automatically create a wifi hotspot when in manual mode"
    )

    def on_loaded(self):
        global READY
        logging.info("Auto Hotspot loaded")
        READY = 1

    def display_text(self, text):
        global STATUS
        STATUS = text

    def on_ui_update(self, ui):
        global STATUS
        while STATUS == "rssi_low":
            ui.set("face", "(ﺏ__ﺏ)")
            ui.set(
                "status",
                "Signal strength of %s is currently too low to connect ..." % NETWORK,
            )
        while STATUS == "home_detected":
            ui.set("face", "(◕‿‿◕)")
            ui.set("face", "(ᵔ◡◡ᵔ)")
            ui.set("status", "Found home network at %s ..." % NETWORK)
        while STATUS == "switching_mon_off":
            ui.set("face", "(◕‿‿◕)")
            ui.set("face", "(ᵔ◡◡ᵔ)")
            ui.set("status", "We're home! Pausing monitor mode ...")
        while STATUS == "scrambling_mac":
            ui.set("face", "(⌐■_■)")
            ui.set(
                "status", "Scrambling MAC address before connecting to %s ..." % NETWORK
            )
        while STATUS == "associating":
            ui.set("status", "Greeting the AP and asking for an IP via DHCP ...")
            ui.set("face", "(◕‿◕ )")
            ui.set("face", "( ◕‿◕)")
        if STATUS == "associated":
            ui.set("face", "(ᵔ◡◡ᵔ)")
            ui.set("status", "Home at last!")

    def _connect_to_target_network(self, network_name, channel):
        global READY
        global STATUS
        global NETWORK
        NETWORK = network_name
        logging.info("sending command to Bettercap to stop using mon0...")
        STATUS = "switching_mon_off"
        requests.post(
            "http://127.0.0.1:8081/api/session",
            data='{"cmd":"wifi.recon off"}',
            auth=("pwnagotchi", "pwnagotchi"),
        )
        logging.info("ensuring all wpa_supplicant processes are terminated...")
        subprocess.Popen(
            "systemctl stop wpa_supplicant; killall wpa_supplicant",
            shell=True,
            stdin=None,
            stdout=open("/dev/null", "w"),
            stderr=None,
            executable="/bin/bash",
        )
        time.sleep(10)
        logging.info("disabling monitor mode...")
        subprocess.Popen(
            "modprobe --remove brcmfmac; modprobe brcmfmac",
            shell=True,
            stdin=None,
            stdout=open("/dev/null", "w"),
            stderr=None,
            executable="/bin/bash",
        )
        time.sleep(10)
        # Runs this driver reload command again because sometimes it gets stuck the first time:
        subprocess.Popen(
            "modprobe --remove brcmfmac; modprobe brcmfmac",
            shell=True,
            stdin=None,
            stdout=open("/dev/null", "w"),
            stderr=None,
            executable="/bin/bash",
        )
        time.sleep(10)
        logging.info("randomizing wlan0 MAC address prior to connecting...")
        STATUS = "scrambling_mac"
        subprocess.Popen(
            "macchanger -A wlan0",
            shell=True,
            stdin=None,
            stdout=open("/dev/null", "w"),
            stderr=None,
            executable="/bin/bash",
        )
        time.sleep(10)
        logging.info(
            "setting hostname to a ^work dictionary word prior to connecting (for added stealth since their DHCP server will see this name)..."
        )
        subprocess.Popen(
            'hostnamectl set-hostname $(grep "^work" /usr/share/dict/words | grep -v "s$" | sort -u | shuf -n 1))',
            shell=True,
            stdin=None,
            stdout=open("/dev/null", "w"),
            stderr=None,
            executable="/bin/bash",
        )
        time.sleep(5)
        logging.info("starting up wlan0 again...")
        subprocess.Popen(
            "ifconfig wlan0 up",
            shell=True,
            stdin=None,
            stdout=open("/dev/null", "w"),
            stderr=None,
            executable="/bin/bash",
        )
        time.sleep(3)
        # This command runs multiple times because it sometimes doesn't work the first time:
        subprocess.Popen(
            "ifconfig wlan0 up",
            shell=True,
            stdin=None,
            stdout=open("/dev/null", "w"),
            stderr=None,
            executable="/bin/bash",
        )
        time.sleep(10)
        logging.info("setting wlan0 channel to match the target...")
        STATUS = "associating"
        subprocess.Popen(
            "iwconfig wlan0 channel %d" % channel,
            shell=True,
            stdin=None,
            stdout=open("/dev/null", "w"),
            stderr=None,
            executable="/bin/bash",
        )
        subprocess.Popen(
            "ifconfig wlan0 up",
            shell=True,
            stdin=None,
            stdout=open("/dev/null", "w"),
            stderr=None,
            executable="/bin/bash",
        )
        time.sleep(10)
        logging.info("writing to wpa_supplicant.conf file...")
        with open("/tmp/wpa_supplicant.conf", "w") as wpa_supplicant_conf:
            wpa_supplicant_conf.write(
                'ctrl_interface=DIR=/var/run/wpa_supplicant\nupdate_config=1\ncountry=GB\n\nnetwork={\n\tssid="%s"\n\tpsk="%s"\n}\n'
                % (network_name, self.options["home-password"])
            )
        logging.info("starting wpa_supplicant background process...")
        subprocess.Popen(
            "ifconfig wlan0 up",
            shell=True,
            stdin=None,
            stdout=open("/dev/null", "w"),
            stderr=None,
            executable="/bin/bash",
        )
        subprocess.Popen(
            "wpa_supplicant -u -s -c /tmp/wpa_supplicant.conf -i wlan0 &",
            shell=True,
            stdin=None,
            stdout=open("/dev/null", "w"),
            stderr=None,
            executable="/bin/bash",
        )
        time.sleep(10)
        logging.info("connecting to wifi...")
        subprocess.Popen(
            "ifconfig wlan0 up",
            shell=True,
            stdin=None,
            stdout=open("/dev/null", "w"),
            stderr=None,
            executable="/bin/bash",
        )
        subprocess.Popen(
            "wpa_cli -i wlan0 reconfigure",
            shell=True,
            stdin=None,
            stdout=open("/dev/null", "w"),
            stderr=None,
            executable="/bin/bash",
        )
        time.sleep(10)
        logging.info("trying to get an IP address on the network via DHCP...")
        subprocess.Popen(
            "dhclient wlan0",
            shell=True,
            stdin=None,
            stdout=open("/dev/null", "w"),
            stderr=None,
            executable="/bin/bash",
        )
        time.sleep(10)
        STATUS = "associated"
        READY = 1

    def _restart_monitor_mode(self):
        logging.info("resuming wifi recon and monitor mode...")
        logging.info("stopping wpa_supplicant...")
        subprocess.Popen(
            "systemctl stop wpa_supplicant; killall wpa_supplicant",
            shell=True,
            stdin=None,
            stdout=open("/dev/null", "w"),
            stderr=None,
            executable="/bin/bash",
        )
        time.sleep(10)
        logging.info("reloading brcmfmac driver...")
        subprocess.Popen(
            "modprobe --remove brcmfmac && modprobe brcmfmac",
            shell=True,
            stdin=None,
            stdout=open("/dev/null", "w"),
            stderr=None,
            executable="/bin/bash",
        )
        time.sleep(10)
        logging.info("randomizing MAC address of wlan0...")
        subprocess.Popen(
            "macchanger -A wlan0",
            shell=True,
            stdin=None,
            stdout=open("/dev/null", "w"),
            stderr=None,
            executable="/bin/bash",
        )
        time.sleep(10)
        subprocess.Popen(
            "ifconfig wlan0 up",
            shell=True,
            stdin=None,
            stdout=open("/dev/null", "w"),
            stderr=None,
            executable="/bin/bash",
        )
        logging.info("starting monitor mode...")
        subprocess.Popen(
            'iw phy "$(iw phy | head -1 | cut -d" " -f2)" interface add mon0 type monitor && ifconfig mon0 up',
            shell=True,
            stdin=None,
            stdout=open("/dev/null", "w"),
            stderr=None,
            executable="/bin/bash",
        )
        logging.info("telling Bettercap to resume wifi recon...")
        requests.post(
            "http://127.0.0.1:8081/api/session",
            data='{"cmd":"wifi.recon on"}',
            auth=("pwnagotchi", "pwnagotchi"),
        )

    def on_epoch(self, ui):
        # If not connected to a wireless network and mon0 doesn't exist, run _restart_monitor_mode function
        if (
            "Not-Associated" in subprocess.Popen("iwconfig wlan0").read()
            and "Monitor" not in subprocess.Popen("iwconfig mon0").read()
        ):
            self._restart_monitor_mode()

    def on_wifi_update(self, agent, access_points):
        global READY
        global STATUS
        home_network = self.options["home-network"]
        if READY == 1 and "Not-Associated" in os.popen("iwconfig wlan0").read():
            for network in access_points:
                if network["hostname"] == home_network:
                    signal_strength = network["rssi"]
                    channel = network["channel"]
                    logging.info(
                        "FOUND home network nearby on channel %d (rssi: %d)"
                        % (channel, signal_strength)
                    )
                    if signal_strength >= self.options["minimum-signal-strength"]:
                        logging.info("Starting association...")
                        READY = 0
                        self._connect_to_target_network(network["hostname"], channel)
                    else:
                        logging.info(
                            "The signal strength is too low (%d) to connect."
                            % (signal_strength)
                        )
                        STATUS = "rssi_low"
