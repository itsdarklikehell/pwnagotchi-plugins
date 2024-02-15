import scapy.all as scapy
from pwnagotchi.plugins import BasePlugin

class NetworkPacketSniffer(BasePlugin):
    __author__ = 'Deus Dust'
    __version__ = '1.0.0'
    __license__ = 'MIT'

    def __init__(self):
        super(NetworkPacketSniffer, self).__init__()

    def packet_handler(self, packet):
        # Voer hier aangepaste logica uit voor het verwerken van pakketten
        print(packet.summary())

    def start_sniffing(self):
        scapy.sniff(prn=self.packet_handler, store=False)

    def on_loaded(self):
        self.log.info("Network Packet Sniffer Plugin loaded")
        self.start_sniffing()

    def on_unload(self):
        self.log.info("Network Packet Sniffer Plugin unloaded")

# Instantiate the plugin
plugin = NetworkPacketSniffer()
