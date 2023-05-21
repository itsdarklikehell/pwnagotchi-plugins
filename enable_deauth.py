import logging

import pwnagotchi.plugins as plugins
from pwnagotchi.ui.components import LabeledValue
from pwnagotchi.ui.view import BLACK
import pwnagotchi.ui.fonts as fonts


class Do_Deauth(plugins.Plugin):
    __author__ = 'evilsocket@gmail.com'
    __version__ = '1.0.0'
    __license__ = 'GPL3'
    __description__ = 'Enable and disable DEAUTH on the fly. Enabled when plugin loads, disabled when plugin unloads.'

    def __init__(self):
        self._agent = None
        self._count = 0
        pass

    # called when http://<host>:<port>/plugins/<plugin>/ is called
    # must return a html page
    # IMPORTANT: If you use "POST"s, add a csrf-token (via csrf_token() and render_template_string)
    def on_webhook(self, path, request):
        pass

    # called when the plugin is loaded
    def on_loaded(self):
        self._count = 0
        pass

    # called before the plugin is unloaded
    def on_unload(self, ui):
        if self._agent: self._agent._config['personality']['deauth'] = False
        ui.remove_element('deauth_count')
        logging.info("[Enable_Deauth] unloading: disabled deauth")
        pass

    # called when everything is ready and the main loop is about to start
    def on_ready(self, agent):
        agent._config['personality']['deauth'] = True
        self._agent = agent
        logging.info("[Enable_Deauth] ready: enabled deauth")

    def on_deauthentication(self, agent, access_point, client_station):
        self._count += 1
        pass

    # called to setup the ui elements
    def on_ui_setup(self, ui):
        # add custom UI elements
        try:
            if "position" in self.options:
                pos = self.options['position'].split(',')
                pos = [int(x.strip()) for x in pos]
            else:
                pos = (0,36)

            ui.add_element('deauth_count', LabeledValue(color=BLACK, label='D', value='0', position=pos,
                                                        label_font=fonts.BoldSmall, text_font=fonts.Small))
        except Exception as err:
            logging.info("enable deauth ui error: %s" % repr(err))

        # called when the ui is updated
    def on_ui_update(self, ui):
        # update those elements
        try:
            ui.set('deauth_count', "%d" % (self._count))
        except Exception as err:
            logging.info("enable deauth ui error: %s" % repr(err))
