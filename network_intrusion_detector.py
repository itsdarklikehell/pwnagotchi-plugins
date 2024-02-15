import scapy.all as scapy
from pwnagotchi.plugins import BasePlugin

class NetworkIntrusionDetector(BasePlugin):
    __author__ = 'Deus Dust'
    __version__ = '1.0.0'
    __license__ = 'MIT'

    def __init__(self):
        super(NetworkIntrusionDetector, self).__init__()

    def packet_handler(self, packet):
        # Voer hier aangepaste logica uit voor het detecteren van indringing
        if packet.haslayer(scapy.IP):
            ip_src = packet[scapy.IP].src
            ip_dst = packet[scapy.IP].dst
            self.log.info(f"Intrusion detected: {ip_src} -> {ip_dst}")

    def start_sniffing(self):
        scapy.sniff(prn=self.packet_handler, store=False)

    def on_loaded(self):
        self.log.info("Network Intrusion Detector Plugin loaded")
        self.start_sniffing()

    def on_unload(self):
        self.log.info("Network Intrusion Detector Plugin unloaded")

# Instantiate the plugin
plugin = NetworkIntrusionDetector()
