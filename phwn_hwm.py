import pwnagotchi.plugins as plugins
import pwnagotchi
import logging
import subprocess
import time
import os


class PhwnHwm(plugins.Plugin):
    __author__ = "@necrosato"
    __version__ = "1.0.0"
    __license__ = "GPL3"
    __description__ = "Define hwms for your pwnagotchi"

    def __init__(self):
        self.status = ""
        self.networks = {}

    def on_loaded(self):
        logging.info(f"[{self.__class__.__name__}] plugin loaded")
        for opt in ["networks", "minimum_rssi"]:
            if opt not in self.options or (
                opt in self.options and self.options[opt] is None
            ):
                logging.error(f"[phwn_hwm] Option {opt} is not set.")
                return
        self.networks = {
            self.options["networks"][i]: self.options["networks"][i + 1]
            for i in range(0, len(self.options["networks"]), 2)
        }
        self.log("plugin loaded - networks: {}".format(str(self.networks)))
        if os.path.isfile("/root/.dwnt_phwn_hwm"):
            os.remove("/root/.dwnt_phwn_hwm")
            self.status = "dwnt_phwn_hwm"
            self.log("disabling phwn_hwm until next reboot")

    def on_unfiltered_ap_list(self, agent, access_points):
        for network in access_points:
            if network["hostname"] in self.networks:
                self.log(
                    "FOUND %s nearby on channel %d (rssi: %d)"
                    % (network["hostname"], network["channel"], network["rssi"])
                )
                if self.status == "phwned_hwm":
                    return
                if (
                    network["rssi"] >= self.options["minimum_rssi"]
                    and self.status != "dwnt_phwn_hwm"
                ):
                    return self.connect_to_target_network(
                        agent,
                        network["hostname"],
                        self.networks[network["hostname"]],
                        network["channel"],
                    )
                else:
                    self.log(
                        "The signal strength is too low (%d) to connect."
                        % (network["rssi"])
                    )
        self.reboot_if_disconnected()

    def on_ui_update(self, ui):
        if self.status == "hwm_found":
            ui.set("face", "(◕‿‿◕)")
            ui.set("face", "(ᵔ◡◡ᵔ)")
            ui.set("status", "Hwm Found" + self.status_str())
        elif self.status == "phwning_hwm":
            ui.set("face", "(◕‿◕ )")
            ui.set("face", "( ◕‿◕)")
            ui.set("status", "Phwning Hwm" + self.status_str())
        elif self.status == "phwned_hwm":
            ui.set("face", "(ᵔ◡◡ᵔ)")
            ui.set("status", "Phwned Home!" + self.status_str())
        self.reboot_if_disconnected()

    def status_str(self):
        return "\n{} {} {}".format(
            self.associated_network(), self.wlan_ip(), self.status
        )

    def connect_to_target_network(self, agent, ssid, password, channel):
        self.log("phwning hwm")
        self.status = "hwm_found"
        agent.run("wifi.recon off")
        subprocess.run(
            "systemctl stop wpa_supplicant; killall wpa_supplicant",
            shell=True,
            stdin=None,
            stdout=open("/dev/null", "w"),
            stderr=None,
            executable="/bin/bash",
        )
        subprocess.run(
            "modprobe --remove brcmfmac; modprobe brcmfmac",
            shell=True,
            stdin=None,
            stdout=open("/dev/null", "w"),
            stderr=None,
            executable="/bin/bash",
        )
        subprocess.run(
            "modprobe --remove brcmfmac; modprobe brcmfmac",
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
        subprocess.run(
            "ifconfig wlan0 up",
            shell=True,
            stdin=None,
            stdout=open("/dev/null", "w"),
            stderr=None,
            executable="/bin/bash",
        )
        time.sleep(3)
        self.status = "phwning_hwm"
        subprocess.run(
            "iwconfig wlan0 channel %d" % channel,
            shell=True,
            stdin=None,
            stdout=open("/dev/null", "w"),
            stderr=None,
            executable="/bin/bash",
        )
        with open("/tmp/wpa_supplicant.conf", "w") as wpa_supplicant_conf:
            wpa_supplicant_conf.write(
                'ctrl_interface=DIR=/var/run/wpa_supplicant\nupdate_config=1\ncountry=GB\n\nnetwork={\n\tssid="%s"\n\tpsk="%s"\n}\n'
                % (ssid, password)
            )
        subprocess.run(
            "wpa_supplicant -u -s -c /tmp/wpa_supplicant.conf -i wlan0 &",
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
        subprocess.run(
            "dhclient wlan0",
            shell=True,
            stdin=None,
            stdout=open("/dev/null", "w"),
            stderr=None,
            executable="/bin/bash",
        )
        time.sleep(3)
        self.status = "phwned_hwm"
        self.log("finished connecting to home wifi, ip address %s" % self.wlan_ip())

    def reboot_if_disconnected(self):
        if self.status == "phwned_hwm":
            if self.wlan_ip() == "" or self.associated_network() == "":
                self.log("rebooting to enable monitor mode")
                pwnagotchi.reboot()

    def run(self, cmd):
        result = subprocess.run(
            cmd,
            shell=True,
            stdin=None,
            stderr=None,
            stdout=subprocess.PIPE,
            executable="/bin/bash",
        )
        return result.stdout.decode("utf-8").strip()

    def associated_network(self):
        return self.run("iwconfig wlan0 | awk -F\\\" '{print $2}'")

    def wlan_ip(self):
        return self.run("ip addr show wlan0 | grep 'inet ' | awk '{print $2}'")

    def log(self, message):
        logging.info("[phwn_hwm] %s" % message)
