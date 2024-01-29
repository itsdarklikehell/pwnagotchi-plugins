import logging
import subprocess
import threading
from pwnagotchi.ui.components import LabeledValue
import pwnagotchi.ui.fonts as fonts
import time
import uuid
import os
import random
from pwnagotchi.plugins import Plugin


class CombinedPlugin(Plugin):
    __author__ = 'Andryu Schittone, @nagy_craig'
    __version__ = '1.0.27'
    __license__ = 'GPL3'
    __description__ = 'A combined Pwnagotchi plugin for setting up a honey pot and performing network authentication.'

    def __init__(self, home_network='test-net', home_password='TestNet1'):
        logging.debug("Combined plugin created")
        self.ui = None
        self.honey_pot_aps = set()
        self.detected_fake_aps = 0
        self.active_fake_aps = 0
        self.num_initial_aps = 5
        self.update_interval = 60
        self.home_network = home_network
        self.home_password = home_password
        self.log_path = "/etc/pwnagotchi/hplogs.log"

        # Verifica la existencia de la interfaz wlan0mon
        if "wlan0mon" in subprocess.getoutput('iwconfig'):
            # Initialize honey pot plugin
            threading.Timer(self.update_interval,
                            self.render_honey_pots).start()
            self.create_fake_aps()

            # Initialize educational purposes only plugin
            self.ready = 1
            self.status = ''
            self.network = ''
            threading.Timer(self.update_interval,
                            self.render_network_status).start()
        else:
            logging.warning(
                "The interface wlan0mon is not present. All functions stopped.")

    def on_loaded(self):
        # Honey pot plugin events
        self.register_event(self.handle_wifi_handshake, 'wifi-handshake')
        self.register_event(self.handle_ap_beacon, 'ap-beacon')

        # Educational purposes only plugin events
        self.register_event(self.handle_wifi_update, 'wifi-update')

    def on_unload(self, ui):
        pass

    def on_ui_setup(self, ui):
        # Common UI elements for both plugins
        ui.add_element('status', LabeledValue(color=fonts.BLACK, label='Status', value='', position=(ui.width() / 2 - 25, 30),
                                              label_font=fonts.Bold, text_font=fonts.Small))

        # UI elements specific to honey pot plugin
        ui.add_element('honey-pots', LabeledValue(color=fonts.BLACK, label='Honey Pots', value='0',
                                                  position=(
                                                      ui.width() / 2 - 25, 0),
                                                  label_font=fonts.Bold, text_font=fonts.Medium))
        ui.add_element('detected-fake-aps', LabeledValue(color=fonts.BLACK, label='Detected Fake APs', value='0',
                                                         position=(
                                                             ui.width() / 2 - 25, 10),
                                                         label_font=fonts.Bold, text_font=fonts.Medium))
        ui.add_element('active-fake-aps', LabeledValue(color=fonts.BLACK, label='Active Fake APs', value='0',
                                                       position=(
                                                           ui.width() / 2 - 25, 20),
                                                       label_font=fonts.Bold, text_font=fonts.Medium))

        # UI elements specific to educational purposes only plugin
        ui.add_element('network-status', LabeledValue(color=fonts.BLACK, label='Network Status', value='',
                                                      position=(
                                                          ui.width() / 2 - 25, 40),
                                                      label_font=fonts.Bold, text_font=fonts.Small))

    def on_ui_update(self, ui):
        some_voltage = 0.1
        some_capacity = 100.0
        ui.set('honey-pots', str(len(self.honey_pot_aps)))
        ui.set('detected-fake-aps', str(self.detected_fake_aps))
        ui.set('active-fake-aps', str(self.active_fake_aps))
        global STATUS

        if STATUS == 'rssi_low':
            ui.set('face', '(ﺏ__ﺏ)')
            ui.set(
                'status', 'Signal strength of %s is currently too low to connect ...')
        elif STATUS == 'home_detected':
            ui.set('face', '(◕‿‿◕)')
            ui.set('face', '(ᵔ◡◡ᵔ)')
            ui.set('status', 'Found home network at %s ...' %
                   self.home_network)
        elif STATUS == 'switching_mon_off':
            ui.set('face', '(◕‿‿◕)')
            ui.set('face', '(ᵔ◡◡ᵔ)')
            ui.set('status', 'We\'re home! Pausing monitor mode ...')
        elif STATUS == 'scrambling_mac':
            ui.set('face', '(⌐■_■)')
            ui.set('status', 'Scrambling MAC address before connecting to %s ...' %
                   self.home_network)
        elif STATUS == 'associating':
            ui.set('status', 'Greeting the AP and asking for an IP via DHCP ...')
            ui.set('face', '(◕‿◕ )')
            ui.set('face', '( ◕‿◕)')
        elif STATUS == 'associated':
            ui.set('face', '(ᵔ◡◡ᵔ)')
            ui.set('status', 'Home at last!')

            # Update UI elements for educational purposes only plugin
            ui.set('network-status', self.status)

    def handle_wifi_handshake(self, agent, filename, access_point, client_station):
        self.log(
            f"WiFi Handshake captured from {client_station['addr']} at {access_point['addr']}")
        logging.debug("Handling wifi handshake event...")
        # Implement additional logic if needed, such as notification or logging.

    def handle_ap_beacon(self, agent, ap):
        if ap['essid'] in self.honey_pot_aps:
            self.log(f"Fake Beacon detected: {ap['essid']} ({ap['addr']})")
            self.detected_fake_aps += 1

        if ap['essid'] in self.honey_pot_aps:
            self.active_fake_aps += 1

    def handle_wifi_update(self, agent, access_points):
        logging.debug("Handling wifi update...")
        if self.ready == 1 and "Not-Associated" in subprocess.getoutput('iwconfig wlan0mon'):
            logging.debug("Ready to connect...")
            for network in access_points:
                if network['hostname'] == self.home_network:
                    signal_strength = network['rssi']
                    channel = network['channel']
                    if signal_strength >= 60:
                        self.ready = 0
                        self.status = f"Connecting to {self.home_network}..."

                        wpa_supplicant_conf_path = '/etc/wpa_supplicant/wpa_supplicant.conf'
                        with open(wpa_supplicant_conf_path, 'w') as wpa_supplicant_conf:
                            wpa_supplicant_conf.write(
                                f"network={{\n\tssid=\"{self.home_network}\"\n\tpsk=\"{self.home_password}\"\n}}\n")

                        subprocess.Popen(
                            ['wpa_supplicant', '-B', '-i', 'wlan0mon', '-c', wpa_supplicant_conf_path])
                        subprocess.Popen(['dhclient', 'wlan0mon'])

                        self.status = f"Connected to {self.home_network}!"

    def generate_fake_essid(self):
        return str(uuid.uuid4())[:8]

    def generate_random_mac_address(self):
        return ':'.join(['{:02x}'.format(random.randint(0, 255)) for _ in range(6)])

    def create_fake_aps(self):
        for _ in range(self.num_initial_aps):
            fake_essid = self.generate_fake_essid()
            fake_ap = {
                'essid': fake_essid,
                'addr': self.generate_random_mac_address(),
            }
            self.honey_pot_aps.add(fake_essid)
            self.log(f"Created HoneyPot: {fake_essid} ({fake_ap['addr']})")

    def render_honey_pots(self):
        self.ui.set('honey-pots', str(len(self.honey_pot_aps)))
        self.ui.set('detected-fake-aps', str(self.detected_fake_aps))
        self.ui.set('active-fake-aps', str(self.active_fake_aps))

        with open(self.log_path, 'a') as log_file:
            log_file.write(
                f"{time.strftime('%Y-%m-%d %H:%M:%S')} - Detected Fake APs: {self.detected_fake_aps}, Active Fake APs: {self.active_fake_aps}\n")

        self.detected_fake_aps = 0
        self.active_fake_aps = 0

        threading.Timer(self.update_interval, self.render_honey_pots).start()

    def render_network_status(self):
        self.ui.set('network-status', self.status)
        threading.Timer(self.update_interval,
                        self.render_network_status).start()

    def log(self, message):
        logging.info(message)
        if self.ui:
            status = self.ui.get('status')
            if status:
                status.value = message

# Register the combined plugin


def setup():
    return CombinedPlugin()
