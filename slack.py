import logging
import pwnagotchi.plugins as plugins
import os
import requests
import subprocess


class Slack(plugins.Plugin):
    __author__ = "branislav.djalic@gmail.com"
    __version__ = "1.0.0"
    __license__ = "GPL3"
    __description__ = (
        "Post recent activity to a Slack using webhooks. Requires slackclient module."
    )
    __name__ = "Slack"
    __help__ = (
        "Post recent activity to a Slack using webhooks. Requires slackclient module."
    )
    __dependencies__ = {
        "apt": ["none"],
        "pip": ["scapy"],
    }
    __defaults__ = {
        "enabled": False,
    }

    def __init__(self):
        self.ready = False

    def on_loaded(self):

        if "token" not in self.options or not self.options["token"]:
            logging.error("Slack: Bot token is not set, cannot post to Slack")
            return

        self.ready = True
        logging.info("Slack: plugin loaded")

    # called when there's available internet
    def on_internet_available(self, agent):
        if not self.ready:
            return

        config = agent.config()
        display = agent.view()
        last_session = agent.last_session

        if last_session.is_new() and last_session.handshakes > 0:
            try:
                from slack import WebClient
            except ImportError as e:
                logging.error("Slack: couldn't import slackclient module")
                logging.debug(e)
                return

            logging.info(
                "Slack: detected new activity and internet, time to send a message!"
            )

            picture = (
                "/var/tmp/pwnagotchi/pwnagotchi.png"
                if os.path.exists("/var/tmp/pwnagotchi/pwnagotchi.png")
                else "/root/pwnagotchi.png"
            )
            display.on_manual_mode(last_session)
            display.image().save(picture, "png")
            display.update(force=True)

            try:
                logging.info("Slack: sending message...")
                token = self.options["token"]
                title_ = self.option["title"]
                channel = self.channel["channel"]
                sc = WebClient(token)
                sc.files_upload(
                    channels=channel, file=picture, title=title_, filetype="png"
                )

                last_session.save_session_id()
                display.set("status", "Slack notification sent!")
                display.update(force=True)
            except Exception as e:
                logging.exception("Slack: error while sending message")
                logging.debug(e)
