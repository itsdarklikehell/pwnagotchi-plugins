import logging

from pwnagotchi import plugins
from pwnagotchi.ui import fonts
from pwnagotchi.ui.components import LabeledValue
from pwnagotchi.ui.view import BLACK


class Deauth(plugins.Plugin):
    __author__ = "SgtStroopwafel, scorp"
    __version__ = "2.0.0"
    __license__ = "MIT"
    __description__ = (
        "A plugin that counts the successful deauth attacks of this session."
    )
    __name__ = "deauth"
    __help__ = "A plugin that counts the successful deauth attacks of this session."
    __dependencies__ = {
        "apt": ["none"],
        "pip": ["scapy"],
    }
    __defaults__ = {
        "enabled": False,
    }

    def __init__(self):
        self.deauth_counter = 0
        self.handshake_counter = 0
        logging.debug(f"[{self.__class__.__name__}] plugin init")

    def on_loaded(self):
        logging.info(f"[{self.__class__.__name__}] plugin loaded")

    def on_ui_setup(self, ui):
        # add custom UI elements
        ui.add_element(
            "deauth",
            LabeledValue(
                color=BLACK,
                label="Deauths ",
                value=str(self.deauth_counter),
                position=(ui.width() / 2 + 50, ui.height() - 25),
                label_font=fonts.Bold,
                text_font=fonts.Medium,
            ),
        )
        ui.add_element(
            "hand",
            LabeledValue(
                color=BLACK,
                label="Handshakes ",
                value=str(self.handshake_counter),
                position=(ui.width() / 2 + 50, ui.height() - 35),
                label_font=fonts.Bold,
                text_font=fonts.Medium,
            ),
        )

    def on_ui_update(self, ui):
        # update those elements
        ui.set("deauth", str(self.deauth_counter))
        ui.set("hand", str(self.handshake_counter))

    def on_deauthentication(self, agent, access_point, client_station):
        self.deauth_counter += 1

    def on_handshake(self, agent, filename, access_point, client_station):
        self.handshake_counter += 1

    def on_unload(self, ui):
        with ui._lock:
            try:
                ui.remove_element("deauth")
                ui.remove_element("hand")
                logging.info(f"[{self.__class__.__name__}] plugin unloaded")
            except Exception as e:
                logging.error(f"[{self.__class__.__name__}] unload: %s" % e)

    def on_webhook(self, path, request):
        logging.info(f"[{self.__class__.__name__}] webhook pressed")
