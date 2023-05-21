import logging

import pwnagotchi.plugins as plugins
from pwnagotchi.ui.components import LabeledValue
from pwnagotchi.ui.view import BLACK
import pwnagotchi.ui.fonts as fonts


class BLEMon(plugins.Plugin):
    __author__ = 'evilsocket@gmail.com'
    __version__ = '1.0.0'
    __license__ = 'GPL3'
    __description__ = 'An example plugin for pwnagotchi that implements all the available callbacks.'

    def __init__(self):
        logging.debug("BLEMon plugin created")
        self.blecount = 0
        self.blemaxcount = 0
        self.stopRecon = False
        self.agent = None

    # called when http://<host>:<port>/plugins/<plugin>/ is called
    # must return a html page
    # IMPORTANT: If you use "POST"s, add a csrf-token (via csrf_token() and render_template_string)
    def on_webhook(self, path, request):
        pass

    # called when the plugin is loaded
    def on_loaded(self):
        if 'face' not in self.options:
            self.options['face'] = "(B+B)"
        logging.warning("BLEMon loaded! with options = %s" % repr(self.options))

    # called before the plugin is unloaded
    def on_unload(self, ui):
        logging.info("[BLEMON] Unloading")
        if self.stopRecon:
            try:
                logging.info("[BLEMON] Stopping ble.recon")
                self.agent.run('ble.recon off; ble.clear')
                self.agent = None
                ui.remove_element('blemon_count')
            except Exception as err:
                logging.warning("[BLEMON] unload err: %s" % repr(err))
        pass

    # called hen there's internet connectivity
    def on_internet_available(self, agent):
        pass

    # called to setup the ui elements
    def on_ui_setup(self, ui):
        # add custom UI elements
        if "position" in self.options:
            pos = self.options['position'].split(',')
            pos = [int(x.strip()) for x in pos]
        else:
            pos = (0,15)

        ui.add_element('blemon_count', LabeledValue(color=BLACK, label='BLE', value='0/0', position=pos,
                                           label_font=fonts.Bold, text_font=fonts.Medium))

    # called when the ui is updated
    def on_ui_update(self, ui):
        # update those elements
        ui.set('blemon_count', "%d/%d" % (self.blecount, self.blemaxcount))

    # called when the hardware display setup is done, display is an hardware specific object
    def on_display_setup(self, display):
        pass

    # called when everything is ready and the main loop is about to start
    def on_ready(self, agent):
        logging.info("[BLEMON] Starting ble.recon")
        if self.agent is None: self.agent = agent
        # you can run custom bettercap commands if you want
        try:
            agent.run('ble.clear; ble.recon on')
            self.stopRecon = True
        except Exception as err:
            logging.warning("[BLEMON] ble probably already running: %s" % repr(err))
            self.stopRecon = False

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
        pass

    # called when the AI got the worst reward so far
    def on_ai_worst_reward(self, agent, reward):
        pass

    # called when a non overlapping wifi channel is found to be free
    def on_free_channel(self, agent, channel):
        pass

    # called when the status is set to bored
    def on_bored(self, agent):
        pass

    # called when the status is set to sad
    def on_sad(self, agent):
        pass

    # called when the status is set to excited
    def on_excited(self, agent):
        pass

    # called when the status is set to lonely
    def on_lonely(self, agent):
        pass

    # called when the agent is rebooting the board
    def on_rebooting(self, agent):
        pass

    # called when the agent is waiting for t seconds
    def on_wait(self, agent, t):
        pass

    # called when the agent is sleeping for t seconds
    def on_sleep(self, agent, t):
        pass

    # called when the agent refreshed its access points list
    def on_wifi_update(self, agent, access_points):
        pass

    # called when the agent refreshed an unfiltered access point list
    # this list contains all access points that were detected BEFORE filtering
    def on_unfiltered_ap_list(self, agent, access_points):
        pass

    # called when the agent is sending an association frame
    def on_association(self, agent, access_point):
        pass

    # called when the agent is deauthenticating a client station from an AP
    def on_deauthentication(self, agent, access_point, client_station):
        pass

    # callend when the agent is tuning on a specific channel
    def on_channel_hop(self, agent, channel):
        pass

    # called when a new handshake is captured, access_point and client_station are json objects
    # if the agent could match the BSSIDs to the current list, otherwise they are just the strings of the BSSIDs
    def on_handshake(self, agent, filename, access_point, client_station):
        pass

    # called when an epoch is over (where an epoch is a single loop of the main algorithm)
    def on_epoch(self, agent, epoch, epoch_data):
        pass

    # called when a new peer is detected
    def on_peer_detected(self, agent, peer):
        pass

    # called when a known peer is lost
    def on_peer_lost(self, agent, peer):
        pass


    # bettercap BLE events. access everything

    def on_bcap_ble_device_new(self, agent, event):
        try:
            logging.info("[BLEMon] BLE device NEW: %s" % repr(event))
            name = event['data']['name']
            mac = event['data']['mac']
            self.blecount = self.blecount + 1
            if (self.blecount > self.blemaxcount): self.blemaxcount = self.blecount

            display = agent.view()
            display.set('face', self.options['face'])
            display.set('blemon_count', "%d/%d" % (self.blecount, self.blemaxcount))
            if name is '':
                display.set('status', "Something blue!!!")
                if mac:
                    # enqueue an enum. run one per epoch
                    # if error, then repeat next time, maybe?
                    res = self.agent.run('ble.enum %s' % mac)
                    logging.info("[BLEMon] enum %s: %s" % (mac, repr(res)))
            else:
                display.set('status', "Blue buddy %s" % name)
        except Exception as err:
            logging.warning("[BLEMon] ble new Error: %s" % err)

    def on_bcap_ble_device_connected(self, agent, event):
        try:
            logging.info("[BLEMon] BLE device CON: %s" % repr(event))
        except Exception as err:
            logging.warning("[BLEMon] ble CON Error: %s" % err)

    def on_bcap_ble_device_service_discovered(self, agent, event):
        try:
            logging.info("[BLEMon] BLE device SVC: %s" % repr(event))
        except Exception as err:
            logging.warning("[BLEMon] ble SVC Error: %s" % err)

    def on_bcap_ble_device_characteristic_discovered(self, agent, event):
        try:
            logging.info("[BLEMon] BLE device CHR: %s" % repr(event))
        except Exception as err:
            logging.warning("[BLEMon] ble CHR Error: %s" % err)

    def on_bcap_ble_device_disconnected(self, agent, event):
        try:
            logging.info("[BLEMon] BLE device DISCON: %s" % repr(event))
        except Exception as err:
            logging.warning("[BLEMon] ble disconn Error: %s" % err)


    def on_bcap_ble_device_lost(self, agent, event):
        try:
            logging.debug("[BLEMon] BLE device LOST: %s" % repr(event))
            name = event['data']['name']
            self.blecount = self.blecount - 1
            ui = agent.view()
            ui.set('blecount', "%d/%d" % (self.blecount, self.blemaxcount))

            if name is '':
                ui.set('status', "So long blue!!!")
            else:
                ui.set('status', "Bye %s" % name)
        except Exception as err:
            logging.warning("[BLEMon] ble lost Error: %s" % err)


