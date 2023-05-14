from multiprocessing.connection import Listener
import pwnagotchi
import pwnagotchi.plugins as plugins
import logging

class powerutils(plugins.Plugin):
    __author__ = 'https://gitlab.com/sn0wflake'
    __version__ = '1.0.0'
    __license__ = 'MIT'
    __description__ = 'A server to shutdown or restart pwnagotchi hardware'

    def __init__(self):
        self.running = True

    def on_loaded(self):
        logging.info("Powerutils Plugin loaded.")
        address = ('localhost', 6799)
        listener = Listener(address)
        while self.running:
            conn = listener.accept()
            msg = conn.recv() # Blocking - waits here for incoming message.
            conn.close()

            if msg == 'shutdown':
                pwnagotchi.shutdown()

            elif msg == 'restart-auto':
                pwnagotchi.restart('auto')

            elif msg == 'restart-manual':
                pwnagotchi.restart('manual')

            elif msg == 'reboot-auto':
                pwnagotchi.reboot('auto')

            elif msg == 'reboot-manual':
                pwnagotchi.reboot('manual')

    def on_unload(self, ui):
        self.running = False
        logging.info("Powerutils plugin unloaded.")
