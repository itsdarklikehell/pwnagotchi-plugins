import scapy.all as scapy
from pwnagotchi.plugins import BasePlugin

class TrafficSniffer(BasePlugin):
    __author__ = 'Deus Dust'
    __version__ = '1.0.0'
    __license__ = 'MIT'

    def __init__(self):
        super(TrafficSniffer, self).__init__()

    def on_loaded(self):
        self.log.info("Traffic Sniffer Plugin loaded")

    def packet_handler(self, packet):
        # Customize packet handling logic here
        print(packet.summary())

    def start_sniffing(self):
        scapy.sniff(prn=self.packet_handler, store=False)

    def on_periodic(self, agent):
        self.start_sniffing()

    def on_unload(self):
        self.log.info("Traffic Sniffer Plugin unloaded")

# Instantiate the plugin
plugin = TrafficSniffer()
