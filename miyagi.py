import logging
import os
import html
import json

import pwnagotchi.plugins as plugins
from pwnagotchi.ui.components import LabeledValue
from pwnagotchi.ui.view import BLACK
import pwnagotchi.ui.fonts as fonts

from flask import abort
from flask import render_template_string


class Miyagi(plugins.Plugin):
    __author__ = "SgtStroopwafel, Sniffleupagus & MaliosDark"
    __version__ = "1.0.2"
    __license__ = "GPL3"
    __description__ = (
        "Manage AI training. Pwn on. Pwn off. (just kidding. always b pwn'in'!)"
    )
    __name__ = "Miyagi"
    __help__ = "Manage AI training. Pwn on. Pwn off. (just kidding. always b pwn'in'!)"
    __dependencies__ = {
        "apt": ["none"],
        "pip": ["scapy"],
    }
    __defaults__ = {
        "enabled": False,
    }

    def __init__(self):
        logging.debug(f"[{self.__class__.__name__}] plugin init")
        logging.debug(f"[{self.__class__.__name__}] Go start training.")
        self._epoch = 0
        self._train_epoch = 0
        self._total_train_epoch = 0
        self._laziness = 0.69
        self._mconfig = {}

    def loadMConfig(self, filename):
        # load all the stats and settings
        pass

    def saveMConfig(self, filename):
        # save all the stats and settings
        pass

    def on_webhook(self, path, request):
        # display parameters for modifying, lock parameter (override AI policy changes), etc

        # display brain age, time gap to backup brain
        # show reward values

        try:
            if request.method == "GET":
                if path == "/" or not path:
                    logging.info(f"[{self.__class__.__name__}] webook called")
                    ret = '<html><head><title>Mr. Miyagi AI Training</title><meta name="csrf_token" content="{{ csrf_token() }}"></head>'
                    ret += "<body><h1>Mr. Miyagi AI Training</h1><p>I'm busy. You train yourself. This doesn't do anything yet.</p>"
                    ret += "<form method=post>"
                    ret += '<input id="csrf_token" name="csrf_token" type="hidden" value="{{ csrf_token() }}">'
                    ret += "<table><tr><th>param</th><th>Value</th><th>New value</th></tr>\n"
                    # show epoch data, so save it at on_epoch, or epoch table

                    #   agent._config['personality']['associate'] = True
                    for secname, sec in [
                        ["AI", self.agent._config["ai"]],
                        ["AI Params", self.agent._config["ai"]["params"]],
                        ["Personality", self.agent._config["personality"]],
                    ]:

                        ret += "<tr><th colspan=2>Section %s</th></tr>" % secname

                        for p in sec:
                            if type(sec[p]) in [int, str, float]:
                                ret += "<tr><th>%s</th><td>%s</td>" % (
                                    p, sec[p])
                                ret += (
                                    '<td><input type=text id="newval_%s_%s" name="newval_%s_%s" size="5"></td>'
                                    % (sec, p, sec, p)
                                )
                            elif type(sec[p]) is bool:
                                # checkbox
                                ret += "<tr><th>%s</th><td>%s</td>" % (
                                    p, sec[p])
                            # ret += '<tr><th>%s</th>' % ("" if p not in self.descriptions else self.descriptions[p])
                            ret += "</tr>\n"
                    ret += "</table>"
                    ret += (
                        '<input type=submit name=submit value="update"></form></pre><p>'
                    )
                    ret += "</body></html>"
                    return render_template_string(ret)
                # other paths here
                #
            elif request.method == "POST":
                if path == "update":  # update settings that changed, save to json file
                    pass

        except Exception as e:
            ret = "<html><head><title>Mr. Miyagi says you made a mistake</title></head>"
            ret += "<body><h1>%s</h1></body></html>" % repr(e)
            logging.error(
                f"[{self.__class__.__name__}] what did you do now? %s" % repr(
                    e)
            )
            return render_template_string(ret)
        pass

    # called when the plugin is loaded
    def on_loaded(self):
        # load /etc/pwnagotchi/miyagi.json
        self._conf_file = (
            self.options["filename"]
            if "filename" in self.options
            else "/etc/pwnagotchi/miyagi.json"
        )
        logging.info(f"[{self.__class__.__name__}] plugin loaded")

        try:
            if os.path.isfile(self._conf_file):
                with open(self._conf_file, "r") as f:
                    self._mconfig = json.load(f)
                    for k, v in self._mconfig.items():
                        logging.info(
                            f"[{self.__class__.__name__}][%s] => %s"
                            % (repr(k), repr(v))
                        )
        except Exception as err:
            logging.error(f"[{self.__class__.__name__}] %s" % repr(err))

        logging.info(f"[{self.__class__.__name__}] PWN on, PWN off!")

    def save_settings(self):
        self._mconfig["laziness"] = self._laziness
        self._conf_file = (
            self.options["filename"]
            if "filename" in self.options
            else "/etc/pwnagotchi/miyagi.json"
        )
        try:
            with open(self._conf_file, "w") as f:
                f.write(json.dumps(self._mconfig, indent=4))
        except Exception as err:
            logging.error(
                f"[{self.__class__.__name__}] Save config err: %s" % repr(err)
            )

    # called before the plugin is unloaded
    def on_unload(self, ui):
        self._view.set("mode", "  AI")
        try:
            ui.remove_element("miyagi")
            ui.remove_element("m_epoch")
            logging.info(f"[{self.__class__.__name__}] plugin unloaded")
            self.save_settings()
        except Exception as e:
            logging.warn(
                f"[{self.__class__.__name__}] how hard is it to unload? %s" % repr(
                    e)
            )
        logging.info(f"[{self.__class__.__name__}] Good PWNing to you!")

    # called hen there's internet connectivity
    def on_internet_available(self, agent):
        pass

    # called to setup the ui elements
    def on_ui_setup(self, ui):
        # add custom UI elements
        self._view = ui

        try:
            ui.add_element(
                "miyagi",
                LabeledValue(
                    color=BLACK,
                    label=" LAZY: ",
                    value="%0.1f%%" % self._laziness,
                    position=(120, 84),
                    label_font=fonts.Small,
                    text_font=fonts.Small,
                    label_spacing=0,
                ),
            )
            ui.add_element(
                "m_epoch",
                LabeledValue(
                    color=BLACK,
                    label=" TRAIN: ",
                    value="BEGIN",
                    position=(185, 84),
                    label_font=fonts.Small,
                    text_font=fonts.Small,
                    label_spacing=0,
                ),
            )
        except Exception as e:
            logging.error(
                f"[{self.__class__.__name__}] ui not allowed: %s" % repr(e))

    # called when the ui is updated
    def on_ui_update(self, ui):
        # update those elements
        pass

    # called when the hardware display setup is done, display is an hardware specific object
    def on_display_setup(self, display):
        pass

    # called when everything is ready and the main loop is about to start
    def on_ready(self, agent):
        # turn off deauth until AI is ready, so all those startup deauths don't get skipped?

        logging.info(f"[{self.__class__.__name__}] plugin ready")
        logging.info(f"[{self.__class__.__name__}] Ready for training")
        self.agent = agent

        # check brain file. if empty or missing, restore backup
        self._nn_path = self.agent._config["ai"]["path"]
        if not os.path.isfile(self._nn_path) or os.path.getsize(self._nn_path) == 0:
            back = "%s.bak" % self._nn_path
            if os.path.isfile(back):
                logging.info(
                    f"[{self.__class__.__name__}] Clear your mind, not empty brain!"
                )
                os.replace(back, self._nn_path)

        # grab from system if not in plugin config file
        self._laziness = (
            self.agent._config["ai"]["laziness"]
            if "laziness" not in self._mconfig
            else self._mconfig["laziness"]
        )

        # increase training for a while, if laziness is really high
        if self._laziness > 0.98:
            self._laziness = 0.5
            logging.info(
                f"[{self.__class__.__name__}] Enough rest. You train hard now!"
            )
        self._view.set("miyagi", "%0.1f%%" % ((self._laziness * 100)))

        self.agent._config["ai"]["laziness"] = self._laziness

    # called when the AI finished loading
    def on_ai_ready(self, agent):
        self._view.set("mode", "AI  ")
        logging.info(f"[{self.__class__.__name__}] AI is ready")
        pass

    # called when the AI finds a new set of parameters
    def on_ai_policy(self, agent, policy):
        # apply overrides here. lol
        pass

    # called when the AI starts training for a given number of epochs
    def on_ai_training_start(self, agent, epochs):
        try:
            self._view.set("mode", "  ai")
            self._train_epoch = 0

            # save a backup of the brain before start training
            self._nn_path = self.agent._config["ai"]["path"]
            if os.path.isfile(self._nn_path):
                back = "%s.bak" % self._nn_path
                os.replace(self._nn_path, back)
                self._view.set("mode", "STRT")

        except Exception as e:
            logging.warn(
                f"[{self.__class__.__name__}] you did not start training: %s" % repr(
                    e)
            )

    # called after the AI completed a training epoch
    def on_ai_training_step(self, agent, _locals, _globals):
        self._train_epoch += 1
        self._total_train_epoch += 1
        self._view.set("mode", "Tr%02i" % self._train_epoch)
        if self._epoch > 0:
            self._view.set(
                "m_epoch", "%0.2f%%" % (
                    self._total_train_epoch / self._epoch * 100.0)
            )

    # called when the AI has done training
    def on_ai_training_end(self, agent):
        self._view.set("mode", "  AI")

        # update laziness to not stay in training forever
        if self.agent._config["ai"]["laziness"] < 0.97:
            self.agent._config["ai"]["laziness"] *= 0.5
            self.agent._config["ai"]["laziness"] += 0.5
        else:
            self.agent._config["ai"]["laziness"] *= 0.8
            self.agent._config["ai"]["laziness"] += 0.2
        self._laziness = self.agent._config["ai"]["laziness"]
        logging.info(
            f"[{self.__class__.__name__}] laziness = %0.4f"
            % self.agent._config["ai"]["laziness"]
        )
        self.save_settings()
        if self.agent._config["ai"]["laziness"] < 10:
            self._view.set(
                "miyagi", "%0.2f%%" % (
                    self.agent._config["ai"]["laziness"] * 100)
            )
        else:
            self._view.set(
                "miyagi", "%0.1f%%" % (
                    self.agent._config["ai"]["laziness"] * 100)
            )

    # called when the AI got the best reward so far
    def on_ai_best_reward(self, agent, reward):
        # change some parameters to stop spoiling the AI
        pass

    # called when the AI got the worst reward so far
    def on_ai_worst_reward(self, agent, reward):
        # change some parameters, because we are sucking!
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

    # called when the agent is sending an association frameR
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
        logging.info(
            f"[{self.__class__.__name__}] on_epoch called %s: %s"
            % (epoch, repr(epoch_data))
        )
        try:
            self._epoch += 1
            self._view.set(
                "m_epoch", "%0.2f%%" % (
                    self._total_train_epoch / self._epoch * 100.0)
            )
            logging.info(
                f"[{self.__class__.__name__}] epoch %s  %s"
                % (self._epoch, self._total_train_epoch)
            )
        except Exception as e:
            logging.error(
                f"[{self.__class__.__name__}] on_epoch: %s" % repr(e))

    # called when a new peer is detected
    def on_peer_detected(self, agent, peer):
        pass

    # called when a known peer is lost
    def on_peer_lost(self, agent, peer):
        pass
