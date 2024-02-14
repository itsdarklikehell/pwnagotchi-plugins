import os
import pwd
import logging
import telegram
import subprocess
import pwnagotchi
import random
import codecs
import base64
import toml
from time import sleep
from pwnagotchi import fs
from pwnagotchi.ui import view
from pwnagotchi.voice import Voice
import pwnagotchi.plugins as plugins
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.botcommand import BotCommand
from telegram.ext import (
    CommandHandler,
    MessageHandler,
    Filters,
    CallbackQueryHandler,
    Updater,
)

home_dir = "/home/pi"
max_length_message = int(4096 // 2)
max_messages_per_minute = 20
main_menu = [
    [
        InlineKeyboardButton("🔄 Reboot", callback_data="reboot"),
        InlineKeyboardButton("🛑 Shutdown", callback_data="shutdown"),
        InlineKeyboardButton("⏰ Uptime", callback_data="uptime"),
    ],
    [
        InlineKeyboardButton("🤝 Handshake Count", callback_data="handshake_count"),
        InlineKeyboardButton(
            "🔓 Read Potfiles Cracked", callback_data="read_potfiles_cracked"
        ),
        InlineKeyboardButton(
            "📬 Fetch Pwngrid Inbox", callback_data="fetch_pwngrid_inbox"
        ),
    ],
    [
        InlineKeyboardButton("🧠 Read Memory & Temp", callback_data="read_memtemp"),
        InlineKeyboardButton("🎨 Take Screenshot", callback_data="take_screenshot"),
        InlineKeyboardButton("💾 Create Backup", callback_data="create_backup"),
    ],
    [
        InlineKeyboardButton("🔄 Update bot", callback_data="bot_update"),
        InlineKeyboardButton("🗡️  Kill the daemon", callback_data="pwnkill"),
        InlineKeyboardButton("🔁 Restart Daemon", callback_data="soft_restart"),
    ],
]

stickers_exception = [
    "CAACAgIAAxkBAAIKJGXHDISOASdXpKbXske2Q1IaVEMpAAIwAAMPdWsI7k_UrvN3piI0BA",
    "CAACAgIAAxkBAAIKJmXHDIji0_pKBLqYHJMHQkw3QzZ9AAIyAAMPdWsIBdtzkkhTXqY0BA",
    "CAACAgQAAxkBAAIKLmXHDM-ynEU2Int0s1YcpC3bqKK2AAIUAAPTrAoCbIyNeEmfdRo0BA",
    "CAACAgIAAxkBAAIKMmXHDOTYF93WIanWQLgh9FgR8SnpAALtDAACT6QpSMtoWq3QTPsONAQ",
]

stickers_kill_daemon = [
    "CAACAgQAAxkBAAIKKGXHDMFCsebQHdKaxBMwDJDpTrc7AAI5AAPTrAoCTTZZF0MD5og0BA",
]

stickers_handshake_or_wpa = [
    "CAACAgIAAxkBAAIKMGXHDNlSDzyw6spWefM0J7O9br61AAL6EAACoccoSDllduuTWAejNAQ",
    "CAACAgQAAxkBAAIKLGXHDMbkJgl6jf2fmkoz5WoSVO8KAAIcAAPTrAoC1E8xZAtCX8A0BA",
]


class Telegram_ng(plugins.Plugin):
    __GitHub__ = ""
    __author__ = (
        "(edited by: itsdarklikehell bauke.molenaar@gmail.com), djerfy@gmail.com"
    )
    __version__ = "2.0.0"
    __license__ = "GPL3"
    __description__ = "Periodically sent messages to Telegram about the recent activity of pwnagotchi."
    __name__ = "Telegram_ng"
    __help__ = "Periodically sent messages to Telegram about the recent activity of pwnagotchi."
    __dependencies__ = {
        "pip": ["python-telegram-bot"],
    }
    __defaults__ = {
        "enabled": False,
        "bot_token": "None",  # Quote me
        "bot_name": "pwnagotchi",
        "chat_id": None,  # Don't quote me
        "send_picture": True,
        "send_message": True,
    }

    def on_loaded(self) -> None:
        logging.info(f"[{self.__class__.__name__}] telegram plugin loaded.")
        self.logger = logging.getLogger("TelegramPlugin")
        self.options["auto_start"] = True
        self.completed_tasks = 0
        self.num_tasks = 8  # Increased for the new pwnkill task
        self.updater = None
        self.start_menu_sent = False
        self.last_backup = ""
        # Read toml file
        try:
            with open("/etc/pwnagotchi/config.toml", "r") as f:
                config = toml.load(f)
                self.screen_rotation = int(config["ui"]["display"]["rotation"])
                self.plugins_dir = str(config["main"]["custom_plugins"])
        except:
            self.screen_rotation = 0
            self.plugins_dir = "/usr/local/share/pwnagotchi/custom-plugins"

    def on_agent(self, agent) -> None:
        if "auto_start" in self.options and self.options["auto_start"]:
            self.on_internet_available(agent)

    def register_command_handlers(self, agent, dispatcher) -> None:
        dispatcher.add_handler(
            MessageHandler(
                Filters.regex("^/start$"),
                lambda update, context: self.start(agent, update, context),
            )
        )
        dispatcher.add_handler(
            CommandHandler(
                "menu",
                lambda update, context: self.start(agent, update, context),
            )
        )
        dispatcher.add_handler(
            CommandHandler(
                "reboot_to_manual",
                lambda update, context: self.reboot_mode("MANUAL", update, context),
            )
        )
        dispatcher.add_handler(
            CommandHandler(
                "reboot_to_auto",
                lambda update, context: self.reboot_mode("AUTO", update, context),
            )
        )
        dispatcher.add_handler(
            CommandHandler(
                "shutdown",
                lambda update, context: self.shutdown(agent, update, context),
            )
        )
        dispatcher.add_handler(
            CommandHandler(
                "uptime", lambda update, context: self.uptime(agent, update, context)
            )
        )
        dispatcher.add_handler(
            CommandHandler(
                "handshake_count",
                lambda update, context: self.handshake_count(agent, update, context),
            )
        )
        dispatcher.add_handler(
            CommandHandler(
                "read_potfiles_cracked",
                lambda update, context: self.read_potfiles_cracked(
                    agent, update, context
                ),
            )
        )
        dispatcher.add_handler(
            CommandHandler(
                "fetch_pwngrid_inbox",
                lambda update, context: self.handle_pwngrid_inbox(
                    agent, update, context
                ),
            )
        )
        dispatcher.add_handler(
            CommandHandler(
                "read_memtemp",
                lambda update, context: self.handle_memtemp(agent, update, context),
            )
        )
        dispatcher.add_handler(
            CommandHandler(
                "take_screenshot",
                lambda update, context: self.take_screenshot(agent, update, context),
            )
        )
        dispatcher.add_handler(
            CommandHandler(
                "create_backup",
                lambda update, context: self.create_backup(agent, update, context),
            )
        )
        dispatcher.add_handler(
            CommandHandler(
                "pwnkill", lambda update, context: self.pwnkill(agent, update, context)
            )
        )
        dispatcher.add_handler(
            CommandHandler(
                "soft_restart",
                lambda update, context: self.soft_restart(agent, update, context),
            )
        )
        dispatcher.add_handler(
            CommandHandler(
                "soft_restart_to_manual",
                lambda update, context: self.soft_restart_mode(
                    "MANUAL", update, context
                ),
            )
        )
        dispatcher.add_handler(
            CommandHandler(
                "soft_restart_to_auto",
                lambda update, context: self.soft_restart_mode("AUTO", update, context),
            )
        )
        dispatcher.add_handler(
            CommandHandler(
                "send_backup",
                lambda update, context: self.send_backup(agent, update, context),
            )
        )
        dispatcher.add_handler(
            CommandHandler(
                "bot_update",
                lambda update, context: self.bot_update(agent, update, context),
            )
        )
        dispatcher.add_handler(
            CommandHandler("help", lambda update, context: self.help(update, context))
        )
        dispatcher.add_handler(
            CommandHandler(
                "rot13", lambda update, context: self.rot13(agent, update, context)
            )
        )
        dispatcher.add_handler(
            CommandHandler(
                "debase64",
                lambda update, context: self.debase64(agent, update, context),
            )
        )
        dispatcher.add_handler(
            CommandHandler(
                "base64", lambda update, context: self.base64(agent, update, context)
            )
        )
        dispatcher.add_handler(
            CommandHandler(
                "cmd", lambda update, context: self.command_executed(update, context)
            )
        )
        dispatcher.add_handler(
            CommandHandler(
                "kill_ps", lambda update, context: self.kill_ps(agent, update, context)
            )
        )
        dispatcher.add_handler(
            CommandHandler(
                "kill_ps_name",
                lambda update, context: self.kill_ps_name(agent, update, context),
            )
        )

        dispatcher.add_handler(
            CommandHandler(
                "turn_led_off",
                lambda update, context: self.change_led(
                    agent, update, context, mode="off"
                ),
            )
        )

        dispatcher.add_handler(
            CommandHandler(
                "turn_led_on",
                lambda update, context: self.change_led(
                    agent, update, context, mode="on"
                ),
            )
        )

        dispatcher.add_handler(
            CallbackQueryHandler(
                lambda update, context: self.button_handler(agent, update, context)
            )
        )

    def start(self, agent, update, context) -> None:
        # Verify if the user is authorized
        if update.effective_chat.id == int(self.options.get("chat_id")):
            bot_name = str(self.options.get("bot_name", "Pwnagotchi"))
            response = f"🖖 Welcome to <b>{bot_name}</b>\n\nPlease select an option:"
            self.send_new_message(update, context, response, main_menu)
        return

    def button_handler(self, agent, update, context) -> None:
        if update.effective_chat.id == int(self.options.get("chat_id")):
            query = update.callback_query
            query.answer()

            action_map = {
                "reboot": self.reboot,
                "reboot_to_manual": self.reboot_to_manual,
                "reboot_to_auto": self.reboot_to_auto,
                "shutdown": self.shutdown,
                "uptime": self.uptime,
                "read_potfiles_cracked": self.read_potfiles_cracked,
                "handshake_count": self.handshake_count,
                "fetch_pwngrid_inbox": self.handle_pwngrid_inbox,
                "read_memtemp": self.handle_memtemp,
                "take_screenshot": self.take_screenshot,
                "pwnkill": self.pwnkill,
                "start": self.start,
                "soft_restart": self.soft_restart,
                "soft_restart_to_manual": self.soft_restart_to_manual,
                "soft_restart_to_auto": self.soft_restart_to_auto,
                "send_backup": self.send_backup,
                "bot_update": self.bot_update,
                "create_backup": self.last_backup,
            }

            action = action_map.get(str(query.data))
            if action:
                action(agent, update, context)

            self.completed_tasks += 1
            if self.completed_tasks == self.num_tasks:
                self.terminate_program()

    def handle_exception(self, update, context, e) -> None:
        if update.effective_chat.id == int(self.options.get("chat_id")):
            error_text = f"⛔ Unexpected error ocurred:\n<code>{e}</code>\nIf this keeps happening, please check the logs and submit an issue with screenshots to https://github.com/wpa-2/telegram.py"
            self.generate_log(error_text, "ERROR")
            self.send_sticker(update, context, random.choice(stickers_exception))
            self.send_new_message(update, context, error_text)

    def generate_log(self, text, type="INFO"):
        """Create a log with the plugin name"""
        log_map = {
            "INFO": logging.info,
            "ERROR": logging.error,
            "WARNING": logging.warning,
            "DEBUG": logging.debug,
        }
        log = log_map.get(type, logging.info)
        log(f"[{self.__class__.__name__}] {text}")

    def change_led(self, agent, update, context, mode="on"):
        # Write 0 or 255 to the led file to turn it off or on
        if update.effective_chat.id == int(self.options.get("chat_id")):
            led_map = {
                "on": "255",
                "off": "0",
            }
            led = led_map.get(mode, "255")
            try:
                with open("/sys/class/leds/ACT/brightness", "w") as f:
                    f.write(led)
                self.update_existing_message(
                    update, context, f"✅ LED turned {mode} correctly"
                )
            except Exception as e:
                self.handle_exception(update, context, e)

    def send_sticker(self, update, context, fileid):
        if update.effective_chat.id == int(self.options.get("chat_id")):
            user_id = update.effective_message.chat_id
            context.bot.send_sticker(chat_id=user_id, sticker=fileid)

    def split_message_into_list(self, text):
        list_of_messages = []
        self.generate_log(f"Splitting message: {text}", "DEBUG")
        while len(text) > max_length_message:
            list_of_messages.append(text[:max_length_message])
            text = text[max_length_message:]
        list_of_messages.append(text)
        return list_of_messages

    def send_new_message(
        self,
        update,
        context,
        text: str,
        keyboard: list = [],
    ):
        if update.effective_chat.id == int(self.options.get("chat_id")):
            try:
                keyboard = self.add_open_menu_button(keyboard)
                update.effective_message.reply_text(
                    text, parse_mode="HTML", reply_markup=InlineKeyboardMarkup(keyboard)
                )
            except Exception:
                try:
                    update.effective_message.reply_text(text)
                except Exception as e:
                    self.handle_exception(update, context, e)

    def add_lossing_html_tags(self, text):
        if "<code>" in text and "</code>" not in text:
            text += "</code>"
        if "<b>" in text and "</b>" not in text:
            text += "</b>"
        if "<i>" in text and "</i>" not in text:
            text += "</i>"
        if "</code>" in text and "<code>" not in text:
            text = "<code>" + text
        if "</b>" in text and "<b>" not in text:
            text = "<b>" + text
        if "</i>" in text and "<i>" not in text:
            text = "<i>" + text
        return text

    def update_existing_message(self, update, context, text, keyboard=[]):
        if update.effective_chat.id == int(self.options.get("chat_id")):
            if len(text) > max_length_message:
                self.generate_log(f"Message too long: {text}", "DEBUG")
                list_of_messages = self.split_message_into_list(text)
                self.generate_log(f"List of messages: {list_of_messages}", "DEBUG")
                self.send_long_messages(list_of_messages, update, context)
            else:
                text = self.add_lossing_html_tags(text)
                self.generate_log(f"Sending message: {text}", "DEBUG")
                keyboard = self.add_open_menu_button(keyboard)
                self.send_or_edit_message(update, context, text, keyboard)

    def send_long_messages(self, list_of_messages, update, context):
        if update.effective_chat.id == int(self.options.get("chat_id")):
            counter = 0
            for message in list_of_messages:
                self.generate_log(f"Sending message: {message}", "DEBUG")
                counter += 1
                if counter >= max_messages_per_minute - 1:
                    self.sleep_and_notify(update, context)
                    counter = 0
                self.update_existing_message(update, context, message)

    def sleep_and_notify(self, update, context):
        if update.effective_chat.id == int(self.options.get("chat_id")):
            response = (
                "💤 Sleeping for <b>60</b> seconds to avoid <i>flooding</i> the chat..."
            )
            self.send_new_message(update, context, response)
            sleep(60)

    def add_open_menu_button(self, keyboard):
        go_back_button = [
            InlineKeyboardButton("📲 Open Menu", callback_data="start"),
        ]
        if keyboard != main_menu and go_back_button not in keyboard:
            keyboard.append(go_back_button)
        return keyboard

    def send_or_edit_message(self, update, context, text, keyboard):
        if update.effective_chat.id == int(self.options.get("chat_id")):
            try:
                old_message = update.callback_query
                old_message.answer()
                old_message.edit_message_text(
                    text=text,
                    reply_markup=InlineKeyboardMarkup(keyboard),
                    parse_mode="HTML",
                )
            except Exception:
                self.send_new_message(update, context, text, keyboard)

    def run_as_user(self, cmd, user):
        uid = pwd.getpwnam(str(user)).pw_uid
        os.setuid(uid)
        os.system(cmd)
        os.setuid(0)
        return

    def bot_update(self, agent, update, context):
        if update.effective_chat.id == int(self.options.get("chat_id")):
            self.generate_log("Updating bot...", "INFO")
            response = "🆙 Updating bot..."
            self.update_existing_message(update, context, response)
            chat_id = update.effective_user["id"]
            context.bot.send_chat_action(chat_id=chat_id, action="upload_document")
            try:
                # Change directory to /home/pi
                os.chdir(home_dir)

                # Check if the telegram-bot folder exists
                if not os.path.exists("telegram-bot"):
                    # Clone the telegram-bot repository if it doesn't exist
                    self.generate_log("Cloning telegram-bot repository...", "DEBUG")
                    subprocess.run(
                        [
                            "git",
                            "clone",
                            "https://github.com/wpa-2/telegram.py",
                            "telegram-bot",
                        ],
                        check=True,
                    )

                    # Add the repository as a safe directory as root
                    self.generate_log(
                        "Adding telegram-bot repository as safe...", "DEBUG"
                    )
                    subprocess.run(
                        [
                            "git",
                            "config",
                            "--global",
                            "--add",
                            "safe.directory",
                            "/home/pi/telegram-bot",
                        ],
                        check=True,
                    )
                    # Add the repository as a safe directory as the pi user
                    self.generate_log(
                        "Adding telegram-bot repository as safe for pi...", "DEBUG"
                    )
                    self.run_as_user(
                        "git config --global --add safe.directory /home/pi/telegram-bot",
                        "pi",
                    )

                    # Delete the self.plugins_dir/telegram.py file if exists
                    if os.path.exists(f"{self.plugins_dir}/telegram.py"):
                        os.remove(f"{self.plugins_dir}/telegram.py")

                    # Create a symbolic link so when the bot is updated, the new version is used
                    subprocess.run(
                        [
                            "ln",
                            "-sf",
                            "/home/pi/telegram-bot/telegram.py",
                            self.plugins_dir,
                        ],
                        check=True,
                    )
                # Change directory to telegram-bot
                os.chdir("telegram-bot")

                # Pull the latest changes from the repository
                self.generate_log(
                    "Pulling latest changes from telegram-bot repository...", "INFO"
                )
                subprocess.run(["git", "pull"], check=True)

            except subprocess.CalledProcessError as e:
                # Handle errors
                logging.error(f"[{self.__class__.__name__}] Error updating bot: {e}")
                response = f"⛔ Error updating bot: <code>{e}</code>"
                update.effective_message.reply_text(response, parse_mode="HTML")
                return

            # Send a message indicating success
            response = "✅ Bot updated <b>successfully!</b>"
            self.update_existing_message(update, context, response)
            return

    def take_screenshot(self, agent, update, context):
        if update.effective_chat.id == int(self.options.get("chat_id")):
            try:
                chat_id = update.effective_user["id"]
                context.bot.send_chat_action(chat_id, "upload_photo")
                display = agent.view()
                picture_path = "/root/pwnagotchi_screenshot.png"

                # Capture screenshot
                screenshot = display.image()

                # Capture the screen rotation value and rotate the image (x degrees) before saving
                # If there is no rotation value, the default value is 0

                rotation_degree = self.screen_rotation

                rotated_screenshot = screenshot.rotate(rotation_degree)

                # Save the rotated image
                rotated_screenshot.save(picture_path, "png")

                with open(picture_path, "rb") as photo:
                    context.bot.send_photo(
                        chat_id=update.effective_chat.id, photo=photo
                    )

                response = "✅ Screenshot taken and sent!"
                self.update_existing_message(update, context, response)
            except Exception as e:
                self.handle_exception(update, context, e)

    def reboot(self, agent, update, context):
        if update.effective_chat.id == int(self.options.get("chat_id")):
            keyboard = [
                [
                    InlineKeyboardButton(
                        "🤖 Reboot to manual mode", callback_data="reboot_to_manual"
                    ),
                    InlineKeyboardButton(
                        "🛜 Reboot to auto mode", callback_data="reboot_to_auto"
                    ),
                ],
            ]

            text = "⚠️  This will restart the device, not the daemon.\nSSH or bluetooth will be interrupted\nPlease select an option:"
            self.update_existing_message(update, context, text, keyboard)
            return

    def reboot_to_manual(self, agent, update, context):
        if update.effective_chat.id == int(self.options.get("chat_id")):
            self.reboot_mode(mode="MANUAL", update=update, context=context)

    def reboot_to_auto(self, agent, update, context):
        if update.effective_chat.id == int(self.options.get("chat_id")):
            self.reboot_mode(mode="AUTO", update=update, context=context)

    def reboot_mode(self, mode, update, context):
        if update.effective_chat.id == int(self.options.get("chat_id")):
            if mode is not None:
                mode = mode.upper()
                reboot_text = f"🔄 rebooting in <b>{mode}</b> mode"
            else:
                reboot_text = "🔄 rebooting..."

            try:
                response = reboot_text
                self.generate_log(reboot_text, "WARNING")
                self.update_existing_message(update, context, response)

                if view.ROOT:
                    view.ROOT.on_custom("Rebooting...")
                    # give it some time to refresh the ui
                    sleep(10)

                if mode == "AUTO":
                    subprocess.run(["sudo", "touch", "/root/.pwnagotchi-auto"])
                elif mode == "MANU":
                    subprocess.run(["sudo", "touch", "/root/.pwnagotchi-manual"])

                self.generate_log("syncing...", "WARNING")

                for m in fs.mounts:
                    m.sync()

                self.generate_log("rebooting...", "INFO")
                subprocess.run(["sudo", "sync"])
                subprocess.run(["sudo", "reboot"])
            except Exception as e:
                self.handle_exception(update, context, e)

    def shutdown(self, agent, update, context):
        if update.effective_chat.id == int(self.options.get("chat_id")):
            response = "📴 Shutting down <b>now</b>..."
            self.update_existing_message(update, context, response)
            self.generate_log("shutting down...", "WARNING")

            try:
                if view.ROOT:
                    view.ROOT.on_shutdown()
                    # Give it some time to refresh the ui
                    sleep(10)

                self.generate_log("syncing...", "WARNING")

                for m in fs.mounts:
                    m.sync()

                subprocess.run(["sudo", "sync"])
                subprocess.run(["sudo", "halt"])
            except Exception as e:
                self.handle_exception(update, context, e)
            return

    def soft_restart(self, agent, update, context):
        if update.effective_chat.id == int(self.options.get("chat_id")):
            keyboard = [
                [
                    InlineKeyboardButton(
                        "🤖 Restart to manual mode",
                        callback_data="soft_restart_to_manual",
                    ),
                    InlineKeyboardButton(
                        "🛜 Restart to auto mode", callback_data="soft_restart_to_auto"
                    ),
                ],
            ]

            text = "⚠️  This will restart the daemon, not the device.\nSSH or bluetooth will not be interrupted\nPlease select an option:"
            self.update_existing_message(update, context, text, keyboard)
            return

    def soft_restart_to_manual(self, agent, update, context):
        if update.effective_chat.id == int(self.options.get("chat_id")):
            self.soft_restart_mode(mode="MANUAL", update=update, context=context)

    def soft_restart_to_auto(self, agent, update, context):
        if update.effective_chat.id == int(self.options.get("chat_id")):
            self.soft_restart_mode(mode="AUTO", update=update, context=context)

    def soft_restart_mode(self, mode, update, context):
        if update.effective_chat.id == int(self.options.get("chat_id")):
            self.generate_log(f"restarting in {mode} mode ...")
            response = f"🔃 Restarting in <b>{mode}</b> mode..."
            self.update_existing_message(update, context, response)

            if view.ROOT:
                view.ROOT.on_custom(f"Restarting daemon to {mode}")
                sleep(10)
            try:
                mode = mode.upper()
                if mode == "AUTO":
                    subprocess.run(["sudo", "touch", "/root/.pwnagotchi-auto"])
                else:
                    subprocess.run(["sudo", "touch", "/root/.pwnagotchi-manual"])

                subprocess.run(["sudo", "systemctl", "restart", "pwnagotchi"])
            except Exception as e:
                self.handle_exception(update, context, e)
            return

    def uptime(self, agent, update, context):
        if update.effective_chat.id == int(self.options.get("chat_id")):
            with open("/proc/uptime", "r") as f:
                uptime_seconds = float(f.readline().split()[0])

            uptime_minutes = uptime_seconds / 60
            uptime_hours = int(uptime_minutes // 60)
            uptime_remaining_minutes = int(uptime_minutes % 60)

            response = f"⏰ Uptime: {uptime_hours} hours and {uptime_remaining_minutes} minutes"
            self.update_existing_message(update, context, response)

            self.completed_tasks += 1
            if self.completed_tasks == self.num_tasks:
                self.terminate_program()
            return

    def pwnkill(self, agent, update, context):
        if update.effective_chat.id == int(self.options.get("chat_id")):
            try:
                response = "⏰ Sending <code>pwnkill</code> to pwnagotchi..."
                self.send_sticker(update, context, random.choice(stickers_kill_daemon))
                update.effective_message.reply_text(response, parse_mode="HTML")
                # TODO: Maybe it's better to use systemctl stop pwnagotchi? To turn it off gracefully?
                subprocess.run(["sudo", "killall", "-USR1", "pwnagotchi"])
            except subprocess.CalledProcessError as e:
                response = f"⛔ Error executing pwnkill command: <code>{e}</code>"
                update.effective_message.reply_text(response, parse_mode="HTML")

    def format_handshake_pot_files(self, file_path):
        try:
            messages_list = []
            message = ""

            try:
                with open(file_path, "r") as file:
                    content = file.readlines()
                    for line in content:
                        pwned = line.split(":")[2:]
                        if len(message + line) > max_length_message:
                            messages_list.append(message)
                            message = ""
                        # This code formatting allow us to copy the code block with one tap
                        # SSID:password
                        message += ":<code>".join(pwned)
                        message = message + "</code>"
                    messages_list.append(message)
            except FileNotFoundError:
                return [f"⛔ The {file_path} does not exists."]
            except:
                return ["⛔ Unexpected error reading file."]
            return messages_list

        except subprocess.CalledProcessError as e:
            return [f"⛔ Error reading file: {e}"]

    def read_potfiles_cracked(self, agent, update, context):
        if update.effective_chat.id == int(self.options.get("chat_id")):
            potfiles_dir = "/root/handshakes"
            potfiles_list = os.listdir(potfiles_dir)
            potfiles_list = [
                file for file in potfiles_list if file.endswith(".potfile")
            ]

            if not potfiles_list:
                self.update_existing_message(
                    text="⛔ No cracked potfile found.", context=context, update=update
                )
                return

            for potfile in potfiles_list:
                file_path = f"{potfiles_dir}/{potfile}"
                chunks = self.format_handshake_pot_files(file_path)
                if not chunks or not any(chunk.strip() for chunk in chunks):
                    self.update_existing_message(
                        text=f"The {potfile} file is empty.",
                        context=context,
                        update=update,
                    )
                else:
                    self.send_sticker(
                        update, context, random.choice(stickers_handshake_or_wpa)
                    )
                    chat_id = update.effective_user["id"]
                    context.bot.send_chat_action(chat_id, "typing")
                    import time

                    message_counter = 0
                    for chunk in chunks:
                        if message_counter >= max_messages_per_minute:
                            response = "💤 Sleeping for <b>60</b> seconds to avoid <i>flooding</i> the chat..."
                            self.send_new_message(
                                update=update, context=context, text=response
                            )
                            time.sleep(60)
                            context.bot.send_chat_action(chat_id, "typing", timeout=60)
                            message_counter = 0
                        self.send_new_message(
                            update=update,
                            context=context,
                            text=f"<b>{potfile}</b>:\n{chunk}",
                        )
                        message_counter += 1

            self.completed_tasks += 1
            if self.completed_tasks == self.num_tasks:
                self.terminate_program()

    def handshake_count(self, agent, update, context):
        if update.effective_chat.id == int(self.options.get("chat_id")):
            handshake_dir = "/root/handshakes/"
            count = len(
                [
                    name
                    for name in os.listdir(handshake_dir)
                    if os.path.isfile(os.path.join(handshake_dir, name))
                ]
            )

            response = f"🤝 Total handshakes captured: <b>{count}</b>"
            self.send_sticker(update, context, random.choice(stickers_handshake_or_wpa))
            self.send_new_message(update, context, response)
            self.completed_tasks += 1
            if self.completed_tasks == self.num_tasks:
                self.terminate_program()
            return

    def fetch_inbox(self):
        command = "sudo pwngrid -inbox"
        output = subprocess.check_output(command, shell=True).decode("utf-8")
        lines = output.split("\n")
        formatted_output = []
        for line in lines:
            if "│" in line:
                message = line.split("│")[1:4]
                formatted_message = (
                    "ID: "
                    + message[0].strip().replace("\x1b[2m", "").replace("\x1b[0m", "")
                    + "\n"
                    + "Date: "
                    + message[1].strip().replace("\x1b[2m", "").replace("\x1b[0m", "")
                    + "\n"
                    + "Sender: "
                    + message[2].strip().replace("\x1b[2m", "").replace("\x1b[0m", "")
                )
                formatted_output.append(formatted_message)

        if len(formatted_output) > 0:
            formatted_output.pop(0)

        return "\n".join(formatted_output)

    def handle_pwngrid_inbox(self, agent, update, context):
        if update.effective_chat.id == int(self.options.get("chat_id")):
            chat_id = update.effective_chat.id
            context.bot.send_chat_action(chat_id, "typing")
            reply = self.fetch_inbox()
            if reply:
                context.bot.send_message(chat_id=chat_id, text=reply)
            else:
                context.bot.send_message(
                    chat_id=chat_id,
                    text="📬 No messages found in Pwngrid inbox.",
                )

    def comming_soon(self, update, context):
        if update.effective_chat.id == int(self.options.get("chat_id")):
            response = "🚧 Comming soon..."
            self.update_existing_message(update, context, response)
            return

    def join_context_args(self, context):
        args = context.args
        if args:
            return " ".join(args[:])
        else:
            return None

    def rot13(self, agent, update, context):
        """Encode/Decode ROT13"""
        if update.effective_chat.id == int(self.options.get("chat_id")):
            try:
                args = self.join_context_args(context)
                if args:
                    rot13_text = codecs.encode(args, "rot_13")
                    response = f"🔠 ROT13: <code>{rot13_text}</code>"
                else:
                    response = "⛔ No text provided to encode/decode with ROT13.\nUsage: /rot13 <code>text</code>"
                self.update_existing_message(update, context, response)
            except Exception as e:
                self.handle_exception(update, context, e)
            return

    def debase64(self, agent, update, context):
        """Decode Base64"""
        if update.effective_chat.id == int(self.options.get("chat_id")):
            try:
                args = self.join_context_args(context)
                if args:
                    base64_text = base64.b64decode(args).decode()
                    response = f"🔠 Base64: <code>{base64_text}</code>"
                else:
                    response = "⛔ No text provided to decode from Base64.\nUsage: /debase64 <code>base64 encode text</code>"
                self.update_existing_message(update, context, response)
            except Exception as e:
                self.handle_exception(update, context, e)
            return

    def base64(self, agent, update, context):
        """Encode Base64"""
        if update.effective_chat.id == int(self.options.get("chat_id")):
            try:
                args = self.join_context_args(context)
                if args:
                    base64_text = base64.b64encode(args.encode()).decode()
                    response = f"🔠 Base64: <code>{base64_text}</code>"
                else:
                    response = "⛔ No text provided to encode to Base64.\nUsage: /base64 <code>text to base64 encode</code>"
                self.update_existing_message(update, context, response)
            except Exception as e:
                self.handle_exception(update, context, e)
            return

    def sanitize_text_to_send(self, text):
        """Sanitize some characters so we don't break the html format"""
        return (
            text.replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace("&", "&amp;")
            .replace("_", "\\_")
            .replace("*", "\\*")
            .replace("`", "\\`")
        )

    def command_executed(self, update, context):
        """Execute a command on the pwnagotchi"""
        if update.effective_chat.id == int(self.options.get("chat_id")):
            try:
                args = self.join_context_args(context)
                if args:
                    chat_id = update.effective_user["id"]
                    context.bot.send_chat_action(chat_id, "typing")
                    # Execute the  args provided and send the output to the chat
                    output = subprocess.check_output(args, shell=True).decode("utf-8")
                    response = f"🔠 ~>$: <code>{args}</code>\n\n📜 ~>$: <code>{self.sanitize_text_to_send(output)}</code>"
                else:
                    response = "⛔ No command provided to execute.\nUsage: /cmd <code>command</code>"
                self.update_existing_message(update, context, response)
            except Exception as e:
                self.handle_exception(update, context, e)
            return

    def kill_ps(self, agent, update, context):
        """Kill a process by id"""
        if update.effective_chat.id == int(self.options.get("chat_id")):
            try:
                args = self.join_context_args(context)
                if args:
                    try:
                        subprocess.run(["sudo", "kill", "-9", args])
                        response = f"🔠 Process <code>{args}</code> killed."
                    except subprocess.CalledProcessError as e:
                        response = f"⛔ Error killing process <code>{args}</code>: <code>{e}</code>"
                    except Exception as e:
                        response = f"⛔ Unexpected error killing process <code>{args}</code>: <code>{e}</code>"
                        self.generate_log(response, "ERROR")
                else:
                    response = "⛔ No process id provided to kill.\nUsage: /kill_ps <code>process_id</code>"
                self.update_existing_message(update, context, response)
            except Exception as e:
                self.handle_exception(update, context, e)
            return

    def kill_ps_name(self, agent, update, context):
        """Kill a process by name"""
        if update.effective_chat.id == int(self.options.get("chat_id")):
            try:
                args = self.join_context_args(context)
                if args:
                    try:
                        subprocess.run(["sudo", "pkill", args])
                        response = f"🔠 Process <code>{args}</code> killed."
                    except subprocess.CalledProcessError as e:
                        response = f"⛔ Error killing process <code>{args}</code>: <code>{e}</code>"
                    except Exception as e:
                        response = f"⛔ Unexpected error killing process <code>{args}</code>: <code>{e}</code>"
                        self.generate_log(response, "ERROR")
                else:
                    response = "⛔ No process name provided to kill.\nUsage: /kill_ps_name <code>process_name</code>"
                self.update_existing_message(update, context, response)
            except Exception as e:
                self.handle_exception(update, context, e)
            return

    def help(self, update, context):
        if update.effective_chat.id == int(self.options.get("chat_id")):
            list_of_commands_with_descriptions = """
<b><u> Telegram Bot Commands </u></b>

/start - See buttons menu
/menu - See buttons menu
/bot_update - Update the bot
/help - Show this message

<b><u> Hacker commands </u></b>

/rot13 <code>text</code> - Encode/Decode ROT13
/debase64 <code>text</code> - Decode Base64
/base64 <code>text</code> - Encode Base64

<b><u> System commands </u></b>

/reboot_to_manual - Reboot the device to manual mode
/reboot_to_auto - Reboot the device to auto mode
/shutdown - Shutdown the device
/read_memtemp - Read memory and temperature
/uptime - Get the uptime of the device
/cmd <code>command</code> - Run a command (As sudo)
/kill_ps <code>ps</code> - Kill a process (By id)
/kill_ps_name <code>ps</code> - Kill a process (By name)

<b><u> Pwnagotchi commands </u></b>

/send_backup - Send the backup if it is available
/fetch_pwngrid_inbox - Fetch the Pwngrid inbox
/handshake_count - Get the handshake count
/read_potfiles_cracked - Read the all the cracked .potfile's
/take_screenshot - Take a screenshot
/create_backup - Create a backup

<b><u> Daemon commands </u></b>

/pwnkill - Kill the daemon
/soft_restart_to_manual - Restart the daemon to manual mode
/soft_restart_to_auto - Restart the daemon to auto mode
        """
            self.update_existing_message(
                update, context, list_of_commands_with_descriptions
            )
            return

    def on_internet_available(self, agent):
        if hasattr(self, "telegram_connected") and self.telegram_connected:
            return

        config = agent.config()
        display = agent.view()
        last_session = agent.last_session

        try:
            self.generate_log("Connecting to Telegram...", "INFO")
            bot = telegram.Bot(self.options["bot_token"])
            bot.set_my_commands(
                commands=[
                    # Add all the buttons actions as commands
                    BotCommand(command="menu", description="See buttons menu"),
                    BotCommand(
                        command="reboot_to_manual",
                        description="Reboot the device to manual mode",
                    ),
                    BotCommand(
                        command="reboot_to_auto",
                        description="Reboot the device to auto mode",
                    ),
                    BotCommand(command="shutdown", description="Shutdown the device"),
                    BotCommand(
                        command="uptime", description="Get the uptime of the device"
                    ),
                    BotCommand(
                        command="handshake_count", description="Get the handshake count"
                    ),
                    BotCommand(
                        command="read_potfiles_cracked",
                        description="Read the every cracked .potfile",
                    ),
                    BotCommand(
                        command="fetch_pwngrid_inbox",
                        description="Fetch the Pwngrid inbox",
                    ),
                    BotCommand(
                        command="read_memtemp",
                        description="Read memory and temperature",
                    ),
                    BotCommand(
                        command="take_screenshot", description="Take a screenshot"
                    ),
                    BotCommand(command="create_backup", description="Create a backup"),
                    BotCommand(command="bot_update", description="Update the bot"),
                    BotCommand(command="pwnkill", description="Kill the daemon"),
                    BotCommand(
                        command="soft_restart_to_manual",
                        description="Restart the daemon to manual mode",
                    ),
                    BotCommand(
                        command="soft_restart_to_auto",
                        description="Restart the daemon to auto mode",
                    ),
                    BotCommand(
                        command="send_backup",
                        description="Send the backup if it is available",
                    ),
                    BotCommand(
                        command="help",
                        description="Get the list of available commands and their descriptions",
                    ),
                    BotCommand(
                        command="rot13",
                        description="Encode/Decode ROT13",
                    ),
                    BotCommand(command="debase64", description="Decode Base64"),
                    BotCommand(command="base64", description="Encode Base64"),
                    BotCommand(command="cmd", description="Run a command (As sudo)"),
                    BotCommand(command="kill_ps", description="Kill a process (By id)"),
                    BotCommand(
                        command="kill_ps_name", description="Kill a process (By name)"
                    ),
                    BotCommand(
                        command="turn_led_on", description="Turn the ACT led on"
                    ),
                    BotCommand(
                        command="turn_led_off", description="Turn the ACT led off"
                    ),
                ],
                scope=telegram.BotCommandScopeAllPrivateChats(),
            )
            if self.updater is None:
                self.updater = Updater(
                    token=self.options["bot_token"], use_context=True
                )
                self.register_command_handlers(agent, self.updater.dispatcher)
                self.updater.start_polling()

            if not self.start_menu_sent:
                try:
                    self.options["bot_name"]
                except:
                    self.options["bot_name"] = "Pwnagotchi"

                bot_name = self.options["bot_name"]
                response = (
                    f"🖖 Welcome to <b>{bot_name}!</b>\n\nPlease select an option:"
                )
                reply_markup = InlineKeyboardMarkup(main_menu)
                bot.send_message(
                    chat_id=int(self.options["chat_id"]),
                    text=response,
                    reply_markup=reply_markup,
                    parse_mode="HTML",
                )
                self.start_menu_sent = True

            self.telegram_connected = True

        except Exception as e:
            self.logger.error("Error while sending on Telegram")
            self.logger.error(str(e))

        if last_session.is_new() and last_session.handshakes > 0:
            msg = f"Session started at {last_session.started_at()} and captured {last_session.handshakes} new handshakes"
            self.send_notification(msg)

            if last_session.is_new() and last_session.handshakes > 0:
                message = Voice(lang=config["main"]["lang"]).on_last_session_tweet(
                    last_session
                )
                if self.options["send_message"] is True:
                    bot.sendMessage(
                        chat_id=int(self.options["chat_id"]),
                        text=message,
                        disable_web_page_preview=True,
                    )
                    self.logger.info("telegram: message sent: %s" % message)

                picture = "/root/pwnagotchi.png"
                display.on_manual_mode(last_session)
                display.image().save(picture, "png")
                display.update(force=True)

                if self.options["send_picture"] is True:
                    bot.sendPhoto(
                        chat_id=int(self.options["chat_id"]), photo=open(picture, "rb")
                    )
                    self.logger.info("telegram: picture sent")

                last_session.save_session_id()
                display.set("status", "Telegram notification sent!")
                display.update(force=True)

    def handle_memtemp(self, agent, update, context):
        if update.effective_chat.id == int(self.options.get("chat_id")):
            reply = f"Memory Usage: {int(pwnagotchi.mem_usage() * 100)}%\n\nCPU Load: {int(pwnagotchi.cpu_load() * 100)}%\n\nCPU Temp: {pwnagotchi.temperature()}c"
            self.update_existing_message(update, context, reply)
            return

    def create_backup(self, agent, update, context):
        if update.effective_chat.id == int(self.options.get("chat_id")):
            context.bot.send_chat_action(
                chat_id=update.effective_chat.id, action="typing"
            )
            backup_files = [
                "/root/brain.json",
                "/root/.api-report.json",
                "/root/handshakes/",
                "/root/peers/",
                "/etc/pwnagotchi/",
                "/var/log/pwnagotchi.log",
            ]

            # Get datetime

            from datetime import datetime

            current_time = datetime.now()
            formatted_time = current_time.strftime("%Y-%m-%d-%H:%M:%S")

            backup_file_name = f"pwnagotchi-backup-{formatted_time}.tar.gz"
            backup_tar_path = f"/root/{backup_file_name}"

            try:
                # Create a tarball
                subprocess.run(["sudo", "tar", "czf", backup_tar_path] + backup_files)

                # Move the tarball to /home/pi/
                subprocess.run(["sudo", "mv", backup_tar_path, "/home/pi/"])

                self.generate_log("Backup created and moved successfully.", "DEBUG")

            except Exception as e:
                self.handle_exception(update, context, e)

            # Obtain the file size

            # Get the size on bytes
            file_size = os.path.getsize(f"/home/pi/{backup_file_name}")
            # Convert to mb
            file_size /= 1024 * 1024
            # Round to 2 decimal places
            file_size = round(file_size, 2)
            keyboard = [
                [
                    InlineKeyboardButton(
                        "📤 Send me the backup here", callback_data="send_backup"
                    ),
                ],
            ]

            response = f"✅ Backup created and moved successfully to <code>/home/pi</code>.\nFile size: <b>{file_size} MB</b>"
            self.update_existing_message(update, context, response, keyboard)
            self.completed_tasks += 1
            if self.completed_tasks == self.num_tasks:
                self.terminate_program()
            self.last_backup = backup_file_name

    def send_backup(self, agent, update, context):
        if update.effective_chat.id == int(self.options.get("chat_id")):
            chat_id = update.effective_user["id"]
            context.bot.send_chat_action(chat_id, "upload_document")

            try:
                backup = self.last_backup
                if backup:
                    self.generate_log(f"Sending backup: {backup}", "DEBUG")
                    backup_path = f"/home/pi/{backup}"
                    with open(backup_path, "rb") as backup_file:
                        update.effective_chat.send_document(document=backup_file)
                    update.effective_message.reply_text("Backup sent successfully.")
                else:
                    self.generate_log("No backup file found.", "ERROR")
                    update.effective_message.reply_text("No backup file found.")
            except Exception as e:
                self.handle_exception(update, context, e)

    def on_handshake(self, agent, filename, access_point, client_station):
        config = agent.config()
        display = agent.view()

        try:
            self.logger.info("Connecting to Telegram...")

            bot = telegram.Bot(self.options["bot_token"])

            message = f"🤝 New handshake captured: {access_point['hostname']} - {client_station['mac']}"
            if self.options["send_message"] is True:
                bot.sendMessage(
                    chat_id=int(self.options["chat_id"]),
                    text=message,
                    disable_web_page_preview=True,
                )
                self.logger.info("telegram: message sent: %s" % message)

            display.set("status", "Telegram notification sent!")
            display.update(force=True)
            # TODO: Add button and option to send the handshake file!
        except Exception:
            self.logger.exception("Error while sending on Telegram")

    def terminate_program(self):
        self.generate_log("All tasks completed. Terminating program.", "INFO")


if __name__ == "__main__":
    plugin = Telegram_ng()
    plugin.on_loaded()
