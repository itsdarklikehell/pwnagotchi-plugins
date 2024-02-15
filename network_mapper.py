import nmap
from pwnagotchi.plugins import BasePlugin

class NetworkMapper(BasePlugin):
    __author__ = 'Deus Dust'
    __version__ = '1.0.0'
    __license__ = 'MIT'

    def __init__(self):
        super(NetworkMapper, self).__init__()

    def scan_network(self):
        nm = nmap.PortScanner()
        nm.scan(hosts='192.168.1.0/24', arguments='-sn')
        return nm.all_hosts()

    def on_loaded(self):
        self.log.info("Network Mapper Plugin loaded")

    def on_periodic(self, agent):
        hosts = self.scan_network()
        self.log.info("Discovered hosts:")
        for host in hosts:
            self.log.info(f"Host: {host}")

    def on_unload(self):
        self.log.info("Network Mapper Plugin unloaded")

# Instantiate the plugin
plugin = NetworkMapper()
