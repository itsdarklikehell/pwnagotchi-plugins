import scapy.all as scapy
from pwnagotchi.plugins import BasePlugin

class DNSSpoofDetector(BasePlugin):
    __author__ = 'Deus Dust'
    __version__ = '1.0.0'
    __license__ = 'MIT'

    def __init__(self):
        super(DNSSpoofDetector, self).__init__()

    def on_loaded(self):
        self.log.info("DNS Spoof Detector Plugin loaded")

    def dns_spoof_handler(self, packet):
        if packet.haslayer(scapy.DNSRR):
            dns_response = packet[scapy.DNSRR]
            if not dns_response.rdata:
                self.log.warning("Possible DNS Spoofing Detected!")
                # Add custom logic for handling DNS spoofing detection

    def start_sniffing(self):
        scapy.sniff(filter="udp port 53", prn=self.dns_spoof_handler, store=False)

    def on_periodic(self, agent):
        self.start_sniffing()

    def on_unload(self):
        self.log.info("DNS Spoof Detector Plugin unloaded")

# Instantiate the plugin
plugin = DNSSpoofDetector()
