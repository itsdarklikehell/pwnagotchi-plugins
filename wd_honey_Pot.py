import logging
import threading
from pwnagotchi.ui.components import LabeledValue
import pwnagotchi.ui.fonts as fonts
import time
import uuid
import random
from pwnagotchi.plugins import Plugin


class HoneyPotPlugin(Plugin):
    __author__ = "Andryu Schittone"
    __version__ = "1.4.5"
    __license__ = "GPL3"
    __description__ = "A Pwnagotchi plugin for setting up a honey pot to detect other Pwnagotchis making deauths."

    def __init__(self):
        logging.debug("HoneyPot plugin created")
        self.ui = None
        self.honey_pot_aps = set()
        self.detected_fake_aps = 0
        self.active_fake_aps = 0
        self.num_initial_aps = 5
        self.update_interval = 60
        self.log_path = "/etc/pwnagotchi/hplogs.log"

        threading.Timer(self.update_interval, self.render_honey_pots).start()
        self.create_fake_aps()

    def on_loaded(self):
        """Register events on plugin load."""
        self.register_event(self.handle_wifi_handshake, "wifi-handshake")
        self.register_event(self.handle_ap_beacon, "ap-beacon")

    def on_unload(self, ui):
        """Unload method."""
        pass

    def on_ui_setup(self, ui):
        """Add UI elements with specific positions."""
        logging.info("Setting up UI")
        ui.add_element(
            "honey-pots", LabeledValue(label="Honey Pots", position=(125, 75))
        )
        ui.add_element(
            "detected-fake-aps",
            LabeledValue(label="Detected Fake APs", position=(125, 85)),
        )
        ui.add_element(
            "active-fake-aps", LabeledValue(label="Active Fake APs", position=(125, 95))
        )

    def on_ui_update(self, ui):
        """Update UI elements."""
        logging.info("Updating UI")
        ui.set("honey-pots", str(len(self.honey_pot_aps)))
        ui.set("detected-fake-aps", str(self.detected_fake_aps))
        ui.set("active-fake-aps", str(self.active_fake_aps))
        ui.update(force=True)

    def handle_wifi_handshake(self, agent, filename, access_point, client_station):
        """Handle wifi handshake event."""
        self.log(
            f"WiFi Handshake captured from {client_station['addr']} at {access_point['addr']}"
        )
        # Implement additional logic if needed, such as notification or logging.

    def handle_ap_beacon(self, agent, ap):
        """Handle AP beacon event."""
        if ap["essid"] in self.honey_pot_aps:
            self.log(f"Fake Beacon detected: {ap['essid']} ({ap['addr']})")
            self.detected_fake_aps += 1

        if ap["essid"] in self.honey_pot_aps:
            self.active_fake_aps += 1

    def generate_fake_essid(self):
        """Generate fake ESSID."""
        return str(uuid.uuid4())[:8]

    def generate_random_mac_address(self):
        """Generate random MAC address."""
        return ":".join(["{:02x}".format(random.randint(0, 255)) for _ in range(6)])

    def create_fake_aps(self):
        """Create fake access points."""
        for _ in range(self.num_initial_aps):
            fake_essid = self.generate_fake_essid()
            fake_ap = {
                "essid": fake_essid,
                "addr": self.generate_random_mac_address(),
            }
            self.honey_pot_aps.add(fake_essid)
            self.log(f"Created HoneyPot AP: {fake_essid} ({fake_ap['addr']})")

    def mask_mac_address(self, mac_address):
        """Mask the last 3 bytes of a MAC address."""
        masked_mac = mac_address[:9] + "XX:XX:XX"
        return masked_mac

    def log(self, message):
        """Log message and update UI status."""
        masked_message = message.replace(
            self.generate_random_mac_address(),
            self.mask_mac_address(self.generate_random_mac_address()),
        )
        logging.info(masked_message)
        if self.ui:
            status = self.ui.get("status")
            if status:
                status.value = masked_message

    def render_honey_pots(self):
        """Render honey pots on UI."""
        self.ui.set("honey-pots", str(len(self.honey_pot_aps)))
        self.ui.set("detected-fake-aps", str(self.detected_fake_aps))
        self.ui.set("active-fake-aps", str(self.active_fake_aps))

        with open(self.log_path, "a") as log_file:
            log_file.write(
                f"{time.strftime('%Y-%m-%d %H:%M:%S')} - Detected Fake APs: {self.detected_fake_aps}, "
                f"Active Fake APs: {self.active_fake_aps}\n"
            )

        self.detected_fake_aps = 0
        self.active_fake_aps = 0

        threading.Timer(self.update_interval, self.render_honey_pots).start()

    def generate_fake_station_info(self):
        """Generate fake information for a station."""
        fake_station_info = {
            "addr": self.generate_random_mac_address(),
            "vendor": "FakeVendor",  # Customize if needed
            "manuf": "FakeManufacturer",  # Customize if needed
            "channel": random.randint(1, 11),  # Customize channel range
            "essid": self.generate_fake_essid(),  # Customize if needed
            "key_mgmt": "WPA2-PSK",  # Customize if needed
            "wpa_cipher": "CCMP",  # Customize if needed
            "rsn_cipher": "CCMP",  # Customize if needed
        }
        return fake_station_info

    def generate_fake_ap_info(self):
        """Generate fake information for an access point."""
        fake_ap_info = {
            "essid": self.generate_fake_essid(),  # Customize if needed
            "addr": self.generate_random_mac_address(),
            "channel": random.randint(1, 11),  # Customize channel range
            "wpa": "2",  # Customize if needed
            "rsn_pairwise": "CCMP",  # Customize if needed
            "wpa_cipher": "CCMP",  # Customize if needed
            "rsn_cipher": "CCMP",  # Customize if needed
        }
        return fake_ap_info

    def add_fake_station(self):
        """Add a fake station to the set of honeypot stations."""
        fake_station_info = self.generate_fake_station_info()
        self.honey_pot_stations.add(fake_station_info)
        self.log(f"Added fake station: {fake_station_info['addr']}")

    def add_fake_ap(self):
        """Add a fake access point to the set of honeypot access points."""
        fake_ap_info = self.generate_fake_ap_info()
        self.honey_pot_aps.add(fake_ap_info)
        self.log(
            f"Added fake access point: {fake_ap_info['essid']} ({fake_ap_info['addr']})"
        )

    def remove_fake_station(self, fake_station_info):
        """Remove a fake station from the set of honeypot stations."""
        if fake_station_info in self.honey_pot_stations:
            self.honey_pot_stations.remove(fake_station_info)
            self.log(f"Removed fake station: {fake_station_info['addr']}")

    def remove_fake_ap(self, fake_ap_info):
        """Remove a fake access point from the set of honeypot access points."""
        if fake_ap_info in self.honey_pot_aps:
            self.honey_pot_aps.remove(fake_ap_info)
            self.log(
                f"Removed fake access point: {fake_ap_info['essid']} ({fake_ap_info['addr']})"
            )

    def get_fake_stations(self):
        """Get the list of fake stations in the honeypot stations set."""
        return list(self.honey_pot_stations)

    def get_fake_aps(self):
        """Get the list of fake access points in the honeypot access points set."""
        return list(self.honey_pot_aps)


# Register the plugin
def setup():
    return HoneyPotPlugin()


#


# USE IN CONFIG.TOML

# main.plugins.wd_honey_pot.update_interval = 60
# main.plugins.wd_honey_pot.num_initial_aps = 5
# main.plugins.wd_honey_pot.log_path = "/etc/pwnagotchi/hplogs.log"
# main.plugins.wd_honey_pot.fake_station.vendor = "FakeVendor"
# main.plugins.wd_honey_pot.fake_station.key_mgmt = "WPA2-PSK"
# main.plugins.wd_honey_pot.fake_station.wpa_cipher = "CCMP"
# main.plugins.wd_honey_pot.fake_station.manuf = "FakeManufacturer"
# main.plugins.wd_honey_pot.fake_station.rsn_cipher = "CCMP"
# main.plugins.wd_honey_pot.fake_ap.wpa = "2"
# main.plugins.wd_honey_pot.fake_ap.rsn_pairwise = "CCMP"
# main.plugins.wd_honey_pot.fake_ap.wpa_cipher = "CCMP"
# main.plugins.wd_honey_pot.fake_ap.rsn_cipher = "CCMP"
# main.plugins.wd_honey_pot.ui.honey-pots.color = 'BLACK'
# main.plugins.wd_honey_pot.ui.honey-pots.label = 'Honey Pots'
# main.plugins.wd_honey_pot.ui.honey-pots.position = [125, 75]
# main.plugins.wd_honey_pot.ui.honey-pots.label_font = 'Bold'
# main.plugins.wd_honey_pot.ui.honey-pots.text_font = 'Medium'
# main.plugins.wd_honey_pot.ui.detected-fake-aps.color = 'BLACK'
# main.plugins.wd_honey_pot.ui.detected-fake-aps.label = 'Detected Fake APs'
# main.plugins.wd_honey_pot.ui.detected-fake-aps.position = [125, 85]
# main.plugins.wd_honey_pot.ui.detected-fake-aps.label_font = 'Bold'
# main.plugins.wd_honey_pot.ui.detected-fake-aps.text_font = 'Medium'
# main.plugins.wd_honey_pot.ui.active-fake-aps.color = 'BLACK'
# main.plugins.wd_honey_pot.ui.active-fake-aps.label = 'Active Fake APs'
# main.plugins.wd_honey_pot.ui.active-fake-aps.position = [125, 95]
# main.plugins.wd_honey_pot.ui.active-fake-aps.label_font = 'Bold'
# main.plugins.wd_honey_pot.ui.active-fake-aps.text_font = 'Medium'
