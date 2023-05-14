import logging
from pwnagotchi.voice import Voice
from pwnagotchi import plugins


class Twitter(plugins.Plugin):
    __author__ = 'evilsocket@gmail.com'
    __version__ = '2.0.1'
    __license__ = 'GPL3'
    __description__ = 'This plugin creates tweets about the recent activity of pwnagotchi'
    __dependencies__ = {
        'pip': ['tweepy']
    }
    __defaults__ = {
        'enabled': False,
        'consumer_key': None,
        'consumer_secret': None,
        'access_token_key': None,
        'access_token_secret': None,
    }

    def on_loaded(self):
        logging.info('[twitter] plugin loaded.')

    # called in manual mode when there's internet connectivity
    def on_internet_available(self, agent):
        config = agent.config()
        display = agent.view()
        last_session = agent.last_session

        if last_session.is_new() and last_session.handshakes > 0:
            try:
                import tweepy
            except ImportError as ie:
                logging.error('[twitter] Couldn\'t import tweepy (%s)', ie)
                return

            logging.info('[twitter] detected a new session and internet connectivity!')

            picture = '/root/pwnagotchi.png'

            display.on_manual_mode(last_session)
            with display.block_update(force=True):
                display.image().save(picture, 'png')
            display.set('status', 'Tweeting...')
            display.update(force=True)

            try:
                auth = tweepy.OAuthHandler(self.options['consumer_key'], self.options['consumer_secret'])
                auth.set_access_token(self.options['access_token_key'], self.options['access_token_secret'])
                api = tweepy.API(auth)

                tweet = Voice(lang=config['main']['lang']).on_last_session_tweet(last_session)
                api.update_with_media(filename=picture, status=tweet)
                last_session.save_session_id()

                logging.info('[twitter] tweeted: %s', tweet)
            except Exception as e:
                logging.exception('[twitter] error while tweeting (%s)', e)
