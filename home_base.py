# home-base watches for a pre-defined home network to be in range, then pauses pwning to
# allow for internet connectivity tasks to be carried out. Once out of range, pwning is resumed
# Inspiration and some methodologies taken from @nagy_craig's "Educational-purposes-only" plugin
# Install dependencies: apt update; apt install nmap macchanger
"""
main.plugins.home_base.enabled = true
main.plugins.home_base.ssid = "home-networkname"
main.plugins.home_base.minimum_signal_strength= -75
"""


import pwnagotchi.plugins as plugins
import pwnagotchi
import logging
import subprocess
import time


class HomeBase(plugins.Plugin):
    __GitHub__ = ""
    __author__ = "(edited by: itsdarklikehell bauke.molenaar@gmail.com), @troystauffer"
    __version__ = "1.0.0"
    __license__ = "GPL3"
    __description__ = "Connects to home network for internet when available"
    __name__ = "HomeBase"
    __help__ = "Connects to home network for internet when available"
    __dependencies__ = {
        "apt": ["none"],
        "pip": ["scapy"],
    }
    __defaults__ = {
        "enabled": False,
        "ssid": "home-networkname",
        "minimum_signal_strength": -75,
    }

    def __init__(self):
        self.ready = False
        logging.debug(f"[{self.__class__.__name__}] plugin init")
        self.title = ""
        self.ready = 0
        self.status = ""
        self.network = ""

    def on_loaded(self):
        for opt in ["ssid", "password", "minimum_signal_strength"]:
            if opt not in self.options or (
                opt in self.options and self.options[opt] is None
            ):
                logging.error(f"[home_base] Option {opt} is not set.")
                return
        _log("plugin loaded")
        logging.info(f"[{self.__class__.__name__}] plugin loaded")
        self.ready = 1

    def on_unfiltered_ap_list(self, agent, access_points):
        home_network = self.options["ssid"]
        result = _run("iwconfig wlan0")
        if self.ready == 1 and "Not-Associated" in result:
            for network in access_points:
                if network["hostname"] == home_network:
                    signal_strength = network["rssi"]
                    channel = network["channel"]
                    _log(
                        "FOUND home network nearby on channel %d (rssi: %d)"
                        % (channel, signal_strength)
                    )
                    if signal_strength >= self.options["minimum_signal_strength"]:
                        _log("Starting association...")
                        self.ready = 0
                        _connect_to_target_network(
                            self, agent, network["hostname"], channel
                        )
                    else:
                        _log(
                            "The signal strength is too low (%d) to connect."
                            % (signal_strength)
                        )
                        self.status = "rssi_low"

    def on_ui_update(self, ui):
        while self.status == "rssi_low":
            ui.set("face", "(ﺏ__ﺏ)")
            ui.set(
                "status",
                "Signal strength of %s is currently too low to connect ..."
                % self.network,
            )
        while self.status == "home_detected":
            ui.set("face", "(◕‿‿◕)")
            ui.set("face", "(ᵔ◡◡ᵔ)")
            ui.set("status", "Found home network at %s ..." % self.network)
        while self.status == "switching_mon_off":
            ui.set("face", "(◕‿‿◕)")
            ui.set("face", "(ᵔ◡◡ᵔ)")
            ui.set("status", "We're home! Pausing monitor mode ...")
        while self.status == "scrambling_mac":
            ui.set("face", "(⌐■_■)")
            ui.set(
                "status",
                "Scrambling MAC address before connecting to %s ..." % self.network,
            )
        while self.status == "associating":
            ui.set("status", "Greeting the AP and asking for an IP via DHCP ...")
            ui.set("face", "(◕‿◕ )")
            ui.set("face", "( ◕‿◕)")
        if self.status == "associated":
            ui.set("face", "(ᵔ◡◡ᵔ)")
            ui.set("status", "Home at last!")

    def on_epoch(self, agent, epoch, epoch_data):
        if "Not-Associated" in _run("iwconfig wlan0") and "Monitor" not in _run(
            "iwconfig wlan0mon"
        ):
            _restart_monitor_mode(self, agent)

    def on_unload(self, ui):
        with ui._lock:
            logging.info(f"[{self.__class__.__name__}] plugin unloaded")


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


def _connect_to_target_network(self, agent, network_name, channel):
    self.network = network_name
    _log("sending command to Bettercap to stop using wlan0mon...")
    self.status = "switching_mon_off"
    agent.run("wifi.recon off")
    _log("ensuring all wpa_supplicant processes are terminated...")
    subprocess.run(
        "systemctl stop wpa_supplicant; killall wpa_supplicant",
        shell=True,
        stdin=None,
        stdout=open("/dev/null", "w"),
        stderr=None,
        executable="/bin/bash",
    )
    time.sleep(5)
    _log("disabling monitor mode...")
    subprocess.run(
        "modprobe --remove brcmfmac; modprobe brcmfmac",
        shell=True,
        stdin=None,
        stdout=open("/dev/null", "w"),
        stderr=None,
        executable="/bin/bash",
    )
    time.sleep(5)
    # Runs this driver reload command again because sometimes it gets stuck the first time:
    subprocess.run(
        "modprobe --remove brcmfmac; modprobe brcmfmac",
        shell=True,
        stdin=None,
        stdout=open("/dev/null", "w"),
        stderr=None,
        executable="/bin/bash",
    )
    time.sleep(5)
    _log("randomizing wlan0 MAC address prior to connecting...")
    self.status = "scrambling_mac"
    subprocess.run(
        "macchanger -A wlan0",
        shell=True,
        stdin=None,
        stdout=open("/dev/null", "w"),
        stderr=None,
        executable="/bin/bash",
    )
    time.sleep(5)
    _log("starting up wlan0 again...")
    subprocess.run(
        "ifconfig wlan0 up",
        shell=True,
        stdin=None,
        stdout=open("/dev/null", "w"),
        stderr=None,
        executable="/bin/bash",
    )
    time.sleep(3)
    # This command runs multiple times because it sometimes doesn't work the first time:
    subprocess.run(
        "ifconfig wlan0 up",
        shell=True,
        stdin=None,
        stdout=open("/dev/null", "w"),
        stderr=None,
        executable="/bin/bash",
    )
    time.sleep(5)
    _log("setting wlan0 channel to match the target...")
    self.status = "associating"
    subprocess.run(
        "iwconfig wlan0 channel %d" % channel,
        shell=True,
        stdin=None,
        stdout=open("/dev/null", "w"),
        stderr=None,
        executable="/bin/bash",
    )
    subprocess.run(
        "ifconfig wlan0 up",
        shell=True,
        stdin=None,
        stdout=open("/dev/null", "w"),
        stderr=None,
        executable="/bin/bash",
    )
    time.sleep(5)
    _log("writing to wpa_supplicant.conf file...")
    with open("/tmp/wpa_supplicant.conf", "w") as wpa_supplicant_conf:
        wpa_supplicant_conf.write(
            'ctrl_interface=DIR=/var/run/wpa_supplicant\nupdate_config=1\ncountry=GB\n\nnetwork={\n\tssid="%s"\n\tpsk="%s"\n}\n'
            % (network_name, self.options["password"])
        )
    _log("starting wpa_supplicant background process...")
    subprocess.run(
        "ifconfig wlan0 up",
        shell=True,
        stdin=None,
        stdout=open("/dev/null", "w"),
        stderr=None,
        executable="/bin/bash",
    )
    subprocess.run(
        "wpa_supplicant -u -s -c /tmp/wpa_supplicant.conf -i wlan0 &",
        shell=True,
        stdin=None,
        stdout=open("/dev/null", "w"),
        stderr=None,
        executable="/bin/bash",
    )
    time.sleep(5)
    _log("connecting to wifi...")
    subprocess.run(
        "ifconfig wlan0 up",
        shell=True,
        stdin=None,
        stdout=open("/dev/null", "w"),
        stderr=None,
        executable="/bin/bash",
    )
    subprocess.run(
        "wpa_cli -i wlan0 reconfigure",
        shell=True,
        stdin=None,
        stdout=open("/dev/null", "w"),
        stderr=None,
        executable="/bin/bash",
    )
    time.sleep(5)
    _log("trying to get an IP address on the network via DHCP...")
    subprocess.run(
        "dhclient wlan0",
        shell=True,
        stdin=None,
        stdout=open("/dev/null", "w"),
        stderr=None,
        executable="/bin/bash",
    )
    time.sleep(5)
    self.status = "associated"
    self.ready = 1
    _log("finished connecting to home wifi")


def _restart_monitor_mode(self, agent):
    _log("resuming wifi recon and monitor mode...")
    _log("stopping wpa_supplicant...")
    subprocess.run(
        "systemctl stop wpa_supplicant; killall wpa_supplicant",
        shell=True,
        stdin=None,
        stdout=open("/dev/null", "w"),
        stderr=None,
        executable="/bin/bash",
    )
    time.sleep(5)
    _log("reloading brcmfmac driver...")
    subprocess.run(
        "modprobe --remove brcmfmac && modprobe brcmfmac",
        shell=True,
        stdin=None,
        stdout=open("/dev/null", "w"),
        stderr=None,
        executable="/bin/bash",
    )
    time.sleep(5)
    _log("randomizing MAC address of wlan0...")
    subprocess.run(
        "macchanger -A wlan0",
        shell=True,
        stdin=None,
        stdout=open("/dev/null", "w"),
        stderr=None,
        executable="/bin/bash",
    )
    time.sleep(5)
    subprocess.run(
        "ifconfig wlan0 up",
        shell=True,
        stdin=None,
        stdout=open("/dev/null", "w"),
        stderr=None,
        executable="/bin/bash",
    )
    _log("starting monitor mode...")
    subprocess.run(
        'iw phy "$(iw phy | head -1 | cut -d" " -f2)" interface add wlan0mon type monitor && ifconfig wlan0mon up',
        shell=True,
        stdin=None,
        stdout=open("/dev/null", "w"),
        stderr=None,
        executable="/bin/bash",
    )
    _log("telling Bettercap to resume wifi recon...")
    agent.run("wifi.recon on")
    agent.next_epoch(self)


def _log(message):
    logging.info(f"[{self.__class__.__name__}] %s" % message)

    def on_webhook(self, path, request):
        logging.info(f"[{self.__class__.__name__}] webhook pressed")
