import subprocess
from pwnagotchi.plugins import BasePlugin

class WiFiAnalyzer(BasePlugin):
    __author__ = 'Deus Dust'
    __version__ = '1.0.0'
    __license__ = 'MIT'

    def __init__(self):
        super(WiFiAnalyzer, self).__init__()

    def scan_wifi_networks(self):
        try:
            output = subprocess.check_output(["iwlist", "wlan0", "scan"])
            return output.decode('utf-8')
        except subprocess.CalledProcessError:
            self.log.error("Failed to scan WiFi networks.")
            return ""

    def on_loaded(self):
        self.log.info("WiFi Analyzer Plugin loaded")

    def on_periodic(self, agent):
        wifi_networks = self.scan_wifi_networks()
        if wifi_networks:
            self.log.info("Available WiFi networks:")
            agent.display_text("WiFi Networks:", font=fonts.Small)
            for line in wifi_networks.split('\n'):
                if "ESSID:" in line:
                    ssid = line.split('ESSID:"')[1].split('"')[0]
                    self.log.info(f"SSID: {ssid}")
                    agent.display_text(ssid, font=fonts.Small)

    def on_unload(self):
        self.log.info("WiFi Analyzer Plugin unloaded")

# Instantiate the plugin
plugin = WiFiAnalyzer()
