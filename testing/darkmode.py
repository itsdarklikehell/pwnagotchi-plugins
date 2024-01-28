import logging
import pwnagotchi
import pwnagotchi.plugins as plugins


class Darkmode(plugins.Plugin):
    __author__ = "sliim@mailoo.org"
    __version__ = "1.0.0"
    __license__ = "GPL3"
    __description__ = "Darkmode plugin."

    def _update_ui_colors(self, ui):
        for key, element in ui._state.items():
            if element.color != pwnagotchi.ui.view.BLACK:
                logging.warning("[darkmode] Update element color: %s" % key)
                element.color = pwnagotchi.ui.view.BLACK
                ui.remove_element(key)
                ui.add_element(key, element)

    def on_loaded(self):
        try:
            pwnagotchi.ui.view.BLACK = 0xff
            pwnagotchi.ui.view.WHITE = 0x00
            logging.info("[darkmode] plugin loaded")
        except Exception as e:
            logging.error("darkmode.on_loaded: %s" % e)

    def on_unload(self, ui):
        try:
            pwnagotchi.ui.view.BLACK = 0x00
            pwnagotchi.ui.view.WHITE = 0xff
            self._update_ui_colors(ui)
            logging.info("[darkmode] plugin unloaded")
        except Exception as e:
            logging.error("darkmode.on_unload: %s" % e)

    def on_ui_update(self, ui):
        try:
            self._update_ui_colors(ui)
        except Exception as e:
            logging.error("darkmode.on_ui_update: %s" % e)
