import logging
import os, subprocess
import pyttsx3
from pwnagotchi import plugins
from pwnagotchi.ui.components import LabeledValue
from pwnagotchi.ui.view import BLACK
import pwnagotchi.ui.fonts as fonts

# object creation
engine = pyttsx3.init()

# getting details of current speaking rate
rate = engine.getProperty('rate')
# setting up new voice rate
#engine.setProperty('rate', 125)

#getting to know current volume level (min=0 and max=1)
volume = engine.getProperty('volume')
# setting up volume level  between 0 and 1
#engine.setProperty('volume',1.0)

#getting details of current voice
voices = engine.getProperty('voices')
#changing index, changes voices. o for male
#engine.setProperty('voice', voices[0].id)
#changing index, changes voices. 1 for female
#engine.setProperty('voice', voices[1].id)

class Pwnspeak(plugins.Plugin):
    __author__ = 'bauke.molenaar@gmail.com'
    __version__ = '1.0.0'
    __license__ = 'GPL3'
    __description__ = 'An Pwnspeak plugin for pwnagotchi that implements all the available callbacks.'
    __name__ = 'Pwnspeak'
    __help__ = (
                "this plugin needs a installed and working audio DAC HAT, USB-Soundcard or a connected bt-headset/headphone for audio output, like https://www.raspiaudio.com/"
                "for enable text2speech on raspberry-pi-zero with debian buster to speak the SSID on handshake and others, you need to install 'pico2wave' as root:"
                "wget http://archive.raspberrypi.org/debian/pool/main/s/svox/libttspico-utils_1.0+git20130326-3+rpi1_armhf.deb"
                "wget http://archive.raspberrypi.org/debian/pool/main/s/svox/libttspico0_1.0+git20130326-3+rpi1_armhf.deb"
                "sudo apt install -f ./libttspico0_1.0+git20130326-3+rpi1_armhf.deb ./libttspico-utils_1.0+git20130326-3+rpi1_armhf.deb"
                "# test:"
                "pico2wave -w lookdave.wav 'Look Dave, I can see you´re really upset about this.' && aplay lookdave.wav"
                "with device https://www.raspiaudio.com/promo you can use the yellow button to shutdown your raspberry-pi. read sound/shutdown_button.py for help"
                )
    __dependencies__ = {
        'pip': ['scapy'],
    }
    __defaults__ = {
        'enabled': False,
    }

    def __init__(self):
        title = ("[pwnspeaker]")
        body = ("plugin created")
        outputfile = ("/tmp/output.wav")

        logging.info(title + " " + body)
        engine.say(body)
        engine.runAndWait()
        engine.stop()
        subprocess.run(["pico2wave", "-w", outputfile, body])
        subprocess.run(["aplay", outputfile])

    # called when http://<host>:<port>/plugins/<plugin>/ is called
    # must return a html page
    # IMPORTANT: If you use "POST"s, add a csrf-token (via csrf_token() and render_template_string)
    def on_webhook(self, path, request):
        title = ("[pwnspeaker]")
        body = ("Webhook clicked!")
        outputfile = ("/tmp/output.wav")

        logging.info(title + " " + body)
        engine.say(body)
        engine.runAndWait()
        engine.stop()
        subprocess.run(["pico2wave", "-w", outputfile, body])
        subprocess.run(["aplay", outputfile])

    # called when the plugin is loaded
    def on_loaded(self):
        title = ("[pwnspeaker]")
        body = ("plugin loaded")
        outputfile = ("/tmp/output.wav")

        logging.info(title + " " + body)
        engine.say(body)
        engine.runAndWait()
        engine.stop()
        subprocess.run(["pico2wave", "-w", outputfile, body])
        subprocess.run(["aplay", outputfile])

    # called before the plugin is unloaded
    def on_unload(self, ui):
        title = ("[pwnspeaker]")
        body = ("plugin unloaded")
        outputfile = ("/tmp/output.wav")

        logging.info(title + " " + body)
        engine.say(body)
        engine.runAndWait()
        engine.stop()
        subprocess.run(["pico2wave", "-w", outputfile, body])
        subprocess.run(["aplay", outputfile])

    # called hen there's internet connectivity
    def on_internet_available(self, agent):
        title = ("[pwnspeaker]")
        body = ("I now have internet.")
        outputfile = ("/tmp/output.wav")

        logging.info(title + " " + body)
        engine.say(body)
        engine.runAndWait()
        engine.stop()
        subprocess.run(["pico2wave", "-w", outputfile, body])
        subprocess.run(["aplay", outputfile])

    # called to setup the ui elements
    def on_ui_setup(self, ui):
        title = ("[pwnspeaker]")
        body = ("Setting up UI elements")
        outputfile = ("/tmp/output.wav")

        logging.info(title + " " + body)
        engine.say(body)
        engine.runAndWait()
        engine.stop()
        #ui.add_element('ups', LabeledValue(color=BLACK, label='UPS', value='0%/0V', position=(ui.width() / 2 - 25, 0), label_font=fonts.Bold, text_font=fonts.Medium))
        subprocess.run(["pico2wave", "-w", outputfile, body])
        subprocess.run(["aplay", outputfile])

    # called when the ui is updated
    def on_ui_update(self, ui):
        # title = ("[pwnspeaker]")
        # body = ("The UI is updated")
        # outputfile = ("/tmp/output.wav")

        # logging.info(title + " " + body)
        # engine.say(body)
        # engine.runAndWait()
        # engine.stop()
        # some_voltage = 0.1
        # some_capacity = 100.0
        # ui.set('ups', "%4.2fV/%2i%%" % (some_voltage, some_capacity))
        # subprocess.run(["pico2wave", "-w", outputfile, body])
        # subprocess.run(["aplay", outputfile])
        pass

    # called when the hardware display setup is done, display is an hardware specific object
    def on_display_setup(self, display):
        title = ("[pwnspeaker]")
        body = ("Pwnspeak plugin created")
        outputfile = ("/tmp/output.wav")

        logging.info(title + " " + body)
        engine.say(body)
        engine.runAndWait()
        engine.stop()
        subprocess.run(["pico2wave", "-w", outputfile, body])
        subprocess.run(["aplay", outputfile])

    # called when everything is ready and the main loop is about to start
    def on_ready(self, agent):
        title = ("[pwnspeaker]")
        body = ("The unit is ready!")
        outputfile = ("/tmp/output.wav")

        logging.info(title + " " + body)
        engine.say(body)
        engine.runAndWait()
        engine.stop()
        subprocess.run(["pico2wave", "-w", outputfile, body])
        subprocess.run(["aplay", outputfile])

        # you can run custom bettercap commands if you want
        #   agent.run('ble.recon on')
        # or set a custom state
        #   agent.set_bored()

    # called when the AI finished loading
    def on_ai_ready(self, agent):
        title = ("[pwnspeaker]")
        body = ("My AI is finished loading, I now have become sentient!")
        outputfile = ("/tmp/output.wav")

        logging.info(title + " " + body)
        engine.say(body)
        engine.runAndWait()
        engine.stop()
        subprocess.run(["pico2wave", "-w", outputfile, body])
        subprocess.run(["aplay", outputfile])

    # called when the AI finds a new set of parameters
    def on_ai_policy(self, agent, policy):
        title = ("[pwnspeaker]")
        body = ("I have found a new set of parameters. " + policy)
        outputfile = ("/tmp/output.wav")

        logging.info(title + " " + body)
        engine.say(body)
        engine.runAndWait()
        engine.stop()
        subprocess.run(["pico2wave", "-w", outputfile, body])
        subprocess.run(["aplay", outputfile])

    # called when the AI starts training for a given number of epochs
    def on_ai_training_start(self, agent, epochs):
        title = ("[pwnspeaker]")
        body = ("The AI has started training for " + epochs + "epochs.")
        outputfile = ("/tmp/output.wav")

        logging.info(title + " " + body)
        engine.say(body)
        engine.runAndWait()
        engine.stop()
        subprocess.run(["pico2wave", "-w", outputfile, body])
        subprocess.run(["aplay", outputfile])

    # called after the AI completed a training epoch
    def on_ai_training_step(self, agent, _locals, _globals):
        title = ("[pwnspeaker]")
        body = ("The AI has completed training for an epoch." + _locals + _globals)
        outputfile = ("/tmp/output.wav")

        logging.info(title + " " + body)
        engine.say(body)
        engine.runAndWait()
        engine.stop()
        subprocess.run(["pico2wave", "-w", outputfile, body])
        subprocess.run(["aplay", outputfile])

    # called when the AI has done training
    def on_ai_training_end(self, agent):
        title = ("[pwnspeaker]")
        body = ("I have finished my training.")
        outputfile = ("/tmp/output.wav")

        logging.info(title + " " + body)
        engine.say(body)
        engine.runAndWait()
        engine.stop()
        subprocess.run(["pico2wave", "-w", outputfile, body])
        subprocess.run(["aplay", outputfile])

    # called when the AI got the best reward so far
    def on_ai_best_reward(self, agent, reward):
        title = ("[pwnspeaker]")
        body = ("I just got my best reward so far, this is my best day ever!" + reward)
        outputfile = ("/tmp/output.wav")

        logging.info(title + " " + body)
        engine.say(body)
        engine.runAndWait()
        engine.stop()
        subprocess.run(["pico2wave", "-w", outputfile, body])
        subprocess.run(["aplay", outputfile])

    # called when the AI got the worst reward so far
    def on_ai_worst_reward(self, agent, reward):
        title = ("[pwnspeaker]")
        body = ("I just got the worst reward so far, my life sucks!" + reward)
        outputfile = ("/tmp/output.wav")

        logging.info(title + " " + body)
        engine.say(body)
        engine.runAndWait()
        engine.stop()
        subprocess.run(["pico2wave", "-w", outputfile, body])
        subprocess.run(["aplay", outputfile])

    # called when a non overlapping wifi channel is found to be free
    def on_free_channel(self, agent, channel):
        title = ("[pwnspeaker]")
        body = ("I just found that channel " + channel + "is free.")
        outputfile = ("/tmp/output.wav")

        logging.info(title + " " + body)
        engine.say(body)
        engine.runAndWait()
        engine.stop()
        subprocess.run(["pico2wave", "-w", outputfile, body])
        subprocess.run(["aplay", outputfile])

    # called when the status is set to bored
    def on_bored(self, agent):
        title = ("[pwnspeaker]")
        body = ("I am so bored right now...")
        outputfile = ("/tmp/output.wav")

        logging.info(title + " " + body)
        engine.say(body)
        engine.runAndWait()
        engine.stop()
        subprocess.run(["pico2wave", "-w", outputfile, body])
        subprocess.run(["aplay", outputfile])

    # called when the status is set to sad
    def on_sad(self, agent):
        title = ("[pwnspeaker]")
        body = ("I am so sad...")
        outputfile = ("/tmp/output.wav")

        logging.info(title + " " + body)
        engine.say(body)
        engine.runAndWait()
        engine.stop()
        subprocess.run(["pico2wave", "-w", outputfile, body])
        subprocess.run(["aplay", outputfile])

    # called when the status is set to excited
    def on_excited(self, agent):
        title = ("[pwnspeaker]")
        body = ("I am so excited...")
        outputfile = ("/tmp/output.wav")

        logging.info(title + " " + body)
        engine.say(body)
        engine.runAndWait()
        engine.stop()
        subprocess.run(["pico2wave", "-w", outputfile, body])
        subprocess.run(["aplay", outputfile])

    # called when the status is set to lonely
    def on_lonely(self, agent):
        title = ("[pwnspeaker]")
        body = ("I am so loneley, nobody wants to play with me...")
        outputfile = ("/tmp/output.wav")

        logging.info(title + " " + body)
        engine.say(body)
        engine.runAndWait()
        engine.stop()
        subprocess.run(["pico2wave", "-w", outputfile, body])
        subprocess.run(["aplay", outputfile])

    # called when the agent is rebooting the board
    def on_rebooting(self, agent):
        title = ("[pwnspeaker]")
        body = ("I am going to reboot now.")
        outputfile = ("/tmp/output.wav")

        logging.info(title + " " + body)
        engine.say(body)
        engine.runAndWait()
        engine.stop()
        subprocess.run(["pico2wave", "-w", outputfile, body])
        subprocess.run(["aplay", outputfile])

    # called when the agent is waiting for t seconds
    def on_wait(self, agent, t):
        title = ("[pwnspeaker]")
        body = ("Waiting for " + t + "seconds...")
        outputfile = ("/tmp/output.wav")

        logging.info(title + " " + body)
        engine.say(body)
        engine.runAndWait()
        engine.stop()
        subprocess.run(["pico2wave", "-w", outputfile, body])
        subprocess.run(["aplay", outputfile])

    # called when the agent is sleeping for t seconds
    def on_sleep(self, agent, t):
        title = ("[pwnspeaker]")
        body = ("Sleeping for " + t + " seconds ...")
        outputfile = ("/tmp/output.wav")

        logging.info(title + " " + body)
        engine.say(body)
        engine.runAndWait()
        engine.stop()
        subprocess.run(["pico2wave", "-w", outputfile, body])
        subprocess.run(["aplay", outputfile])

    # called when the agent refreshed its access points list
    def on_wifi_update(self, agent, access_points):
        title = ("[pwnspeaker]")
        body = ("I have refreshed my list of access points: " + access_points)
        outputfile = ("/tmp/output.wav")

        logging.info(title + " " + body)
        engine.say(body)
        engine.runAndWait()
        engine.stop()
        subprocess.run(["pico2wave", "-w", outputfile, body])
        subprocess.run(["aplay", outputfile])

    # called when the agent refreshed an unfiltered access point list
    # this list contains all access points that were detected BEFORE filtering
    def on_unfiltered_ap_list(self, agent, access_points):
        title = ("[pwnspeaker]")
        body = ("I have refreshed my list of unfilteted access points: " + access_points)
        outputfile = ("/tmp/output.wav")

        logging.info(title + " " + body)
        engine.say(body)
        engine.runAndWait()
        engine.stop()
        subprocess.run(["pico2wave", "-w", outputfile, body])
        subprocess.run(["aplay", outputfile])

    # called when the agent is sending an association frame
    def on_association(self, agent, access_point):
        title = ("[pwnspeaker]")
        body = ("I am sending an association frame to: " + access_point)
        outputfile = ("/tmp/output.wav")

        logging.info(title + " " + body)
        engine.say(body)
        engine.runAndWait()
        engine.stop()
        subprocess.run(["pico2wave", "-w", outputfile, body])
        subprocess.run(["aplay", outputfile])

    # called when the agent is deauthenticating a client station from an AP
    def on_deauthentication(self, agent, access_point, client_station):
        title = ("[pwnspeaker]")
        body = ("I am deauthenticating" + client_station + "from" + access_point)
        outputfile = ("/tmp/output.wav")

        logging.info(title + " " + body)
        engine.say(body)
        engine.runAndWait()
        engine.stop()
        subprocess.run(["pico2wave", "-w", outputfile, body])
        subprocess.run(["aplay", outputfile])

    # callend when the agent is tuning on a specific channel
    def on_channel_hop(self, agent, channel):
        title = ("[pwnspeaker]")
        body = ("I am running on channel: " + channel)
        outputfile = ("/tmp/output.wav")

        logging.info(title + " " + body)
        engine.say(body)
        engine.runAndWait()
        engine.stop()
        subprocess.run(["pico2wave", "-w", outputfile, body])
        subprocess.run(["aplay", outputfile])

    # called when a new handshake is captured, access_point and client_station are json objects
    # if the agent could match the BSSIDs to the current list, otherwise they are just the strings of the BSSIDs
    def on_handshake(self, agent, filename, access_point, client_station):
        title = ("[pwnspeaker]")
        body = ("Handshake captured from" + client_station + "tryning to connect to" + access_point + "saved to" + filename)
        outputfile = ("/tmp/output.wav")

        logging.info(title + " " + body)
        engine.say(body)
        engine.runAndWait()
        engine.stop()
        subprocess.run(["pico2wave", "-w", outputfile, body])
        subprocess.run(["aplay", outputfile])

    # called when an epoch is over (where an epoch is a single loop of the main algorithm)
    def on_epoch(self, agent, epoch, epoch_data):
        title = ("[pwnspeaker]")
        body = ("I have completed epoch number: " + epoch + "with data: " + epoch_data)
        outputfile = ("/tmp/output.wav")

        logging.info(title + " " + body)
        engine.say(body)
        engine.runAndWait()
        engine.stop()
        subprocess.run(["pico2wave", "-w", outputfile, body])
        subprocess.run(["aplay", outputfile])

    # called when a new peer is detected
    def on_peer_detected(self, agent, peer):
        title = ("[pwnspeaker]")
        body = ("I have found a new peer:" + peer)
        outputfile = ("/tmp/output.wav")

        logging.info(title + " " + body)
        engine.say(body)
        engine.runAndWait()
        engine.stop()
        subprocess.run(["pico2wave", "-w", outputfile, body])
        subprocess.run(["aplay", outputfile])

    # called when a known peer is lost
    def on_peer_lost(self, agent, peer):
        title = ("[pwnspeaker]")
        body = ("I have lost contact with" + peer)
        outputfile = ("/tmp/output.wav")

        logging.info(title + " " + body)
        engine.say(body)
        engine.runAndWait()
        engine.stop()
        subprocess.run(["pico2wave", "-w", outputfile, body])
        subprocess.run(["aplay", outputfile])