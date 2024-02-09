import os
import re
import sys
import time
import logging
import random
import re
import subprocess

import pwnagotchi.plugins as plugins
from pwnagotchi.ui.components import LabeledValue
from pwnagotchi.ui.view import BLACK
import pwnagotchi.ui.fonts as fonts

import html

try:
    import feedparser
except Exception as e:
    logging.error("%s. Installing feedparser..." % repr(e))
    subprocess.check_call(
        [sys.executable, "-m", "pip", "install", "feedparser"])
    logging.info("Trying to import 'feedparser' again")
    import feedparser


class RSS_Voice(plugins.Plugin):
    __GitHub__ = ""
    __author__ = "(edited by: itsdarklikehell bauke.molenaar@gmail.com), Sniffleupagus"
    __version__ = "1.0.0"
    __license__ = "GPL3"
    __description__ = "Use RSS Feeds to replace canned voice messages on various events"
    __name__ = "RSS_Voice"
    __help__ = "Use RSS Feeds to replace canned voice messages on various events"
    __dependencies__ = {
        "apt": ["none"],
        "pip": ["scapy"],
    }
    __defaults__ = {
        "enabled": False,
        "feed.wait.url": "https://www.reddit.com/r/worldnews.rss",
        "feed.bored.url": "https://www.reddit.com/r/showerthoughts.rss",
        "feed.sad.url": "https://www.reddit.com/r/pwnagotchi.rss",
        "path": "/home/pi/voice_rss",
    }

    def __init__(self):
        self.last_checks = {"wait": 0}
        logging.debug(f"[{self.__class__.__name__}] plugin init")
        self.voice = ""

    def _wget(self, url, rssfile, verbose=False):
        logging.debug("[{self.__class__.__name__}] _wget %s: %s" %
                      (rssfile, url))
        process = subprocess.run(["/usr/bin/wget", "-q", "-O", rssfile, url])
        logging.debug("[{self.__class__.__name__}] %s", repr(process))

    def _fetch_rss_message(self, key):
        rssfile = "%s/%s.rss" % (self.options["path"], key)
        if os.path.isfile(rssfile):
            logging.debug(
                "[{self.__class__.__name__}] pulling from %s" % (rssfile))
            try:
                feed = feedparser.parse(rssfile)
                article = random.choice(feed.entries)

                def sub_element(match_obj):
                    ele = match_obj.group(1)
                    if ele in article:
                        return article[ele]
                    else:
                        try:
                            return html.unescape(
                                re.sub("<[^>]+>", "",
                                       eval("article[%s]" % ele))
                            )

                        except Exception as e:
                            logging.warn(repr(e))
                            return repr(e)

                if "format" in self.options["feed"][key]:
                    headline = re.sub(
                        r"%([^%]+)%", sub_element, self.options["feed"][key]["format"]
                    )
                    headline = html.unescape(re.sub("<[^>]+>", "", headline))
                else:
                    headline = "%s: %s" % (
                        article.author[3:],
                        html.unescape(re.sub("<[^>]+>", "", article.summary)),
                    )

            except Exception as e:
                headline = repr(e)

            logging.debug("[{self.__class__.__name__}] %s: %s" %
                          (key, headline))

            return headline
        else:
            return ""

    # called when the plugin is loaded
    def on_loaded(self):
        logging.info(f"[{self.__class__.__name__}] plugin loaded")
        logging.warn("[{self.__class__.__name__}] options = %s" % self.options)
        if "path" not in self.options:
            self.options["path"] = "/root/voice_rss"

        rssdir = self.options["path"]
        if not os.path.isdir(rssdir):
            logging.info("Creating directory for rss feeds: %s" % (rssdir))
            try:
                os.mkdir(rssdir)
            except Exception as e:
                logging.error("mkdir %s: %s" % (rssdir, repr(e)))

    # called before the plugin is unloaded
    def on_unload(self, ui):
        pass

    # called hen there's internet connectivity
    def on_internet_available(self, agent):
        # check rss feeds, unless too recent
        logging.debug("[{self.__class__.__name__}] internet available")
        if "feed" in self.options:
            now = time.time()
            feeds = self.options["feed"]
            logging.debug(
                "[{self.__class__.__name__}] processing feeds: %s" % feeds)
            for k, v in feeds.items():  # a feed value can be a dictionary
                logging.debug(
                    "[{self.__class__.__name__}] feed: %s = %s" % (
                        repr(k), repr(v))
                )
                timeout = 3600 if "timeout" not in v else v["timeout"]
                logging.debug(
                    "[{self.__class__.__name__}] %s timeout = %s" % (
                        repr(k), timeout)
                )
                try:
                    if not k in self.last_checks or now > (
                        self.last_checks[k] + timeout
                    ):
                        # update feed if past timeout since last check
                        rss_file = "%s/%s.rss" % (self.options["path"], k)
                        if (
                            os.path.isfile(rss_file)
                            and now < os.path.getmtime(rss_file) + timeout
                        ):
                            logging.debug("too soon by file age!")
                        else:
                            if "url" in v:
                                self._wget(v["url"], rss_file)
                                self.last_checks[k] = time.time()
                            else:
                                logging.warn("No url in  %s" % repr(v))
                    else:
                        logging.debug("too soon!")
                except Exception as e:
                    logging.error("[{self.__class__.__name__}] %s" % repr(e))
        pass

    # called to setup the ui elements
    def on_ui_setup(self, ui):
        #
        # use built in elements, probably
        #
        # add custom UI elements
        # ui.add_element('ups', LabeledValue(color=BLACK, label='UPS', value='0%/0V', position=(ui.width() / 2 - 25, 0),
        #                                   label_font=fonts.Bold, text_font=fonts.Medium))
        pass

    # called when the ui is updated
    def on_ui_update(self, ui):
        # update those elements
        if self.voice != "":
            logging.debug("RSS: Status to %s" % self.voice)
            ui.set("status", self.voice)
            self.voice = ""

    # called when the hardware display setup is done, display is an hardware specific object
    def on_display_setup(self, display):
        pass

    # called when everything is ready and the main loop is about to start
    def on_ready(self, agent):
        self.on_internet_available(agent)
        # you can run custom bettercap commands if you want
        #   agent.run('ble.recon on')
        # or set a custom state
        #   agent.set_bored()

    # set up RSS feed per emotion

    # called when the status is set to bored
    def on_bored(self, agent):
        self.voice = self._fetch_rss_message("bored")
        pass

    # called when the status is set to sad
    def on_sad(self, agent):
        self.voice = self._fetch_rss_message("sad")
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
        self.voice = "(%ss) %s" % (int(t), self._fetch_rss_message("wait"))
        logging.debug("[{self.__class__.__name__}] on_wait: %s" % self.voice)

    # called when the agent is sleeping for t seconds
    def on_sleep(self, agent, t):
        self.voice = "(%ss zzz) %s" % (
            int(t), self._fetch_rss_message("sleep"))

    # called when an epoch is over (where an epoch is a single loop of the main algorithm)
    def on_epoch(self, agent, epoch, epoch_data):
        pass

    def on_webhook(self, path, request):
        logging.info(f"[{self.__class__.__name__}] webhook pressed")
