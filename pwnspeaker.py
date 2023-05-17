import logging
import os
import pyttsx3
import pwnagotchi.plugins as plugins
from pwnagotchi.ui.components import LabeledValue
from pwnagotchi.ui.view import BLACK
import pwnagotchi.ui.fonts as fonts

# object creation
engine = pyttsx3.init()

# getting details of current speaking rate
rate = engine.getProperty("rate")
# setting up new voice rate
# engine.setProperty('rate', 125)

# getting to know current volume level (min=0 and max=1)
volume = engine.getProperty("volume")
# setting up volume level  between 0 and 1
# engine.setProperty('volume',1.0)

# getting details of current voice
voices = engine.getProperty("voices")
# changing index, changes voices. o for male
# engine.setProperty('voice', voices[0].id)
# changing index, changes voices. 1 for female
# engine.setProperty('voice', voices[1].id)


class Pwnspeak(plugins.Plugin):
    __author__ = "bauke.molenaar@gmail.com"
    __version__ = "1.0.0"
    __license__ = "GPL3"
    __description__ = (
        "An Pwnspeak plugin for pwnagotchi that implements all the available callbacks."
    )
    __name__ = "Pwnspeak"
    __help__ = """
-this plugin needs a installed and working audio DAC HAT, USB-Soundcard or a connected bt-headset/headphone for audio output, like https://www.raspiaudio.com/
-for enable text2speech on raspberry-pi-zero with debian buster to speak the SSID on handshake and others, you need to install "pico2wave" as root:
⋅⋅⋅wget http://archive.raspberrypi.org/debian/pool/main/s/svox/libttspico-utils_1.0+git20130326-3+rpi1_armhf.deb
⋅⋅⋅wget http://archive.raspberrypi.org/debian/pool/main/s/svox/libttspico0_1.0+git20130326-3+rpi1_armhf.deb
⋅⋅⋅apt-get install -f ./libttspico0_1.0+git20130326-3+rpi1_armhf.deb ./libttspico-utils_1.0+git20130326-3+rpi1_armhf.deb
⋅⋅⋅# test:
⋅⋅⋅pico2wave -w lookdave.wav "Look Dave, I can see you're really upset about this." && aplay lookdave.wav
-with device https://www.raspiaudio.com/promo you can use the yellow button to shutdown your raspberry-pi. read sound/shutdown_button.py for help
"""

    def __init__(self):
        logging.debug("Pwnspeak plugin created")
        engine.say("Pwnspeak plugin created")
        engine.runAndWait()
        engine.stop()

    # called when http://<host>:<port>/plugins/<plugin>/ is called
    # must return a html page
    # IMPORTANT: If you use "POST"s, add a csrf-token (via csrf_token() and render_template_string)
    def on_webhook(self, path, request):
        engine.say("Webhook clicked!")
        engine.runAndWait()
        engine.stop()
        pass

    # called when the plugin is loaded
    def on_loaded(self):
        logging.debug("Pwnspeak plugin loaded")
        engine.say("Pwnspeak plugin loaded")
        engine.runAndWait()
        engine.stop()
        pass

    # called before the plugin is unloaded
    def on_unload(self, ui):
        logging.debug("Pwnspeak plugin unloaded")
        engine.say("Pwnspeak plugin unloaded")
        engine.runAndWait()
        engine.stop()
        pass

    # called hen there's internet connectivity
    def on_internet_available(self, agent):
        logging.debug("I now have internet.")
        engine.say("I have detected a internet connection")
        engine.runAndWait()
        engine.stop()
        pass

    # called to setup the ui elements
    def on_ui_setup(self, ui):
        # add custom UI elements
        logging.debug("Setting up UI elements")
        engine.say("Setting up UI elements")
        engine.runAndWait()
        engine.stop()
        # ui.add_element('ups', LabeledValue(color=BLACK, label='UPS', value='0%/0V', position=(ui.width() / 2 - 25, 0), label_font=fonts.Bold, text_font=fonts.Medium))
        pass

    # called when the ui is updated
    def on_ui_update(self, ui):
        # update those elements
        # logging.debug("The UI is updated")
        # engine.say("The UI updated")
        # engine.runAndWait()
        # engine.stop()
        # some_voltage = 0.1
        # some_capacity = 100.0
        # ui.set('ups', "%4.2fV/%2i%%" % (some_voltage, some_capacity))
        pass

    # called when the hardware display setup is done, display is an hardware specific object
    def on_display_setup(self, display):
        # logging.debug("Pwnspeak plugin created")
        # engine.say("Pwnspeak plugin created")
        # engine.runAndWait()
        # engine.stop()
        pass

    # called when everything is ready and the main loop is about to start
    def on_ready(self, agent):
        logging.info("unit is ready!")
        engine.say("The unit is ready!")
        engine.runAndWait()
        engine.stop()

        # you can run custom bettercap commands if you want
        #   agent.run('ble.recon on')
        # or set a custom state
        #   agent.set_bored()
        pass

    # called when the AI finished loading
    def on_ai_ready(self, agent):
        logging.debug("The AI is finished loading")
        engine.say("My AI is finished loading, I now have become sentient!")
        engine.runAndWait()
        engine.stop()
        pass

    # called when the AI finds a new set of parameters
    def on_ai_policy(self, agent, policy):
        logging.debug("I have found a new set of parameters.")
        engine.say("I have found a new set of parameters.")
        engine.runAndWait()
        engine.stop()
        pass

    # called when the AI starts training for a given number of epochs
    def on_ai_training_start(self, agent, epochs):
        logging.debug("The AI has started training.")
        engine.say("I have started training.")
        engine.runAndWait()
        engine.stop()
        pass

    # called after the AI completed a training epoch
    def on_ai_training_step(self, agent, _locals, _globals):
        logging.debug("The AI has completed training for an epoch.")
        engine.say("I have completed my training for the last epoch.")
        engine.runAndWait()
        engine.stop()
        pass

    # called when the AI has done training
    def on_ai_training_end(self, agent):
        logging.debug("The AI is done with training.")
        engine.say("I have finished my training.")
        engine.runAndWait()
        engine.stop()
        pass

    # called when the AI got the best reward so far
    def on_ai_best_reward(self, agent, reward):
        logging.debug("The AI just got its best reward so far.")
        engine.say("I just got my best reward so far, this is my best day ever!")
        engine.runAndWait()
        engine.stop()
        pass

    # called when the AI got the worst reward so far
    def on_ai_worst_reward(self, agent, reward):
        logging.debug("The AI just got its worst reward so far.")
        engine.say("I just got the worst reward so far, my life sucks!")
        engine.runAndWait()
        engine.stop()
        pass

    # called when a non overlapping wifi channel is found to be free
    def on_free_channel(self, agent, channel):
        logging.debug("I just found a non overlapping wifi channel that is free.")
        engine.say("I just found a non overlapping wifi channel that is free.")
        engine.runAndWait()
        engine.stop()
        pass

    # called when the status is set to bored
    def on_bored(self, agent):
        logging.debug("I am so bored right now...")
        engine.say("I am so bored right now...")
        engine.runAndWait()
        engine.stop()
        pass

    # called when the status is set to sad
    def on_sad(self, agent):
        logging.debug("I am so sad...")
        engine.say("I am so sad...")
        engine.runAndWait()
        engine.stop()
        pass

    # called when the status is set to excited
    def on_excited(self, agent):
        logging.debug("I am so excited...")
        engine.say("I am so excited...")
        engine.runAndWait()
        engine.stop()
        pass

    # called when the status is set to lonely
    def on_lonely(self, agent):
        logging.debug("I am so loneley, nobody wants to play with me...")
        engine.say("I am so lonenly, nobody wants to play wiith me...")
        engine.runAndWait()
        engine.stop()
        pass

    # called when the agent is rebooting the board
    def on_rebooting(self, agent):
        logging.debug("I am going to reboot now.")
        engine.say("I am going to reboot now.")
        engine.runAndWait()
        engine.stop()
        pass

    # called when the agent is waiting for t seconds
    def on_wait(self, agent, t):
        logging.debug("Waiting for a few seconds...")
        engine.say("Waiting for a few seconds...")
        engine.runAndWait()
        engine.stop()
        pass

    # called when the agent is sleeping for t seconds
    def on_sleep(self, agent, t):
        logging.debug("Sleeping for a few seconds ...")
        engine.say("Sleeping for a few seconds...")
        engine.runAndWait()
        engine.stop()
        pass

    # called when the agent refreshed its access points list
    def on_wifi_update(self, agent, access_points):
        # logging.debug("I have refreshed my list of access points...")
        # engine.say("I have refreshed my list of access points...")
        # engine.runAndWait()
        # engine.stop()
        pass

    # called when the agent refreshed an unfiltered access point list
    # this list contains all access points that were detected BEFORE filtering
    def on_unfiltered_ap_list(self, agent, access_points):
        # logging.debug("I have refreshed my list of unfilteted access points...")
        # engine.say("I have refreshed my list of unfiltered access points...")
        # engine.runAndWait()
        # engine.stop()
        pass

    # called when the agent is sending an association frame
    def on_association(self, agent, access_point):
        logging.debug("I am sending an association frame now...")
        engine.say("I am sending an association frame now...")
        engine.runAndWait()
        engine.stop()
        pass

    # called when the agent is deauthenticating a client station from an AP
    def on_deauthentication(self, agent, access_point, client_station):
        engine.say("I am deauthenticating a client from its access point...")
        engine.runAndWait()
        engine.stop()
        pass

    # callend when the agent is tuning on a specific channel
    def on_channel_hop(self, agent, channel):
        # engine.say("I am running on channel C...")
        # engine.runAndWait()
        # engine.stop()
        pass

    # called when a new handshake is captured, access_point and client_station are json objects
    # if the agent could match the BSSIDs to the current list, otherwise they are just the strings of the BSSIDs
    def on_handshake(self, agent, filename, access_point, client_station):
        engine.say("I have captured a handshake...")
        engine.runAndWait()
        engine.stop()
        pass

    # called when an epoch is over (where an epoch is a single loop of the main algorithm)
    def on_epoch(self, agent, epoch, epoch_data):
        engine.say("I have completed a whole epoch...")
        engine.runAndWait()
        engine.stop()
        pass

    # called when a new peer is detected
    def on_peer_detected(self, agent, peer):
        engine.say("I have found a new peer...")
        engine.runAndWait()
        engine.stop()
        pass

    # called when a known peer is lost
    def on_peer_lost(self, agent, peer):
        engine.say("I have lost contact with a peer...")
        engine.runAndWait()
        engine.stop()
        pass
