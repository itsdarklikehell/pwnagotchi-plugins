import pwnagotchi.plugins as plugins
import pwnagotchi
import logging
import subprocess
import time
import re
from operator import methodcaller

class AwayBase(plugins.Plugin):
    __author__ = '@nope'
    __version__ = '1.0.0'
    __license__ = 'GPL3'
    __description__ = 'watches for known networks, connects for a while, then returns to recon.'
    __name__ = 'AwayBase'
    __help__ = """
    watches for known networks, connects for a while, then returns to recon
    """
    __dependencies__ = {
        'apt': ['aircrack-ng'],
    }
    __defaults__ = {
        'enabled': False,
        'face': '(>.<)',
    }

    def __init__(self):
        self.ready = 0
        self.status = ''
        self.network = ''
        self.used_networks = {}

    def on_loaded(self):
        for opt in ['disconnect_after_cycles', 'minimum_signal_strength']:
            if opt not in self.options or (opt in self.options and self.options[opt] is None):
                logging.error(f"[away_base] Option {opt} is not set.")
                return
        _log("plugin loaded")
        self.ready = 1

    def on_wifi_update(self, agent, access_points):
        result = _run('iwconfig wlan0')
        if self.ready == 1 and "Not-Associated" in result:
            potfile = _run('cat /root/handshakes/wpa-sec.founds.potfile | awk -F: \'{print $3 ":" $4}\'').splitlines()
            pwned_networks = {}
            for line in potfile:
                network = line.split(":")
                pwned_networks[network[0]] = network[1]
            for network in access_points:
                if network['hostname'] in pwned_networks and network['hostname'] not in self.used_networks:
                    signal_strength = network['rssi']
                    channel = network['channel']
                    _log("FOUND cracked network nearby on channel %d (rssi: %d)" % (channel, signal_strength))
                    if signal_strength >= self.options['minimum_signal_strength']:
                        password = pwned_networks[network['hostname']]
                        _log("Starting association...")
                        self.ready = 0
                        _connect_to_target_network(self, agent, network['hostname'], channel, password)
                    else:
                        _log("The signal strength is too low (%d) to connect." % (signal_strength))
                        self.status = 'rssi_low'

    def on_ui_update(self, ui):
        while self.status == 'rssi_low':
            ui.set('face', '(ﺏ__ﺏ)')
            ui.set('status', 'Signal strength of %s is currently too low to connect ...' % self.network)
        while self.status == 'home_detected':
            ui.set('face', '(◕‿‿◕)')
            ui.set('face', '(ᵔ◡◡ᵔ)')
            ui.set('status', 'Found home network at %s ...' % self.network)
        while self.status == 'switching_mon_off':
            ui.set('face', '(◕‿‿◕)')
            ui.set('face', '(ᵔ◡◡ᵔ)')
            ui.set('status', 'We\'re home! Pausing monitor mode ...')
        while self.status == 'scrambling_mac':
            ui.set('face', '(⌐■_■)')
            ui.set('status', 'Scrambling MAC address before connecting to %s ...' % self.network)
        while self.status == 'associating':
            ui.set('status', 'Greeting the AP and asking for an IP via DHCP ...')
            ui.set('face', '(◕‿◕ )')
            ui.set('face', '( ◕‿◕)')
        if self.status == 'associated':
            ui.set('face', '(ᵔ◡◡ᵔ)')
            ui.set('status', 'Home at last!')

    def on_epoch(self, agent, epoch, epoch_data):
        wireless_status = _run('iwconfig wlan0')
        l = wireless_status.splitlines()[0]
        current_network = l[slice(l.find('"') + 1, [m.start() for m in re.finditer(r'"', l)][1])]
        if current_network in self.used_networks and self.used_networks[current_network] > self.options['disconnect_after_cycles']:
            _restart_monitor_mode(self,agent)

def _run(cmd):
    result = subprocess.run(cmd, shell=True, stdin=None, stderr=None, stdout=subprocess.PIPE, executable="/bin/bash")
    return result.stdout.decode('utf-8').strip()

def _connect_to_target_network(self, agent, network_name, channel, password):
    self.network = network_name
    _log('sending command to Bettercap to stop using mon0...')
    self.status = 'switching_mon_off'
    agent.run('wifi.recon off')
    _log('ensuring all wpa_supplicant processes are terminated...')
    subprocess.run('systemctl stop wpa_supplicant; killall wpa_supplicant', shell=True, stdin=None, stdout=open("/dev/null", "w"), stderr=None, executable="/bin/bash")
    time.sleep(5)
    _log('disabling monitor mode...')
    subprocess.run('modprobe --remove brcmfmac; modprobe brcmfmac', shell=True, stdin=None, stdout=open("/dev/null", "w"), stderr=None, executable="/bin/bash")
    time.sleep(5)
    # Runs this driver reload command again because sometimes it gets stuck the first time:
    subprocess.run('modprobe --remove brcmfmac; modprobe brcmfmac', shell=True, stdin=None, stdout=open("/dev/null", "w"), stderr=None, executable="/bin/bash")
    time.sleep(5)
    _log('randomizing wlan0 MAC address prior to connecting...')
    self.status = 'scrambling_mac'
    subprocess.run('macchanger -A wlan0', shell=True, stdin=None, stdout=open("/dev/null", "w"), stderr=None, executable="/bin/bash")
    time.sleep(5)
    _log('starting up wlan0 again...')
    subprocess.run('ifconfig wlan0 up', shell=True, stdin=None, stdout=open("/dev/null", "w"), stderr=None, executable="/bin/bash")
    time.sleep(3)
    # This command runs multiple times because it sometimes doesn't work the first time:
    subprocess.run('ifconfig wlan0 up', shell=True, stdin=None, stdout=open("/dev/null", "w"), stderr=None, executable="/bin/bash")
    time.sleep(5)
    _log('setting wlan0 channel to match the target...')
    self.status = 'associating'
    subprocess.run('iwconfig wlan0 channel %d' % channel, shell=True, stdin=None, stdout=open("/dev/null", "w"), stderr=None, executable="/bin/bash")
    subprocess.run('ifconfig wlan0 up', shell=True, stdin=None, stdout=open("/dev/null", "w"), stderr=None, executable="/bin/bash")
    time.sleep(5)
    _log('writing to wpa_supplicant.conf file...')
    with open('/tmp/wpa_supplicant.conf', 'w') as wpa_supplicant_conf:
        wpa_supplicant_conf.write("ctrl_interface=DIR=/var/run/wpa_supplicant\nupdate_config=1\ncountry=NL\n\nnetwork={\n\tssid=\"%s\"\n\tpsk=\"%s\"\n}\n" % (network_name, password))
    _log('starting wpa_supplicant background process...')
    subprocess.run('ifconfig wlan0 up', shell=True, stdin=None, stdout=open("/dev/null", "w"), stderr=None, executable="/bin/bash")
    subprocess.run('wpa_supplicant -u -s -c /tmp/wpa_supplicant.conf -i wlan0 &', shell=True, stdin=None, stdout=open("/dev/null", "w"), stderr=None, executable="/bin/bash")
    time.sleep(5)
    _log('connecting to wifi...')
    subprocess.run('ifconfig wlan0 up', shell=True, stdin=None, stdout=open("/dev/null", "w"), stderr=None, executable="/bin/bash")
    subprocess.run('wpa_cli -i wlan0 reconfigure', shell=True, stdin=None, stdout=open("/dev/null", "w"), stderr=None, executable="/bin/bash")
    time.sleep(5)
    _log('trying to get an IP address on the network via DHCP...')
    subprocess.run('dhclient wlan0', shell=True, stdin=None, stdout=open("/dev/null", "w"), stderr=None, executable="/bin/bash")
    time.sleep(5)
    self.used_networks[network_name] = 1
    self.status = 'associated'
    self.ready = 1
    _log('finished connecting to home wifi')

def _restart_monitor_mode(self,agent):
    _log('resuming wifi recon and monitor mode...')
    _log('stopping wpa_supplicant...')
    subprocess.run('systemctl stop wpa_supplicant; killall wpa_supplicant', shell=True, stdin=None, stdout=open("/dev/null", "w"), stderr=None, executable="/bin/bash")
    time.sleep(5)
    _log('reloading brcmfmac driver...')
    subprocess.run('modprobe --remove brcmfmac && modprobe brcmfmac', shell=True, stdin=None, stdout=open("/dev/null", "w"), stderr=None, executable="/bin/bash")
    time.sleep(5)
    _log('randomizing MAC address of wlan0...')
    subprocess.run('macchanger -A wlan0', shell=True, stdin=None, stdout=open("/dev/null", "w"), stderr=None, executable="/bin/bash")
    time.sleep(5)
    subprocess.run('ifconfig wlan0 up', shell=True, stdin=None, stdout=open("/dev/null", "w"), stderr=None, executable="/bin/bash")
    _log('starting monitor mode...')
    subprocess.run('iw phy "$(iw phy | head -1 | cut -d" " -f2)" interface add mon0 type monitor && ifconfig mon0 up', shell=True, stdin=None, stdout=open("/dev/null", "w"), stderr=None, executable="/bin/bash")
    _log('telling Bettercap to resume wifi recon...')
    agent.run('wifi.recon on')
    agent.next_epoch(self)

def _log(message):
    logging.info('[away_base] %s' % message)
