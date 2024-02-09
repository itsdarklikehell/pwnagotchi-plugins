import logging
import pwnagotchi
import pwnagotchi.plugins as plugins


class Darkmode(plugins.Plugin):
    __GitHub__ = ""
    __author__ = "(edited by: itsdarklikehell bauke.molenaar@gmail.com), sliim@mailoo.org"
    __version__ = "1.0.0"
    __license__ = "GPL3"
    __description__ = "Darkmode plugin."
    __name__ = "Darkmode"
    __help__ = "Darkmode plugin."
    __dependencies__ = {
        "apt": ["none"],
        "pip": ["scapy"],
    }
    __defaults__ = {
        "enabled": False,
    }

    def __init__(self):
        self.ready = False
        logging.debug(f"[{self.__class__.__name__}] plugin init")
        self.title = ""

    def _update_ui_colors(self, ui):
        for key, element in ui._state.items():
            if element.color != pwnagotchi.ui.view.BLACK:
                logging.warn(
                    f"[{self.__class__.__name__}] Update element color: %s" % key
                )
                element.color = pwnagotchi.ui.view.BLACK
                ui.remove_element(key)
                ui.add_element(key, element)

    def on_loaded(self):
        logging.info(f"[{self.__class__.__name__}] plugin loaded")
        try:
            pwnagotchi.ui.view.BLACK = 0xFF
            pwnagotchi.ui.view.WHITE = 0x00
            logging.info(f"[{self.__class__.__name__}] plugin loaded")
        except Exception as e:
            logging.error(f"[{self.__class__.__name__}] _loaded: %s" % e)

    def on_unload(self, ui):
        logging.info(f"[{self.__class__.__name__}] plugin unloaded")
        try:
            pwnagotchi.ui.view.BLACK = 0x00
            pwnagotchi.ui.view.WHITE = 0xFF
            self._update_ui_colors(ui)
            logging.info(f"[{self.__class__.__name__}] plugin unloaded")
        except Exception as e:
            logging.error(f"[{self.__class__.__name__}] unload: %s" % e)

    def on_ui_update(self, ui):
        try:
            self._update_ui_colors(ui)
        except Exception as e:
            logging.error(f"[{self.__class__.__name__}] update: %s" % e)

    def on_webhook(self, path, request):
        logging.info(f"[{self.__class__.__name__}] webhook pressed")
