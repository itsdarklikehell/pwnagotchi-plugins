import logging
import os
import apprise
import pwnagotchi.plugins as plugins
from pwnagotchi.ui.components import LabeledValue
from pwnagotchi.ui.view import BLACK
import pwnagotchi.ui.fonts as fonts


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
        'apt': ['wget', 'libttspico0', 'libttspico-utils'],
        'pip': ['apprise'],
    }
    __defaults__ = {
        'enabled': False,
        'face': '(>.<)',
    }

    def __init__(self):
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

        # Tagging allows you to specifically target only specific notification
        # services you've loaded:
        # apobj.notify(
        #     body='send a notification to our admin group',
        #     title='Attention Admins',
        #     # notify any services tagged with the 'admin' tag
        #     tag='admin',
        # )

        # If you want to notify absolutely everything (reguardless of whether
        # it's been tagged or not), just use the reserved tag of 'all':
        # apobj.notify(
        #     body='send a notification to our admin group',
        #     title='Attention Admins',
        #     # notify absolutely everything loaded, regardless on wether
        #     # it has a tag associated with it or not:
        #     tag='all',
        # )

        # Then send your attachment.
        apobj.notify(
            title='A rare photo of a pwnagotchi.',
            body='They are often well hidden from plain sight! but not this one, hah! :)',
            attach='/home/pi/pwnagotchi-splashscreen.png',
        )

        # Send a web based attachment too! In the below example, we connect to a home
        # security camera and send a live image to an email. By default remote web
        # content is cached but for a security camera, we might want to call notify
        # again later in our code so we want our last image retrieved to expire(in
        # this case after 3 seconds).
        # apobj.notify(
        #     title='Latest security image',
        #     attach='http:/admin:password@hikvision-cam01/ISAPI/Streaming/channels/101/picture?cache=3'
        # )

        # Now add all of the entries we're intrested in:
        # attach = (
        #     # ?name= allows us to rename the actual jpeg as found on the site
        #     # to be another name when sent to our receipient(s)
        #     'https://i.redd.it/my2t4d2fx0u31.jpg?name=FlyingToMars.jpg',

        #     # Now add another:
        #     '/path/to/funny/joke.gif',
        # )

        # # Send your multiple attachments with a single notify call:
        # apobj.notify(
        #     title='Some good jokes.',
        #     body='Hey guys, check out these!',
        #     attach=attach,
        # )

        self.text_to_set = ""
        title=("[apprise]")
        body=("plugin created")
        logging.info(title)
        logging.info(body)
        # Then send your attachment.
        apobj.notify(
            title=title,
            body=body,
            attach='/home/pi/pwnagotchi-splashscreen.png',
        )

    # called when http://<host>:<port>/plugins/<plugin>/ is called
    # must return a html page
    # IMPORTANT: If you use "POST"s, add a csrf-token (via csrf_token() and render_template_string)
    def on_webhook(self, path, request):
        title=("[apprise]")
        body=("Webhook clicked! " + path + " " + request)
        logging.info(title)
        logging.info(body)

    # called when the plugin is loaded
    def on_loaded(self):
        title=("[apprise]")
        body=("plugin loaded")
        logging.info(title)
        logging.info(body)

    # called before the plugin is unloaded
    def on_unload(self, ui):
        title=("[apprise]")
        body=("plugin unloaded")
        logging.info(title)
        logging.info(body)

    # called hen there's internet connectivity
    def on_internet_available(self, agent):
        title=("[apprise]")
        body=("I now have internet.")
        logging.info(title)
        logging.info(body)

    # called to setup the ui elements
    def on_ui_setup(self, ui):
        # add custom UI elements
        title=("[apprise]")
        body=("Setting up UI elements")
        logging.info(title)
        logging.info(body)

    # called when the ui is updated
    def on_ui_update(self, ui):
        title=("[apprise]")
        body=("The UI is updated")
        logging.info(title)
        logging.info(body)

    # called when the hardware display setup is done, display is an hardware specific object
    def on_display_setup(self, display):
        title=("[apprise]")
        body=("plugin created")
        logging.info(title)
        logging.info(body)

    # called when everything is ready and the main loop is about to start
    def on_ready(self, agent):
        title=("[apprise]")
        body=("unit is ready!")
        logging.info(title)
        logging.info(body)

    # called when the AI finished loading
    def on_ai_ready(self, agent):
        title=("[apprise]")
        body=("The AI is finished loading")
        logging.info(title)
        logging.info(body)


    # called when the AI finds a new set of parameters
    def on_ai_policy(self, agent, policy):
        title=("[apprise]")
        body=("I have found a new set of parameters. Policy: " + policy)
        logging.info(title)
        logging.info(body)

    # called when the AI starts training for a given number of epochs
    def on_ai_training_start(self, agent, epochs):
        title=("[apprise]")
        body=("The AI has started training. Epochs: " + epochs)
        logging.info(title)
        logging.info(body)

    # called after the AI completed a training epoch
    def on_ai_training_step(self, agent, _locals, _globals):
        title=("[apprise]")
        body=("The AI has completed training for an epoch.")
        logging.info(title)
        logging.info(body)

    # called when the AI has done training
    def on_ai_training_end(self, agent):
        title=("[apprise]")
        body=("The AI is done with training.")
        logging.info(title)
        logging.info(body)

    # called when the AI got the best reward so far
    def on_ai_best_reward(self, agent, reward):
        title=("[apprise]")
        body=("The AI just got its best reward so far. Reward: " + reward)
        logging.info(title)
        logging.info(body)

    # called when the AI got the worst reward so far
    def on_ai_worst_reward(self, agent, reward):
        title=("[apprise]")
        body=("The AI just got its worst reward so far. Reward: " + reward)
        logging.info(title)
        logging.info(body)

    # called when a non overlapping wifi channel is found to be free
    def on_free_channel(self, agent, channel):
        title=("[apprise]")
        body=("I just found a non overlapping wifi channel: " + channel + " that is free.")
        logging.info(title)
        logging.info(body)

    # called when the status is set to bored
    def on_bored(self, agent):
        title=("[apprise]")
        body=("I am so bored right now...")
        logging.info(title)
        logging.info(body)

    # called when the status is set to sad
    def on_sad(self, agent):
        title=("[apprise]")
        body=("I am so sad...")
        logging.info(title)
        logging.info(body)

    # called when the status is set to excited
    def on_excited(self, agent):
        title=("[apprise]")
        body=("I am so excited...")
        logging.info(title)
        logging.info(body)

    # called when the status is set to lonely
    def on_lonely(self, agent):
        title=("[apprise]")
        body=("I am so loneley, nobody wants to play with me...")
        logging.info(title)
        logging.info(body)

    # called when the agent is rebooting the board
    def on_rebooting(self, agent):
        title=("[apprise]")
        body=("I am going to reboot now.")
        logging.info(title)
        logging.info(body)

    # called when the agent is waiting for t seconds
    def on_wait(self, agent, t):
        title=("[apprise]")
        body=("Waiting for " + t + " seconds...")
        logging.info(title)
        logging.info(body)

    # called when the agent is sleeping for t seconds
    def on_sleep(self, agent, t):
        title=("[apprise]")
        body=("Sleeping for " + t + " seconds ...")
        logging.info(title)
        logging.info(body)

    # called when the agent refreshed its access points list
    def on_wifi_update(self, agent, access_points):
        title=("[apprise]")
        body=("I have refreshed my list of access points. Access points: " + access_points)
        logging.info(title)
        logging.info(body)

    # called when the agent refreshed an unfiltered access point list
    # this list contains all access points that were detected BEFORE filtering
    def on_unfiltered_ap_list(self, agent, access_points):
        title=("[apprise]")
        body=("I have refreshed my list of unfilteted access points. Access points: " + access_points)
        logging.info(title)
        logging.info(body)

    # called when the agent is sending an association frame
    def on_association(self, agent, access_point):
        title=("[apprise]")
        body=("I am sending " + access_point + " an association frame now.")
        logging.info(title)
        logging.info(body)

    # called when the agent is deauthenticating a client station from an AP
    def on_deauthentication(self, agent, access_point, client_station):
        title=("[apprise]")
        body=("I am deauthenticating " + client_station + "from " + access_point)
        logging.info(title)
        logging.info(body)

    # called when the agent is tuning on a specific channel
    def on_channel_hop(self, agent, channel):
        title=("[apprise]")
        body=("I am running on " + channel)
        logging.info(title)
        logging.info(body)

    # called when a new handshake is captured, access_point and client_station are json objects
    # if the agent could match the BSSIDs to the current list, otherwise they are just the strings of the BSSIDs
    def on_handshake(self, agent, filename, access_point, client_station):
        title=("[apprise]")
        body=("I have captured a handshake. \nFilename: " + filename + "\nClient station: " + client_station + "\nAccess point: " + access_point)
        logging.info(title)
        logging.info(body)
    # called when an epoch is over (where an epoch is a single loop of the main algorithm)
    def on_epoch(self, agent, epoch, epoch_data):
        title=("[apprise]")
        body=("I have completed a whole epoch. \nEpoch: " + epoch + "\nEpoch data: " + epoch_data)
        logging.info(title)
        logging.info(body)

    # called when a new peer is detected
    def on_peer_detected(self, agent, peer):
        title=("[apprise]")
        body=("I have found a new peer. \nPeer: " + peer)
        logging.info(title)
        logging.info(body)

    # called when a known peer is lost
    def on_peer_lost(self, agent, peer):
        title=("[apprise]")
        body=("I have lost contact with a peer. \nPeer: " + peer)
        logging.info(title)
        logging.info(body)
