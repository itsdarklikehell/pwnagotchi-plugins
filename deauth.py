import logging

from pwnagotchi import plugins
from pwnagotchi.ui import fonts
from pwnagotchi.ui.components import LabeledValue
from pwnagotchi.ui.view import BLACK


class Deauth(plugins.Plugin):
    __author__ = 'scorp'
    __version__ = '2.0.0'
    __name__ = 'deauthcounter'
    __license__ = 'MIT'
    __description__ = 'counts the successful deauth attacks of this session '
    __defaults__ = {
        'enabled': False,
    }

    def __init__(self):
        self.deauth_counter = 0
        self.handshake_counter = 0

    def on_loaded(self):
        logging.info("[deauth] pluginloaded")

    # called to setup the ui elements
    def on_ui_setup(self, ui):
        # add custom UI elements
        ui.add_element('deauth', LabeledValue(color=BLACK, label='Deauths ', value=str(self.deauth_counter),
                                              position=(ui.width() / 2 + 50, ui.height() - 25),
                                              label_font=fonts.Bold, text_font=fonts.Medium))
        ui.add_element('hand', LabeledValue(color=BLACK, label='Handshakes ', value=str(self.handshake_counter),
                                            position=(ui.width() / 2 + 50, ui.height() - 35),
                                            label_font=fonts.Bold, text_font=fonts.Medium))

    # called when the ui is updated
    def on_ui_update(self, ui):
        # update those elements
        ui.set('deauth', str(self.deauth_counter))
        ui.set('hand', str(self.handshake_counter))

    # called when the agent is deauthenticating a client station from an AP
    def on_deauthentication(self, agent, access_point, client_station):
        self.deauth_counter += 1

    def on_handshake(self, agent, filename, access_point, client_station):
        self.handshake_counter += 1
