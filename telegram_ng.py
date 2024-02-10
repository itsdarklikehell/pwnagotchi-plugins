import logging
from pwnagotchi.voice import Voice
import pwnagotchi.plugins as plugins
import os
import pwnagotchi
import glob
from subprocess import Popen

# See here to make the summary send in auto mode
# https://gist.github.com/alistar79/785b422ab5de846b27e1770550526bce


class Telegram_ng(plugins.Plugin):
    __GitHub__ = ""
    __author__ = "(edited by: itsdarklikehell bauke.molenaar@gmail.com), djerfy@gmail.com"
    __version__ = "2.0.0"
    __license__ = "GPL3"
    __description__ = "Periodically sent messages to Telegram about the recent activity of pwnagotchi."
    __name__ = "Telegram_ng"
    __help__ = "Periodically sent messages to Telegram about the recent activity of pwnagotchi."
    __dependencies__ = {
        "pip": ["python-telegram-bot"],
    }
    __defaults__ = {
        'enabled': False,
        'bot_token': 'None',  # Quote me
        'bot_name': 'pwnagotchi',
        'chat_id': None,  # Don't quote me
        'send_picture': True,
        'send_message': True,
    }

    def on_loaded(self):
        logging.info(f"[{self.__class__.__name__}] plugin loaded.")

    # called when there's available internet
    def on_internet_available(self, agent):
        config = agent.config()
        display = agent.view()
        last_session = agent.last_session

        if last_session.is_new() and last_session.handshakes >= 0:

            try:
                import telegram
            except ImportError:
                logging.error(
                    f"[{self.__class__.__name__}] Couldn't import telegram")
                return

            logging.info(
                f"[{self.__class__.__name__}] Detected new activity and internet, time to send a message!"
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
                logging.info(
                    f"[{self.__class__.__name__}] Connecting to Telegram...")

                message = Voice(lang=config["main"]["lang"]).on_last_session_tweet(
                    last_session
                )

                bot = telegram.Bot(self.options["bot_token"])
                if self.options["send_picture"] is True:
                    bot.sendPhoto(
                        chat_id=self.options["chat_id"], photo=open(
                            picture, "rb")
                    )
                    logging.info(f"[{self.__class__.__name__}] picture sent")
                if self.options["send_message"] is True:
                    bot.sendMessage(
                        chat_id=self.options["chat_id"],
                        text=message,
                        disable_web_page_preview=True,
                    )
                    logging.info(
                        f"[{self.__class__.__name__}] message sent: %s", message
                    )

                last_session.save_session_id()
                display.set("status", "Telegram notification sent!")
                display.update(force=True)
            except Exception as ex:
                logging.exception(
                    f"[{self.__class__.__name__}] Error while sending on Telegram: %s",
                    ex,
                )
        try:
            import telegram
        except ImportError:
            logging.error(
                f"[{self.__class__.__name__}] Couldn't import telegram")
            return
        bot = telegram.Bot(self.options["bot_token"])
        updates = bot.get_updates()
        try:
            with open("/root/.tuid", "r") as f:
                update_id = int(f.read().replace("\n", ""))
        except Exception:
            update_id = 0
        try:
            message = updates[update_id].message.text
            msg_id = updates[update_id].message.message_id
            logging.info(
                f"[{self.__class__.__name__}] Received message ID: %d", msg_id)
            try:
                with open("/root/.tmid", "r") as f:
                    last_msg_id = int(f.read().replace("\n", ""))
            except:
                last_msg_id = -1
            if msg_id > last_msg_id:
                with open("/root/.tmid", "w") as f:
                    f.write("%d\n" % msg_id)
            else:
                update_id += 1
                with open("/root/.tuid", "w") as f:
                    f.write("%d\n" % update_id)
                raise Exception("Old message")
        except:
            if update_id != 0:
                try:
                    message = updates[update_id - 1].message.text
                except:
                    update_id = 0
                    with open("/root/.tuid", "w") as f:
                        f.write("%d\n" % update_id)

        else:
            logging.info(
                f"[{self.__class__.__name__}] Recevied message: %s", message)
            update_id += 1
            with open("/root/.tuid", "w") as f:
                f.write("%d\n" % update_id)
            if message == "/start":
                repmessage = """
(⌐■_■) Pwnagotchi Telegram Bot (⌐■_■)
(◕‿‿◕) Commands (◕‿‿◕)
(☓‿‿☓) /start This menu!
(☓‿‿☓) /handshakes Prints last 100 handshake filenames
(☓‿‿☓) /passwords Prints cracked passwords
(☓‿‿☓) /restart Restarts pwnagotchi service
(☓‿‿☓) /shutdown Shutdown device
(☓‿‿☓) /switch_mode Switch between manual and auto mode
(☓‿‿☓) /flip_col Invert display colors
(☓‿‿☓) /flip_faces Switch between emoticons and punk girl faces
(☓‿‿☓) /flip_led Switch between morse code led and normal
(☓‿‿☓) /add_cracked Add cracked hashes to webgpsmap
(☓‿‿☓) /pwnmenu Relays pwnmenu commands up/down/ok/back/close/stop
(⇀‿‿↼)(≖‿‿≖)(◕‿‿◕)( ⚆_⚆)(☉_☉ )( ◕‿◕)(◕‿◕ )(°▃▃°)(⌐■_■)(•‿‿•)
(^‿‿^)(ᵔ◡◡ᵔ)(✜‿‿✜)(♥‿‿♥)(☼‿‿☼)(≖__≖)(-__-)(╥☁╥ )(ب__ب)(☓‿‿☓)
"""
                bot.sendMessage(
                    chat_id=self.options["chat_id"],
                    text=repmessage,
                    disable_web_page_preview=True,
                )
            elif message == "/handshakes":
                os.chdir("/root/handshakes")
                cur_handshakes = sorted(
                    glob.glob("*.pcap"), key=os.path.getmtime)
                s_cur_handshakes = """
(⌐■_■) Handshakes
{}
""".format(
                    "\n".join(cur_handshakes[-100:])
                )
                repmessage = s_cur_handshakes
                bot.sendMessage(
                    chat_id=self.options["chat_id"],
                    text=repmessage,
                    disable_web_page_preview=True,
                )
            elif message == "/passwords":
                files = [
                    "/root/handshakes/wpa-sec.cracked.potfile",
                    "/root/handshakes/banthex.cracked.potfile",
                    "/root/handshakes/onlinehashcrack.cracked",
                ]
                # loop to retreive all passwords of all files into a big list without dulicate
                tmp_list = list()
                clist = list()
                for file_path in files:
                    if file_path.lower().endswith(".potfile"):
                        with open(file_path) as f:
                            for line in f:
                                tmp_line = str(
                                    line.rstrip().split(":", 2)[-1:])[2:-2]
                                tmp_list.append(tmp_line)
                    elif file_path.lower().endswith(".cracked"):
                        with open(file_path) as f:

                            for line in f:
                                tmp_first = str(line.rstrip().split(",")[:3][1:-1])[
                                    3:-3
                                ]
                                tmp_last = str(line.rstrip().split(",")[
                                               3:][1:-1])[3:-3]
                                tmp_line = "%s:%s" % (tmp_first, tmp_last)
                                tmp_list.append(tmp_line)
                    else:
                        logging.info(
                            "[CRACK HOUSE] %s type is not managed"
                            % (os.path.splitext(file_path))
                        )

                for line in tmp_list:
                    if line.rstrip().split(":")[1] != "":
                        clist.append(line)
                CRACK_MENU = """
(⌐■_■) Passwords
{}
""".format(
                    "\n".join(clist[0:])
                )
                repmessage = CRACK_MENU
                bot.sendMessage(
                    chat_id=self.options["chat_id"],
                    text=repmessage,
                    disable_web_page_preview=True,
                )
            elif message == "/restart":
                repmessage = "(⌐■_■) Restart initiated..."
                bot.sendMessage(
                    chat_id=self.options["chat_id"],
                    text=repmessage,
                    disable_web_page_preview=True,
                )
                mode = "MANU" if agent.mode == "manual" else "AUTO"
                pwnagotchi.restart(mode)
            elif message == "/shutdown":
                repmessage = "(⌐■_■) Shutdown initiated..."
                bot.sendMessage(
                    chat_id=self.options["chat_id"],
                    text=repmessage,
                    disable_web_page_preview=True,
                )
                pwnagotchi.shutdown()
            elif message == "/switch_mode":
                repmessage = "(⌐■_■) Mode switch initiated..."
                bot.sendMessage(
                    chat_id=self.options["chat_id"],
                    text=repmessage,
                    disable_web_page_preview=True,
                )
                mode = "AUTO" if agent.mode == "manual" else "MANU"
                pwnagotchi.restart(mode)
            elif message == "/flip_col":
                repmessage = "(⌐■_■) Color invert initiated..."
                bot.sendMessage(
                    chat_id=self.options["chat_id"],
                    text=repmessage,
                    disable_web_page_preview=True,
                )
                Popen("/root/flip_col.sh")
            elif message == "/flip_faces":
                repmessage = "(⌐■_■) Faces/Emoticon switch initiated..."
                bot.sendMessage(
                    chat_id=self.options["chat_id"],
                    text=repmessage,
                    disable_web_page_preview=True,
                )
                Popen("/root/flip_faces.sh")
            elif message == "/flip_led":
                repmessage = "(⌐■_■) LED Morse code/Normal switch initiated..."
                bot.sendMessage(
                    chat_id=self.options["chat_id"],
                    text=repmessage,
                    disable_web_page_preview=True,
                )
                Popen("/root/flip_led.sh")
            elif message == "/add_cracked":
                repmessage = "(⌐■_■) OHC, wpa-sec insert to webgpsmap initiated..."
                bot.sendMessage(
                    chat_id=self.options["chat_id"],
                    text=repmessage,
                    disable_web_page_preview=True,
                )
                Popen("/root/ohc.founds.insert.py")
                Popen("/root/wpa-sec.founds.insert.py")
            elif "/pwnmenu" in message:
                word_count = len(message.split())
                if word_count > 1:
                    word = message.split()[1]
                    logging.info(
                        f"[{self.__class__.__name__}] /pwnmenu cmd: %s", word)
                    if word in ("up", "down", "ok", "back", "close", "stop"):
                        Popen("/root/pwnmenucmd.py " + word, shell=True)
                        repmessage = "(⌐■_■) Pwnmenu command " + \
                            word + " sent..."
                    else:
                        repmessage = "(☓‿‿☓) Pwnmenu command error"
                else:
                    repmessage = "(☓‿‿☓) Pwnmenu command error"
                bot.sendMessage(
                    chat_id=self.options["chat_id"],
                    text=repmessage,
                    disable_web_page_preview=True,
                )
            else:
                repmessage = (
                    message + "????!??! What you think this is?? ChatGPT?? pffttt"
                )
                bot.sendMessage(
                    chat_id=self.options["chat_id"],
                    text=repmessage,
                    disable_web_page_preview=True,
                )
