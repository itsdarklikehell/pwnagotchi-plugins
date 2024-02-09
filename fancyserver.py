# modified code from powerutils plugin of https://gitlab.com/sn0wflake

from multiprocessing.connection import Listener
import pwnagotchi
import pwnagotchi.plugins as plugins
import logging
from pwnagotchi.plugins import toggle_plugin
import time


class fancyserver(plugins.Plugin):
    __author__ = "SgtStroopwafel, @V0rT3x https://github.com/V0r-T3x"
    __version__ = "1.0.0"
    __license__ = "MIT"
    __description__ = "A server to receive extra commands to control your Pwnagotchi"
    __name__ = "fancyserver"
    __help__ = "A server to receive extra commands to control your Pwnagotchi"
    __dependencies__ = {
        "apt": ["none"],
        "pip": ["scapy"],
    }
    __defaults__ = {
        "enabled": false,
    }

    def __init__(self):
        self.running = True
        self.ready = False
        logging.debug(f"[{self.__class__.__name__}] plugin init")
        self.title = ""

    def on_loaded(self):
        while self.running:
            try:
                logging.info(f"[{self.__class__.__name__}] plugin loaded")
                address = ("localhost", 3699)
                listener = Listener(address)
                while self.running:
                    try:
                        logging.warn("start loop fancyserver")
                        conn = listener.accept()
                        command = (
                            conn.recv()
                        )  # Blocking - waits here for incoming message.
                        conn.close()

                        msg = command[0]
                        if len(command) > 1:
                            name = command[1]
                            state = command[2]

                        if msg == "shutdown":
                            pwnagotchi.shutdown()

                        elif msg == "restart-auto":
                            pwnagotchi.restart("auto")

                        elif msg == "restart-manual":
                            logging.warn("restart in manual mode")
                            pwnagotchi.restart("manual")

                        elif msg == "reboot-auto":
                            pwnagotchi.reboot("auto")

                        elif msg == "reboot-manual":
                            pwnagotchi.reboot("manual")

                        elif msg == "plugin":
                            logging.warn("plugin command " + name + " " + state)
                            if state == "True":
                                is_change = toggle_plugin(name, enable=True)
                                # logging.warn('enable: '+is_change)
                            else:
                                is_change = toggle_plugin(name, enable=False)
                                # logging.warn('disable: '+is_change)
                            if is_change:
                                logging.warn(name + " changed state")
                            else:
                                logging.warn(name + " didn't changed state")

                    except ConnectionRefusedError as cre:
                        logging.warn(f"Connection refused error: {cre}")
                        time.sleep(
                            5
                        )  # wait for a few seconds before attempting to reconnect

            except Exception as e:
                logging.warn(f"An unexpected error occurred: {e}")
                logging.warn(traceback.format_exc())
                time.sleep(
                    5
                )  # wait for a few seconds before attempting to restart the script

    def on_unload(self, ui):
        self.running = False
        logging.info(f"[{self.__class__.__name__}] plugin unloaded")
