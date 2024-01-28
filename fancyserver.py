#modified code from powerutils plugin of https://gitlab.com/sn0wflake

from multiprocessing.connection import Listener
import pwnagotchi
import pwnagotchi.plugins as plugins
import logging
from pwnagotchi.plugins import toggle_plugin
import time

class fancyserver(plugins.Plugin):
    __author__ = '@V0rT3x https://github.com/V0r-T3x'
    __version__ = '1.0.0'
    __license__ = 'MIT'
    __description__ = 'A server to receive extra commands to control your Pwnagotchi'

    def __init__(self):
        self.running = True

    def on_loaded(self):
        while self.running:
            try:
                logging.info("Fancyserver Plugin loaded.")
                address = ('localhost', 3699)
                listener = Listener(address)
                while self.running:
                    try:
                        logging.warning('start loop fancyserver')
                        conn = listener.accept()
                        command = conn.recv()  # Blocking - waits here for incoming message.
                        conn.close()

                        msg = command[0]
                        if len(command) > 1:
                            name = command[1]
                            state = command[2]

                        if msg == 'shutdown':
                            pwnagotchi.shutdown()

                        elif msg == 'restart-auto':
                            pwnagotchi.restart('auto')

                        elif msg == 'restart-manual':
                            logging.warning('restart in manual mode')
                            pwnagotchi.restart('manual')

                        elif msg == 'reboot-auto':
                            pwnagotchi.reboot('auto')

                        elif msg == 'reboot-manual':
                            pwnagotchi.reboot('manual')

                        elif msg == 'plugin':
                            logging.warning('plugin command ' + name + ' ' + state)
                            if state == 'True':
                                is_change = toggle_plugin(name, enable=True)
                                # logging.warning('enable: '+is_change)
                            else:
                                is_change = toggle_plugin(name, enable=False)
                                # logging.warning('disable: '+is_change)
                            if is_change:
                                logging.warning(name+' changed state')
                            else:
                                logging.warning(name+" didn't changed state")

                    except ConnectionRefusedError as cre:
                        logging.warning(f"Connection refused error: {cre}")
                        time.sleep(5)  # wait for a few seconds before attempting to reconnect

            except Exception as e:
                logging.warning(f"An unexpected error occurred: {e}")
                logging.warning(traceback.format_exc())
                time.sleep(5)  # wait for a few seconds before attempting to restart the script

    def on_unload(self, ui):
        self.running = False
        logging.info("Fancyservers plugin unloaded.")
