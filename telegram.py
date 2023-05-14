from pwnagotchi import plugins
from pwnagotchi.voice import Voice
import logging


class Telegram(plugins.Plugin):
    __author__ = 'djerfy@gmail.com'
    __version__ = '2.0.0'
    __license__ = 'GPL3'
    __description__ = 'Periodically sent messages to Telegram about the recent activity of pwnagotchi'
    __dependencies__ = {
        'pip': ['python-telegram-bot'],
    }
    __defaults__ = {
        'enabled': False,
        'bot_token': None,
        'bot_name': 'pwnagotchi',
        'chat_id': None,
        'send_picture': True,
        'send_message': True,
    }

    def on_loaded(self):
        logging.info('[telegram] plugin loaded.')

    # called when there's available internet
    def on_internet_available(self, agent):
        config = agent.config()
        display = agent.view()
        last_session = agent.last_session

        if last_session.is_new() and last_session.handshakes > 0:

            try:
                import telegram
            except ImportError:
                logging.error('[telegram] Couldn\'t import telegram')
                return

            logging.info('[telegram] Detected new activity and internet, time to send a message!')

            picture = '/root/pwnagotchi.png'
            display.on_manual_mode(last_session)
            display.image().save(picture, 'png')
            display.update(force=True)

            try:
                logging.info('[telegram] Connecting to Telegram...')

                message = Voice(lang=config['main']['lang']).on_last_session_tweet(last_session)

                bot = telegram.Bot(self.options['bot_token'])
                if self.options['send_picture'] is True:
                    bot.sendPhoto(chat_id=self.options['chat_id'], photo=open(picture, 'rb'))
                    logging.info('[telegram] picture sent')
                if self.options['send_message'] is True:
                    bot.sendMessage(chat_id=self.options['chat_id'], text=message, disable_web_page_preview=True)
                    logging.info('[telegram] message sent: %s', message)

                last_session.save_session_id()
                display.set('status', 'Telegram notification sent!')
                display.update(force=True)
            except Exception as ex:
                logging.exception('[telegram] Error while sending on Telegram: %s', ex)
