#
# Morse Code for pwnagotchi
#
# extending the led.py plugin to blink messages
# in morse code
#

from threading import Event
import _thread
import logging
import time

import pwnagotchi.plugins as plugins
from pwnagotchi.ui.components import LabeledValue
from pwnagotchi.ui.view import BLACK
import pwnagotchi.ui.fonts as fonts


class MorseCode(plugins.Plugin):
    __author__ = 'sniffleupagus'
    __version__ = '1.0.0'
    __license__ = 'GPL3'
    __description__ = 'An example plugin for pwnagotchi that implements all the available callbacks.'

    # Dictionary representing the morse code chart
    MORSE_CODE_DICT = { 'A':'.-', 'B':'-...',
                        'C':'-.-.', 'D':'-..', 'E':'.',
                        'F':'..-.', 'G':'--.', 'H':'....',
                        'I':'..', 'J':'.---', 'K':'-.-',
                        'L':'.-..', 'M':'--', 'N':'-.',
                        'O':'---', 'P':'.--.', 'Q':'--.-',
                        'R':'.-.', 'S':'...', 'T':'-',
                        'U':'..-', 'V':'...-', 'W':'.--',
                        'X':'-..-', 'Y':'-.--', 'Z':'--..',
                        '1':'.----', '2':'..---', '3':'...--',
                        '4':'....-', '5':'.....', '6':'-....',
                        '7':'--...', '8':'---..', '9':'----.',
                        '0':'-----', ', ':'--..--', '.':'.-.-.-',
                        '?':'..--..', '/':'-..-.', '-':'-....-',
                        '(':'-.--.', ')':'-.--.-'}

    def _convert_code(self, msg):
        didah = ''
        for l in msg:
            l = l.upper()
            if l in self.MORSE_CODE_DICT:
                didah += self.MORSE_CODE_DICT[l] + ' '
            else:
                # add a space for unknown characters
                didah += ' '
        return didah

    def _blink(self, msg):
        if len(msg) > 0:
            pattern = self._convert_code(msg)
            self.logger.info("[MORSE] '%s' -> '%s'" % (msg, pattern))

            # Attention signal
            for _ in range(3):
                self._led(1)
                time.sleep(0.5 * self._delay / 1000.0)
                self._led(0)
                time.sleep(0.5 * self._delay / 1000.0)
            time.sleep(4 * self._delay / 1000.0)

            for c in pattern:
                if c == '.':
                    self._led(1)
                    time.sleep(self._delay / 1000.0)
                    self._led(0)
                    time.sleep(self._delay / 1000.0)
                elif c == '-':
                    self._led(1)
                    time.sleep(3 * self._delay / 1000.0)
                    self._led(0)
                    time.sleep(self._delay / 1000.0)
                elif c == ' ':
                    time.sleep(2 * self._delay / 1000.0)
                else:
                    # unexpected character... skip it
                    pass

            # blank at end message
            self._led(0)
            time.sleep(7 * self._delay / 1000.0)

            if self.options['leaveOn']:
                # and back on
                self._led(1)

    # thread stuff copied from plugins/default/led.py

    # queue a message
    #   but if there is one already (busy) then don't
    def _queue_message(self, message):
        if not self._is_busy:
            self._message = message
            self._event.set()
            self.logger.debug("[Morse] message '%s' set", message)
        else:
            self.logger.debug("[Morse] skipping '%s' because the worker is busy", message)

    def _led(self, on):
        if on is "on": on = 1
        elif on is "off": on = 0

        # invert if LED brightness=1 is off, 0 is on
        if self.options['invert']:
            if on : on = 0
            else: on = 1

        with open(self._led_file, 'wt') as fp:
            fp.write(str(on))

    def _worker(self):
        while self._keep_going:
            self._event.wait()
            self._event.clear()

            if self._message is "QUITXXXQUIT":
                break

            self._is_busy = True
            self.logger.debug("Worker loop")

            try:
                self._blink(self._message)
                self.logger.debug("[Morse] blinked")
            except Exception as e:
                self.logger.warn("[Morse] error while blinking")

            finally:
                self._is_busy = False

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.logger.debug("[Morse] Code plugin initializing")
        self._is_busy = False
        self._keep_going = True
        self._event = Event()
        self._message = None
        self._led_file = "/sys/class/leds/led0/brightness"
        self._delay = 200


    # called when http://<host>:<port>/plugins/<plugin>/ is called
    # must return a html page
    # IMPORTANT: If you use "POST"s, add a csrf-token (via csrf_token() and render_template_string)
    def on_webhook(self, path, request):
        self.logger.info("[Morse] Web hook: %s" % repr(request))
        return "<html><body>Woohoo!</body></html>"

    # called when the plugin is loaded
    def on_loaded(self):
        try:
            self._is_busy = False

            self.logger.info("[Morse] loaded %s" % repr(self.options))

            for k,v in {'led': 0, 'delay' : 200, 'invert': True, 'leaveOn': False}.items():
                if k not in self.options:
                    self.options[k] = v


            self._led_file = "/sys/class/leds/led%d/brightness" % int(self.options['led'])
            self._delay = int(self.options['delay'])

            self._keep_going = True
            _thread.start_new_thread(self._worker, ())
            self._queue_message('loaded')
            self.logger.info("[Morse Code] plugin loaded for %s" % self._led_file)
        except Exception as err:
            self.logger.warn("[Morse Code] loading: %s" % repr(err))

    # called before the plugin is unloaded
    def on_unload(self, ui):
        self._keep_going = False
        self._queue_message('unload')

        pass

    # called when there's internet connectivity
    def on_internet_available(self, agent):
        pass

    # called when the hardware display setup is done, display is an hardware specific object
    def on_display_setup(self, display):
        pass

    # called when everything is ready and the main loop is about to start
    def on_ready(self, agent):
        self._queue_message("READY OK")
        # you can run custom bettercap commands if you want
        #   agent.run('ble.recon on')
        # or set a custom state
        #   agent.set_bored()

    # called when the AI finished loading
    def on_ai_ready(self, agent):
        self._queue_message("AI READY")
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
        self._queue_message("WOOHOO")
        pass

    # called when the AI got the worst reward so far
    def on_ai_worst_reward(self, agent, reward):
        self._queue_message("MEH")
        pass

    # called by bettercap events
    def on_bcap_ble_device_new(self, agent, event):
        self._queue_message("NEW BLE")
        pass
    
    # called when a non overlapping wifi channel is found to be free
    def on_free_channel(self, agent, channel):
        pass

    # called when the status is set to bored
    def on_bored(self, agent):
        pass

    # called when the status is set to sad
    def on_sad(self, agent):
        self._queue_message("SAD!!!")
        pass

    # called when the status is set to excited
    def on_excited(self, agent):
        pass

    # called when the status is set to lonely
    def on_lonely(self, agent):
        pass

    # called when the agent is rebooting the board
    def on_rebooting(self, agent):
        self._queue_message("HASTA LAVISTA BABY")
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
        self._queue_message("ASSOC")
        pass

    # called when the agent is deauthenticating a client station from an AP
    def on_deauthentication(self, agent, access_point, client_station):
        self._queue_message("PWNED")
        pass

    # callend when the agent is tuning on a specific channel
    def on_channel_hop(self, agent, channel):
        pass

    # called when a new handshake is captured, access_point and client_station are json objects
    # if the agent could match the BSSIDs to the current list, otherwise they are just the strings of the BSSIDs
    def on_handshake(self, agent, filename, access_point, client_station):
        self._queue_message("HI FRIEND")
        pass

    # called when an epoch is over (where an epoch is a single loop of the main algorithm)
    def on_epoch(self, agent, epoch, epoch_data):
        pass

    # called when a new peer is detected
    def on_peer_detected(self, agent, peer):
        self._queue_message("HI FRIEND")
        pass

    # called when a known peer is lost
    def on_peer_lost(self, agent, peer):
        self._queue_message("BYE FRIEND")
        pass
