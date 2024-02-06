import os
import logging
import subprocess
import string
import re
import pwnagotchi.plugins as plugins
import qrcode
import io
import os

# from telegram import Bot  # install with pip install python-telegram-bot

"""
Aircrack-ng needed, to install:
> apt-get install aircrack-ng
Upload wordlist with this name mini-8.txt to home file (/home/pi/mini-8.txt)
Cracked and failed handshakes are stored in /home/pi/wpa-sec.cracked.potfile 
Please check that these two file a present
"""


class QuickDic(plugins.Plugin):
    __author__ = "pwnagotchi [at] rossmarks [dot] uk"
    __modified_by__ = "@7h30th3r0n3"
    __version__ = "1.0.0"
    __license__ = "GPL3"
    __description__ = "Run a small aircrack scan against captured handshakes and PMKID"
    __dependencies__ = {
        "apt": ["aircrack-ng"],
    }
    __defaults__ = {
        "enabled": False,
        "wordlist_folder": "/etc/pwnagotchi/wordlists/passwords/",
        "face": "(·ω·)",
        "api": None,
        "id": None,
    }

    def __init__(self):
        self.text_to_set = ""

    def on_loaded(self):
        logging.info("[quickdic] quickdic plugin loaded")

    def on_loaded(self):
        logging.info("[better_quickdic] plugin loaded")

        if "face" not in self.options:
            self.options["face"] = "(·ω·)"
        if "wordlist_folder" not in self.options:
            self.options["wordlist_folder"] = "/etc/pwnagotchi/wordlists/passwords/"
        if "enabled" not in self.options:
            self.options["enabled"] = False
        if "api" not in self.options:
            self.options["api"] = None
        if "id" not in self.options:
            self.options["id"] = None

        check = subprocess.run(
            ("/usr/bin/dpkg -l aircrack-ng | grep aircrack-ng | awk '{print $2, $3}'"),
            shell=True,
            stdout=subprocess.PIPE,
        )
        check = check.stdout.decode("utf-8").strip()
        if check != "aircrack-ng <none>":
            logging.info("[quickdic] Found %s" % check)
        else:
            logging.warning("[quickdic] aircrack-ng is not installed!")

        # if self.options['id'] != None and self.options['api'] != None:
        # self._send_message(filename='Android AP', pwd='12345678')

    def on_handshake(self, agent, filename, access_point, client_station):
        display = agent.view()
        result = subprocess.run(
            (
                "/usr/bin/aircrack-ng "
                + filename
                + " | grep \"1 handshake\" | awk '{print $2}'"
            ),
            shell=True,
            stdout=subprocess.PIPE,
        )
        result = result.stdout.decode("utf-8").translate(
            {ord(c): None for c in string.whitespace}
        )
        if not result:
            logging.info("[quickdic] No handshake")
        else:
            logging.info("[quickdic] Handshake confirmed")
            result2 = subprocess.run(
                (
                    "aircrack-ng -w `echo "
                    + self.options["wordlist_folder"]
                    + "*.txt | sed 's/ /,/g'` -l "
                    + filename
                    + ".cracked -q -b "
                    + result
                    + " "
                    + filename
                    + " | grep KEY"
                ),
                shell=True,
                stdout=subprocess.PIPE,
            )
            result2 = result2.stdout.decode("utf-8").strip()
            logging.info("[quickdic] %s" % result2)
            if result2 != "KEY NOT FOUND":
                key = re.search(r"\[(.*)\]", result2)
                pwd = str(key.group(1))
                self.text_to_set = "Cracked password: " + pwd
                # logging.warning('!!! [quickdic] !!! %s' % self.text_to_set)
                display.set("face", self.options["face"])
                display.set("status", self.text_to_set)
                self.text_to_set = ""
                display.update(force=True)
                # plugins.on('cracked', access_point, pwd)
                if self.options["id"] != None and self.options["api"] != None:
                    self._send_message(filename, pwd)

    def _send_message(self, filename, pwd):
        try:
            security = "WPA"
            filename = filename
            base_filename = os.path.splitext(os.path.basename(filename))[0]
            ssid = base_filename.split("_")[0:-2]
            password = pwd
            wifi_config = "WIFI:S:" + ssid + ";T:" + security + ";P:" + password + ";;"
            # bot = Bot(token=self.options["api"])
            chat_id = int(self.options["id"])

            qr = qrcode.QRCode(
                version=None,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            qr.add_data(wifi_config)
            qr.make(fit=True)

            # Create an image from the QR code instance
            # img = qr.make_image(fill_color="black", back_color="white")
            q = io.StringIO()
            qr.print_ascii(out=q)
            q.seek(0)

            # Convert the image to bytes
            # image_bytes = io.BytesIO()
            # img.save(image_bytes)
            # image_bytes.seek(0)

            # Send the image directly as bytes
            # message_text = 'ssid: ' + ssid + ' password: ' + password
            # bot.send_photo(chat_id=chat_id, photo=InputFile(image_bytes, filename=ssid+'-'+password+'.txt'), caption=message_text)
            message_text = f"\nSSID: {ssid}\nPassword: {password}\n```\n{q.read()}\n```"
            # bot.send_message(chat_id=chat_id, text=message_text, parse_mode="Markdown")
            logging.info(message_text)
            logging.info("[better_quickdic] QR code content sent to Telegram.")

        except Exception as e:
            logging.error(
                f"[better_quickdic] Error sending QR code content to Telegram: {str(e)}"
            )

    def on_ui_update(self, ui):
        if self.text_to_set:
            ui.set("face", self.options["face"])
            ui.set("status", self.text_to_set)
            self.text_to_set = ""
