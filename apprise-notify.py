import logging
import os
import apprise
import pwnagotchi.plugins as plugins
from pwnagotchi.ui.components import LabeledValue
from pwnagotchi.ui.view import BLACK
import pwnagotchi.ui.fonts as fonts

apobj = apprise.Apprise()

# Create an Config instance
config = apprise.AppriseConfig()

# Add a configuration source:
config.add('/home/pi/pwnagotchi-control-center/pwnagotchi-plugins/apprise-config.yml')

# Add another...
#config.add('https://myserver:8080/path/to/config')

# Make sure to add our config into our apprise object
apobj.add(config)

# You can mix and match; add an entry directly if you want too
# In this entry we associate the 'admin' tag with our notification
# apobj.add('mailto://bauke.molenaar:mypass@gmail.com', tag='admin')

# Then notify these services any time you desire. The below would
# notify all of the services that have not been bound to any specific
# tag.
# apobj.notify(
#     body='what a great notification service!',
#     title='my notification title',
# )


picture = '/var/tmp/pwnagotchi/pwnagotchi.png' if os.path.exists("/var/tmp/pwnagotchi/pwnagotchi.png") else '/root/pwnagotchi.png'
#outputfilepath = '/tmp/' + short + '.wav' if os.path.exists('/tmp/' + short + '.wav') else '/tmp/output.wav' if os.path.exists('/tmp/' + short + '.wav') else '/tmp/output.wav'

class Apprise(plugins.Plugin):
    __author__ = 'bauke.molenaar@gmail.com'
    __version__ = '1.0.0'
    __license__ = 'GPL3'
    __description__ = 'An Apprise plugin for pwnagotchi that implements all the available callbacks.'
    __name__ = 'Apprise'
    __help__ = """
    An Apprise plugin for pwnagotchi that implements all the available callbacks.
    """
    __dependencies__ = {
        'pip': ['apprise'],
    }
    __defaults__ = {
        'enabled': False,
        'face': '(>.<)',
    }

    def __init__(self):
        self.text_to_set = ""
        title = ("[apprise]")
        short = ("__init__")
        body = ("They are often well hidden from plain sight! but not this one, hah!")
        logging.debug(title + " " + short + " " + body)
        apobj.notify(
            title=title,
            body=body,
            attach=picture,
        )
        outputfilepath = '/tmp/' + short + '.wav' if os.path.exists('/tmp/' + short + '.wav') else '/tmp/output.wav'
        apobj.notify(
            title=title,
            body=body,
            attach=outputfilepath,
        )

    # called when the config is updated
    def on_config_changed(self, config):
        self.config = config
        self.ready = True

    # called when the ui is updated
    def on_ui_update(self, ui):
        title = ("[apprise]")
        short = ("on_ui_update")
        body = ("The UI is updated")
        logging.debug(title + " " + short + " " + body)
        apobj.notify(
            title=title,
            body=body,
            attach=picture,
        )
        outputfilepath = '/tmp/' + short + '.wav' if os.path.exists('/tmp/' + short + '.wav') else '/tmp/output.wav'
        apobj.notify(
            title=title,
            body=body,
            attach=outputfilepath,
        )

    # called when http://<host>:<port>/plugins/<plugin>/ is called
    # must return a html page
    # IMPORTANT: If you use "POST"s, add a csrf-token (via csrf_token() and render_template_string)
    def on_webhook(self, path, request):
        title = ("[apprise]")
        short = ("on_webhook")
        body = ("Webhook clicked! " + path + " " + request)
        logging.debug(title + " " + short + " " + body)
        apobj.notify(
            title=title,
            body=body,
            attach=picture,
        )
        outputfilepath = '/tmp/' + short + '.wav' if os.path.exists('/tmp/' + short + '.wav') else '/tmp/output.wav'
        apobj.notify(
            title=title,
            body=body,
            attach=outputfilepath,
        )

    # called when the plugin is loaded
    def on_loaded(self):
        title = ("[apprise]")
        short = ("on_loaded")
        body = ("plugin loaded")
        logging.debug(title + " " + short + " " + body)
        apobj.notify(
            title=title,
            body=body,
            attach=picture,
        )
        outputfilepath = '/tmp/' + short + '.wav' if os.path.exists('/tmp/' + short + '.wav') else '/tmp/output.wav'
        apobj.notify(
            title=title,
            body=body,
            attach=outputfilepath,
        )

    # called before the plugin is unloaded
    def on_unload(self, ui):
        title = ("[apprise]")
        short = ("on_unload")
        body = ("plugin unloaded")
        logging.debug(title + " " + short + " " + body)
        apobj.notify(
            title=title,
            body=body,
            attach=picture,
        )
        outputfilepath = '/tmp/' + short + '.wav' if os.path.exists('/tmp/' + short + '.wav') else '/tmp/output.wav'
        apobj.notify(
            title=title,
            body=body,
            attach=outputfilepath,
        )

    # called hen there's internet connectivity
    def on_internet_available(self, agent):
        title = ("[apprise]")
        short = ("on_internet_available")
        body = ("I now have internet.")
        logging.debug(title + " " + short + " " + body)
        apobj.notify(
            title=title,
            body=body,
            attach=picture,
        )
        outputfilepath = '/tmp/' + short + '.wav' if os.path.exists('/tmp/' + short + '.wav') else '/tmp/output.wav'
        apobj.notify(
            title=title,
            body=body,
            attach=outputfilepath,
        )

    # called to setup the ui elements
    def on_ui_setup(self, ui):
        # add custom UI elements
        title = ("[apprise]")
        short = ("on_ui_setup")
        body = ("Setting up UI elements")
        logging.debug(title + " " + short + " " + body)
        apobj.notify(
            title=title,
            body=body,
            attach=picture,
        )
        outputfilepath = '/tmp/' + short + '.wav' if os.path.exists('/tmp/' + short + '.wav') else '/tmp/output.wav'
        apobj.notify(
            title=title,
            body=body,
            attach=outputfilepath,
        )

    # called when the hardware display setup is done, display is an hardware specific object
    def on_display_setup(self, display):
        title = ("[apprise]")
        short = ("on_display_setup")
        body = ("plugin created")
        logging.debug(title + " " + short + " " + body)
        apobj.notify(
            title=title,
            body=body,
            attach=picture,
        )
        outputfilepath = '/tmp/' + short + '.wav' if os.path.exists('/tmp/' + short + '.wav') else '/tmp/output.wav'
        apobj.notify(
            title=title,
            body=body,
            attach=outputfilepath,
        )

    # called when everything is ready and the main loop is about to start
    def on_ready(self, agent):
        title = ("[apprise]")
        short = ("on_ready")
        body = ("unit is ready!")
        logging.debug(title + " " + short + " " + body)
        apobj.notify(
            title=title,
            body=body,
            attach=picture,
        )
        outputfilepath = '/tmp/' + short + '.wav' if os.path.exists('/tmp/' + short + '.wav') else '/tmp/output.wav'
        apobj.notify(
            title=title,
            body=body,
            attach=outputfilepath,
        )

    # called when the AI finished loading
    def on_ai_ready(self, agent):
        title = ("[apprise]")
        short = ("on_ai_ready")
        body = ("The AI is finished loading")
        logging.debug(title + " " + short + " " + body)
        apobj.notify(
            title=title,
            body=body,
            attach=picture,
        )
        outputfilepath = '/tmp/' + short + '.wav' if os.path.exists('/tmp/' + short + '.wav') else '/tmp/output.wav'
        apobj.notify(
            title=title,
            body=body,
            attach=outputfilepath,
        )

    # called when the AI finds a new set of parameters
    def on_ai_policy(self, agent, policy):
        title = ("[apprise]")
        short = ("on_ai_policy")
        body = ("I have found a new set of parameters. Policy: " + policy)
        logging.debug(title + " " + short + " " + body)
        apobj.notify(
            title=title,
            body=body,
            attach=picture,
        )
        outputfilepath = '/tmp/' + short + '.wav' if os.path.exists('/tmp/' + short + '.wav') else '/tmp/output.wav'
        apobj.notify(
            title=title,
            body=body,
            attach=outputfilepath,
        )

    # called when the AI starts training for a given number of epochs
    def on_ai_training_start(self, agent, epochs):
        title = ("[apprise]")
        short = ("on_ai_training_start")
        body = ("The AI has started training. Epochs: " + epochs)
        logging.debug(title + " " + short + " " + body)
        apobj.notify(
            title=title,
            body=body,
            attach=picture,
        )
        outputfilepath = '/tmp/' + short + '.wav' if os.path.exists('/tmp/' + short + '.wav') else '/tmp/output.wav'
        apobj.notify(
            title=title,
            body=body,
            attach=outputfilepath,
        )

    # called after the AI completed a training epoch
    def on_ai_training_step(self, agent, _locals, _globals):
        title = ("[apprise]")
        short = ("on_ai_training_step")
        body = ("The AI has completed training for an epoch.")
        logging.debug(title + " " + short + " " + body)
        apobj.notify(
            title=title,
            body=body,
            attach=picture,
        )
        outputfilepath = '/tmp/' + short + '.wav' if os.path.exists('/tmp/' + short + '.wav') else '/tmp/output.wav'
        apobj.notify(
            title=title,
            body=body,
            attach=outputfilepath,
        )

    # called when there are unread messages
    def on_unread_messages(self, count, total, agent, unread_messages, total_messages):
        s = 's' if count > 1 else ''
        title = ("[apprise]")
        short = ("on_unread_messages")
        body = ('You have {count} new message{plural}!').format(count=count, plural=s)
        logging.debug(title + " " + short + " " + body)
        apobj.notify(
            title=title,
            body=body,
            attach=picture,
        )
        outputfilepath = '/tmp/' + short + '.wav' if os.path.exists('/tmp/' + short + '.wav') else '/tmp/output.wav'
        apobj.notify(
            title=title,
            body=body,
            attach=outputfilepath,
        )

    # called when the AI has done training
    def on_ai_training_end(self, agent):
        title = ("[apprise]")
        short = ("on_ai_training_end")
        body = ("The AI is done with training.")
        logging.debug(title + " " + short + " " + body)
        apobj.notify(
            title=title,
            body=body,
            attach=picture,
        )
        outputfilepath = '/tmp/' + short + '.wav' if os.path.exists('/tmp/' + short + '.wav') else '/tmp/output.wav'
        apobj.notify(
            title=title,
            body=body,
            attach=outputfilepath,
        )

    # called when the AI got the best reward so far
    def on_ai_best_reward(self, agent, reward):
        title = ("[apprise]")
        short = ("on_ai_best_reward")
        body = ("The AI just got its best reward so far. Reward: " + reward)
        logging.debug(title + " " + short + " " + body)
        apobj.notify(
            title=title,
            body=body,
            attach=picture,
        )
        outputfilepath = '/tmp/' + short + '.wav' if os.path.exists('/tmp/' + short + '.wav') else '/tmp/output.wav'
        apobj.notify(
            title=title,
            body=body,
            attach=outputfilepath,
        )

    # called when the AI got the worst reward so far
    def on_ai_worst_reward(self, agent, reward):
        title = ("[apprise]")
        short = ("on_ai_worst_reward")
        body = ("The AI just got its worst reward so far. Reward: " + reward)
        logging.debug(title + " " + short + " " + body)
        apobj.notify(
            title=title,
            body=body,
            attach=picture,
        )
        outputfilepath = '/tmp/' + short + '.wav' if os.path.exists('/tmp/' + short + '.wav') else '/tmp/output.wav'
        apobj.notify(
            title=title,
            body=body,
            attach=outputfilepath,
        )

    # called when a non overlapping wifi channel is found to be free
    def on_free_channel(self, agent, channel):
        title = ("[apprise]")
        short = ("on_free_channel")
        body = ("I just found a non overlapping wifi channel: " + channel + " that is free.")
        logging.debug(title + " " + short + " " + body)
        apobj.notify(
            title=title,
            body=body,
            attach=picture,
        )
        outputfilepath = '/tmp/' + short + '.wav' if os.path.exists('/tmp/' + short + '.wav') else '/tmp/output.wav'
        apobj.notify(
            title=title,
            body=body,
            attach=outputfilepath,
        )

    # called when the status is set to bored
    def on_bored(self, agent):
        title = ("[apprise]")
        short = ("on_bored")
        body = ("I am so bored right now...")
        logging.debug(title + " " + short + " " + body)
        apobj.notify(
            title=title,
            body=body,
            attach=picture,
        )
        outputfilepath = '/tmp/' + short + '.wav' if os.path.exists('/tmp/' + short + '.wav') else '/tmp/output.wav'
        apobj.notify(
            title=title,
            body=body,
            attach=outputfilepath,
        )

    # called when the status is set to sad
    def on_sad(self, agent):
        title = ("[apprise]")
        short = ("on_sad")
        body = ("I am so sad...")
        logging.debug(title + " " + short + " " + body)
        apobj.notify(
            title=title,
            body=body,
            attach=picture,
        )
        outputfilepath = '/tmp/' + short + '.wav' if os.path.exists('/tmp/' + short + '.wav') else '/tmp/output.wav'
        apobj.notify(
            title=title,
            body=body,
            attach=outputfilepath,
        )

    # called when the status is set to excited
    def on_excited(self, agent):
        title = ("[apprise]")
        short = ("on_excited")
        body = ("I am so excited...")
        logging.debug(title + " " + short + " " + body)
        apobj.notify(
            title=title,
            body=body,
            attach=picture,
        )
        outputfilepath = '/tmp/' + short + '.wav' if os.path.exists('/tmp/' + short + '.wav') else '/tmp/output.wav'
        apobj.notify(
            title=title,
            body=body,
            attach=outputfilepath,
        )

    # called when the status is set to lonely
    def on_lonely(self, agent):
        title = ("[apprise]")
        short = ("on_lonely")
        body = ("I am so loneley, nobody wants to play with me...")
        logging.debug(title + " " + short + " " + body)
        apobj.notify(
            title=title,
            body=body,
            attach=picture,
        )
        outputfilepath = '/tmp/' + short + '.wav' if os.path.exists('/tmp/' + short + '.wav') else '/tmp/output.wav'
        apobj.notify(
            title=title,
            body=body,
            attach=outputfilepath,
        )

    # called when the agent is rebooting the board
    def on_rebooting(self, agent):
        title = ("[apprise]")
        short = ("on_rebooting")
        body = ("I am going to reboot now.")
        logging.debug(title + " " + short + " " + body)
        apobj.notify(
            title=title,
            body=body,
            attach=picture,
        )
        outputfilepath = '/tmp/' + short + '.wav' if os.path.exists('/tmp/' + short + '.wav') else '/tmp/output.wav'
        apobj.notify(
            title=title,
            body=body,
            attach=outputfilepath,
        )

    # called when the agent is waiting for t seconds
    def on_wait(self, agent, t):
        title = ("[apprise]")
        short = ("on_wait")
        body = ("Waiting for " + t + " seconds...")
        logging.debug(title + " " + short + " " + body)
        apobj.notify(
            title=title,
            body=body,
            attach=picture,
        )
        outputfilepath = '/tmp/' + short + '.wav' if os.path.exists('/tmp/' + short + '.wav') else '/tmp/output.wav'
        apobj.notify(
            title=title,
            body=body,
            attach=outputfilepath,
        )

    # called when the agent is sleeping for t seconds
    def on_sleep(self, agent, t):
        title = ("[apprise]")
        short = ("on_sleep")
        body = ("Sleeping for " + t + " seconds ...")
        logging.debug(title + " " + short + " " + body)
        apobj.notify(
            title=title,
            body=body,
            attach=picture,
        )
        outputfilepath = '/tmp/' + short + '.wav' if os.path.exists('/tmp/' + short + '.wav') else '/tmp/output.wav'
        apobj.notify(
            title=title,
            body=body,
            attach=outputfilepath,
        )

    # called when the agent refreshed its access points list
    def on_wifi_update(self, agent, access_points):
        title = ("[apprise]")
        short = ("on_wifi_update")
        body = ("I have refreshed my list of access points. Access points: " + access_points)
        logging.debug(title + " " + short + " " + body)
        apobj.notify(
            title=title,
            body=body,
            attach=picture,
        )
        outputfilepath = '/tmp/' + short + '.wav' if os.path.exists('/tmp/' + short + '.wav') else '/tmp/output.wav'
        apobj.notify(
            title=title,
            body=body,
            attach=outputfilepath,
        )

    # called when the agent refreshed an unfiltered access point list
    # this list contains all access points that were detected BEFORE filtering
    def on_unfiltered_ap_list(self, agent, access_points):
        title = ("[apprise]")
        short = ("on_unfiltered_ap_list")
        body = ("I have refreshed my list of unfilteted access points. Access points: " + access_points)
        logging.debug(title + " " + short + " " + body)
        apobj.notify(
            title=title,
            body=body,
            attach=picture,
        )
        outputfilepath = '/tmp/' + short + '.wav' if os.path.exists('/tmp/' + short + '.wav') else '/tmp/output.wav'
        apobj.notify(
            title=title,
            body=body,
            attach=outputfilepath,
        )

    # called when the agent is sending an association frame
    def on_association(self, agent, access_point):
        title = ("[apprise]")
        short = ("on_association")
        body = ("I am sending " + access_point + " an association frame now.")
        logging.debug(title + " " + short + " " + body)
        apobj.notify(
            title=title,
            body=body,
            attach=picture,
        )
        outputfilepath = '/tmp/' + short + '.wav' if os.path.exists('/tmp/' + short + '.wav') else '/tmp/output.wav'
        apobj.notify(
            title=title,
            body=body,
            attach=outputfilepath,
        )

    # called when the agent is deauthenticating a client station from an AP
    def on_deauthentication(self, agent, access_point, client_station):
        title = ("[apprise]")
        short = ("on_deauthentication")
        body = ("I am deauthenticating " + client_station + "from " + access_point)
        logging.debug(title + " " + short + " " + body)
        apobj.notify(
            title=title,
            body=body,
            attach=picture,
        )
        outputfilepath = '/tmp/' + short + '.wav' if os.path.exists('/tmp/' + short + '.wav') else '/tmp/output.wav'
        apobj.notify(
            title=title,
            body=body,
            attach=outputfilepath,
        )

    # called when the agent is tuning on a specific channel
    def on_channel_hop(self, agent, channel):
        title = ("[apprise]")
        short = ("on_channel_hop")
        body = ("I am running on " + channel)
        logging.debug(title + " " + short + " " + body)
        apobj.notify(
            title=title,
            body=body,
            attach=picture,
        )
        outputfilepath = '/tmp/' + short + '.wav' if os.path.exists('/tmp/' + short + '.wav') else '/tmp/output.wav'
        apobj.notify(
            title=title,
            body=body,
            attach=outputfilepath,
        )

    # called when a new handshake is captured, access_point and client_station are json objects
    # if the agent could match the BSSIDs to the current list, otherwise they are just the strings of the BSSIDs
    def on_handshake(self, agent, filename, access_point, client_station):
        title = ("[apprise]")
        short = ("on_handshake")
        body = ("I have captured a handshake. \nFilename: " + filename + "\nClient station: " + client_station + "\nAccess point: " + access_point)
        logging.debug(title + " " + short + " " + body)
        apobj.notify(
            title=title,
            body=body,
            attach=picture,
        )
        outputfilepath = '/tmp/' + short + '.wav' if os.path.exists('/tmp/' + short + '.wav') else '/tmp/output.wav'
        apobj.notify(
            title=title,
            body=body,
            attach=outputfilepath,
        )

    # called when an epoch is over (where an epoch is a single loop of the main algorithm)
    def on_epoch(self, agent, epoch, epoch_data):
        title = ("[apprise]")
        short = ("on_epoch")
        body = ("I have completed a whole epoch. \nEpoch: " + epoch + "\nEpoch data: " + epoch_data)
        logging.debug(title + " " + short + " " + body)
        apobj.notify(
            title=title,
            body=body,
            attach=picture,
        )
        outputfilepath = '/tmp/' + short + '.wav' if os.path.exists('/tmp/' + short + '.wav') else '/tmp/output.wav'
        apobj.notify(
            title=title,
            body=body,
            attach=outputfilepath,
        )

    # called when a new peer is detected
    def on_peer_detected(self, agent, peer):
        title = ("[apprise]")
        short = ("on_peer_detected")
        body = ("I have found a new peer. \nPeer: " + peer)
        logging.debug(title + " " + short + " " + body)
        apobj.notify(
            title=title,
            body=body,
            attach=picture,
        )
        outputfilepath = '/tmp/' + short + '.wav' if os.path.exists('/tmp/' + short + '.wav') else '/tmp/output.wav'
        apobj.notify(
            title=title,
            body=body,
            attach=outputfilepath,
        )

    # called when a known peer is lost
    def on_peer_lost(self, agent, peer):
        title = ("[apprise]")
        short = ("on_peer_lost")
        body = ("I have lost contact with a peer. \nPeer: " + peer)
        logging.debug(title + " " + short + " " + body)
        apobj.notify(
            title=title,
            body=body,
            attach=picture,
        )
        outputfilepath = '/tmp/' + short + '.wav' if os.path.exists('/tmp/' + short + '.wav') else '/tmp/output.wav'
        apobj.notify(
            title=title,
            body=body,
            attach=outputfilepath,
        )

    # called when a password is cracked
    def on_cracked(self, agent, access_point):
        title = ("[apprise]")
        short = ("on_cracked")
        body = ("I have cracked the password for: " + access_point)
        logging.debug(title + " " + short + " " + body)
        apobj.notify(
            title=title,
            body=body,
            attach=picture,
        )
        outputfilepath = '/tmp/' + short + '.wav' if os.path.exists('/tmp/' + short + '.wav') else '/tmp/output.wav'
        apobj.notify(
            title=title,
            body=body,
            attach=outputfilepath,
        )
