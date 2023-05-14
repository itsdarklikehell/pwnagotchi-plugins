from pwnagotchi import plugins
from pwnagotchi.voice import Voice
import logging
import os


class Discord(plugins.Plugin):
    __author__ = 'isabelladonnamoore@outlook.com'
    __version__ = '2.0.0'
    __license__ = 'GPL3'
    __description__ = 'Post recent activity to a Discord channel using webhooks. Requires discord.py module.'
    __dependencies__ = {
        'pip': ['discord'],
        'webhook_url': '',
        'username': 'pwnagotchi',
    }
    __defaults__ = {
        'enabled': False,
    }

    def __init__(self):
        self.ready = False

    def on_loaded(self):

        if 'webhook_url' not in self.options or not self.options['webhook_url']:
            logging.error("[discord] Webhook URL is not set, cannot post to Discord")
            return

        if 'username' not in self.options or not self.options['username']:
            with open('/etc/hostname') as fp:
                self.options['username'] = fp.read().strip()

        self.ready = True
        logging.info("[discord] plugin loaded")

    # called when there's available internet
    def on_internet_available(self, agent):
        if not self.ready:
            return

        config = agent.config()
        display = agent.view()
        last_session = agent.last_session

        if last_session.is_new() and last_session.handshakes > 0:
            try:
                from discord import Webhook, RequestsWebhookAdapter, File
            except ImportError as e:
                logging.error('[discord] couldn\'t import discord.py (%s)', e)
                return

            logging.info('[discord] detected new activity and internet, time to send a message!')

            picture = '/var/tmp/pwnagotchi/pwnagotchi.png' if os.path.exists(
                "/var/tmp/pwnagotchi/pwnagotchi.png") else '/root/pwnagotchi.png'
            display.on_manual_mode(last_session)
            display.image().save(picture, 'png')
            display.update(force=True)

            try:
                logging.info('[discord] sending message...')

                message = Voice(lang=config['main']['lang']).on_last_session_tweet(
                    last_session)
                url = self.options['webhook_url']
                username = self.options['username']

                webhook = Webhook.from_url(
                    url, adapter=RequestsWebhookAdapter())
                webhook.send(
                    message, username=username, file=File(picture))
                logging.info('[discord] message sent: %s', message)

                last_session.save_session_id()
                display.set('status', 'Discord notification sent!')
                display.update(force=True)
            except Exception as e:
                logging.exception('[discord] error while sending message (%s)', e)
