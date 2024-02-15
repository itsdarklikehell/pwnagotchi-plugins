import subprocess
import random
from pwnagotchi.plugins import BasePlugin

class MACRandomizer(BasePlugin):
    __author__ = 'Deus Dust'
    __version__ = '1.0.0'
    __license__ = 'MIT'

    def __init__(self):
        super(MACRandomizer, self).__init__()

    def randomize_mac(self):
        new_mac = ':'.join(['{:02x}'.format(random.randint(0, 255)) for _ in range(6)])
        try:
            subprocess.run(['sudo', 'ifconfig', 'wlan0', 'down'])
            subprocess.run(['sudo', 'ifconfig', 'wlan0', 'hw', 'ether', new_mac])
            subprocess.run(['sudo', 'ifconfig', 'wlan0', 'up'])
            self.log.info(f"MAC Address changed to: {new_mac}")
        except Exception as e:
            self.log.error(f"Failed to change MAC Address: {e}")

    def on_loaded(self):
        self.log.info("MAC Randomizer Plugin loaded")
        self.randomize_mac()

    def on_unload(self):
        self.log.info("MAC Randomizer Plugin unloaded")

# Instantiate the plugin
plugin = MACRandomizer()
