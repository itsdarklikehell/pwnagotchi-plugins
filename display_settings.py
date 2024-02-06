import logging

import pwnagotchi.plugins as plugins
from pwnagotchi.ui.components import LabeledValue
from pwnagotchi.ui.view import BLACK
import pwnagotchi.ui.fonts as fonts


class DisplaySettings(plugins.Plugin):
    __author__ = "Sniffleupagus"
    __version__ = "1.0.0"
    __license__ = "GPL3"
    __description__ = "Control backlight, and maybe other settings for displays. (but only pimoroni displayhatmini for now)"

    def __init__(self):
        logging.debug("DisplaySettings plugin created")
        logging.debug(f"[{self.__class__.__name__}] plugin created")

    # called when http://<host>:<port>/plugins/<plugin>/ is called
    # must return a html page
    # IMPORTANT: If you use "POST"s, add a csrf-token (via csrf_token() and render_template_string)
    def on_webhook(self, path, request):
        # show sliders and control and shit :)
        pass

    # called when the plugin is loaded
    def on_loaded(self):
        logging.info("DisplaySettings options = %s" % self.options)
        logging.info(f"[{self.__class__.__name__}] plugin loaded")

    # called before the plugin is unloaded
    def on_unload(self, ui):
        logging.info("goodbye")
        pass

    # called hen there's internet connectivity
    def on_internet_available(self, agent):
        pass

    # called to setup the ui elements
    def on_ui_setup(self, ui):
        try:
            self._ui = ui
            self._display = ui._implementation
            if hasattr(self._display, "get_backlight"):
                logging.info("UI backlight ready")
            if hasattr(self._ui, "set_backgroundcolor"):
                logging.info("UI backgrounds ready")
            # add custom UI elements
        except Exception as err:
            logging.warn("Display: %s, err: %s" % (repr(self._display), repr(err)))

    # called when the ui is updated
    def on_ui_update(self, ui):
        # update those elements
        pass

    # called when the hardware display setup is done, display is an hardware specific object
    def on_display_setup(self, display):
        self._display = display
        # if hasattr(display, "get_backlight"):

        pass

    # called when everything is ready and the main loop is about to start
    def on_ready(self, agent):
        logging.info("unit is ready")
        # you can run custom bettercap commands if you want
        #   agent.run('ble.recon on')
        # or set a custom state
        #   agent.set_bored()

    # called when the AI finished loading
    def on_ai_ready(self, agent):
        pass

    # called when the AI finds a new set of parameters
    def on_ai_policy(self, agent, policy):
        pass

    # called when the AI starts training for a given number of epochs
    def on_ai_training_start(self, agent, epochs):
        pass

    # called after the AI completed a training epoch
    def on_ai_training_step(self, agent, _locals, _globals):
        pass

    # called when the AI has done training
    def on_ai_training_end(self, agent):
        pass

    # called when the AI got the best reward so far
    def on_ai_best_reward(self, agent, reward):
        if hasattr(self._display, "set_backgroundcolor"):
            self._ui.set_backgroundcolor("#708090")
        pass

    # called when the AI got the worst reward so far
    def on_ai_worst_reward(self, agent, reward):
        if hasattr(self._ui, "set_backgroundcolor"):
            self._ui.set_backgroundcolor("#203040")
        pass

    # called when a non overlapping wifi channel is found to be free
    def on_free_channel(self, agent, channel):
        pass

    # called when the status is set to bored
    def on_bored(self, agent):
        if hasattr(self._ui, "set_backgroundcolor"):
            self._ui.set_backgroundcolor("#308080")
        pass

    # called when the status is set to sad
    def on_sad(self, agent):
        if hasattr(self._ui, "set_backgroundcolor"):
            self._ui.set_backgroundcolor("#302080")
        pass

    # called when the status is set to excited
    def on_excited(self, agent):
        try:
            if hasattr(self._display, "set_backlight"):
                self._display.set_backlight(0.9)
            if hasattr(self._ui, "set_backgroundcolor"):
                self._ui.set_backgroundcolor("#c08080")
        except Exception as err:
            logging.warn(repr(err))
        pass

    # called when the status is set to lonely
    def on_lonely(self, agent):
        try:
            if hasattr(self._display, "set_backlight"):
                self._display.set_backlight(0.4)
            if hasattr(self._ui, "set_backgroundcolor"):
                self._ui.set_backgroundcolor("#101090")
        except Exception as err:
            logging.warn(repr(err))
        pass

    # called when the agent is rebooting the board
    def on_rebooting(self, agent):
        if hasattr(self._ui, "set_backgroundcolor"):
            self._ui.set_backgroundcolor("#101010")
        pass

    # called when the agent is waiting for t seconds
    def on_wait(self, agent, t):
        try:
            if hasattr(self._display, "set_backlight"):
                self._display.set_backlight(0.2)
            if hasattr(self._ui, "set_backgroundcolor"):
                self._ui.set_backgroundcolor("#600000")
        except Exception as err:
            logging.warn(repr(err))
        pass

    # called when the agent is sleeping for t seconds
    def on_sleep(self, agent, t):
        try:
            if hasattr(self._display, "set_backlight"):
                self._display.set_backlight(0.1)
            if hasattr(self._ui, "set_backgroundcolor"):
                self._ui.set_backgroundcolor("#000080")
        except Exception as err:
            logging.warn(repr(err))
        pass

    # called when the agent refreshed its access points list
    def on_wifi_update(self, agent, access_points):
        try:
            if hasattr(self._display, "set_backlight"):
                self._display.set_backlight(0.6)
            if hasattr(self._ui, "set_backgroundcolor"):
                self._ui.set_backgroundcolor("#208030")
        except Exception as err:
            logging.warn(repr(err))
        pass

    # called when the agent refreshed an unfiltered access point list
    # this list contains all access points that were detected BEFORE filtering
    def on_unfiltered_ap_list(self, agent, access_points):
        pass

    # called when the agent is sending an association frame
    def on_association(self, agent, access_point):
        try:
            if hasattr(self._display, "set_backlight"):
                self._display.set_backlight(0.8)
            if hasattr(self._ui, "set_backgroundcolor"):
                self._ui.set_backgroundcolor("#208020")
        except Exception as err:
            logging.warn(repr(err))
        pass

    # called when the agent is deauthenticating a client station from an AP
    def on_deauthentication(self, agent, access_point, client_station):
        if hasattr(self._ui, "set_backgroundcolor"):
            self._ui.set_backgroundcolor("#400000")
        pass

    # callend when the agent is tuning on a specific channel
    def on_channel_hop(self, agent, channel):
        if hasattr(self._ui, "set_backgroundcolor"):
            self._ui.set_backgroundcolor("#00a000")
        pass

    # called when a new handshake is captured, access_point and client_station are json objects
    # if the agent could match the BSSIDs to the current list, otherwise they are just the strings of the BSSIDs
    def on_handshake(self, agent, filename, access_point, client_station):
        try:
            if hasattr(self._display, "set_backlight"):
                self._display.set_backlight(1.0)
            if hasattr(self._ui, "set_backgroundcolor"):
                self._ui.set_backgroundcolor("#00FF00")
        except Exception as err:
            logging.warn(repr(err))
        pass

    # called when an epoch is over (where an epoch is a single loop of the main algorithm)
    def on_epoch(self, agent, epoch, epoch_data):
        if hasattr(self._ui, "set_backgroundcolor"):
            self._ui.set_backgroundcolor("#305070")
        pass

    # called when a new peer is detected
    def on_peer_detected(self, agent, peer):
        try:
            if hasattr(self._display, "set_backlight"):
                self._display.set_backlight(1.0)
            if hasattr(self._ui, "set_backgroundcolor"):
                self._ui.set_backgroundcolor("#008080")
        except Exception as err:
            logging.warn(repr(err))
        pass

    # called when a known peer is lost
    def on_peer_lost(self, agent, peer):
        if hasattr(self._ui, "set_backgroundcolor"):
            self._ui.set_backgroundcolor("#800080")
        pass
