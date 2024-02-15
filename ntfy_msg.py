import pwnagotchi.plugins as plugins
import subprocess

class ntfy_msg(plugins.Plugin):
    __author__ = "Lehni"
    __version__ = '1.0.1'
    __license__ = 'GPL3'
    __description__ = 'Send notifications to any device with a ntfy call to your ntfy instance'

    def __init__(self):
        self.serverlink = "http://127.0.0.1/"
        self.name = "pwnagotchi"
        
    def on_loaded(self):
        if self.options['name']:
            self.name = self.options['name']
        self.serverlink = self.options['serverlink']

    def on_handshake(self, agent,filename, access_point, client_station):
        cmd = f"curl -d 'Your {self.name} has a new handshake for you' {self.serverlink}"

        try:
            subprocess.run(cmd, shell=True, check=True)
            self._log.info("Command executed successfully")
        except subprocess.CalledProcessError as e:
            self._log.error(f"Command failed with error: {e}")
        except Exception as e:
            self._log.error(f"An error occurred: {e}")