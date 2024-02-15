import subprocess
from pwnagotchi.plugins import BasePlugin

class BluetoothScanner(BasePlugin):
    __author__ = 'Deus Dust'
    __version__ = '1.0.0'
    __license__ = 'MIT'

    def __init__(self):
        super(BluetoothScanner, self).__init__()

    def scan_bluetooth_devices(self):
        try:
            output = subprocess.check_output(["hcitool", "scan"])
            return output.decode('utf-8')
        except subprocess.CalledProcessError:
            self.log.error("Failed to scan Bluetooth devices.")
            return ""

    def on_loaded(self):
        self.log.info("Bluetooth Scanner Plugin loaded")

    def on_periodic(self, agent):
        bluetooth_devices = self.scan_bluetooth_devices()
        if bluetooth_devices:
            self.log.info("Available Bluetooth devices:")
            agent.display_text("Bluetooth Devices:", font=fonts.Small)
            for line in bluetooth_devices.split('\n'):
                if "Scanning ..." not in line and line.strip():
                    device_info = line.strip().split('\t')
                    device_mac = device_info[0]
                    device_name = device_info[1]
                    self.log.info(f"MAC: {device_mac}, Name: {device_name}")
                    agent.display_text(f"{device_name} ({device_mac})", font=fonts.Small)

    def on_unload(self):
        self.log.info("Bluetooth Scanner Plugin unloaded")

# Instantiate the plugin
plugin = BluetoothScanner()
