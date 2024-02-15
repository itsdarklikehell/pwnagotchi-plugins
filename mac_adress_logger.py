from pwnagotchi.plugins import BasePlugin

class MacAddressLogger(BasePlugin):
    __author__ = 'Deus Dust'
    __version__ = '1.0.0'
    __license__ = 'MIT'

    def __init__(self):
        super(MacAddressLogger, self).__init__()

    def on_loaded(self):
        self.log.info("MAC Address Logger Plugin loaded")

    def on_handshake(self, agent, filename, access_point):
        self.log.info(f"Handshake captured from {access_point['station']}")
        self.log.info(f"MAC Address: {access_point['station']}")
        # You can save or log this MAC address as needed

    def on_unload(self):
        self.log.info("MAC Address Logger Plugin unloaded")

# Instantiate the plugin
plugin = MacAddressLogger()
