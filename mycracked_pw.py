import pwnagotchi.plugins as plugins
import pwnagotchi
import logging
import qrcode
import csv
import os
import io


class MyCrackedPasswords(plugins.Plugin):
    __GitHub__ = ""
    __author__ = "(edited by: itsdarklikehell bauke.molenaar@gmail.com), @silentree12th"
    __version__ = "5.2.3"
    __license__ = "GPL3"
    __description__ = "A plugin to grab all cracked passwords and creates wifi qrcodes and a wordlist which can be used for the quickdic plugin. It stores them in the home directory. Read with cat"
    __name__ = "MyCrackedPasswords"
    __help__ = "A plugin to grab all cracked passwords and creates wifi qrcodes and a wordlist which can be used for the quickdic plugin. It stores them in the home directory. Read with cat"
    __dependencies__ = {
        "apt": ["none"],
        "pip": ["scapy"],
    }
    __defaults__ = {
        "enabled": False,
    }

    def on_loaded(self):
        logging.info(f"[{self.__class__.__name__}] plugin loaded")
        if not os.path.exists("/etc/pwnagotchi/wordlists/passwords/"):
            os.makedirs("/etc/pwnagotchi/wordlists/passwords/")
        if not os.path.exists("/home/pi/qrcodes/"):
            os.makedirs("/home/pi/qrcodes/")
        self._update_all()

    def on_handshake(self, agent, filename, access_point, client_station):
        self._update_all()

    def _update_all(self):
        all_passwd = []
        all_bssid = []
        all_ssid = []

        try:
            f = open("/root/handshakes/wpa-sec.cracked.potfile",
                     "r+", encoding="utf-8")
            for line_f in f:
                pwd_f = line_f.split(":")
                all_passwd.append(str(pwd_f[-1].rstrip("\n")))
                all_bssid.append(str(pwd_f[0]))
                all_ssid.append(str(pwd_f[-2]))
            f.close()
        except Exception as e:
            logging.error(
                f"[{self.__class__.__name__}] encountered a problem in wpa-sec.cracked.potfile:\n{e}"
            )

        try:
            h = open("/root/handshakes/onlinehashcrack.cracked",
                     "r+", encoding="utf-8")
            for line_h in csv.DictReader(h):
                pwd_h = str(line_h["password"])
                task_h = str(line_h["task"])
                ssid_h = task_h[0:-20]
                bssid_h = task_h[-18:-1]
                if pwd_h and ssid_h and bssid_h:
                    all_passwd.append(pwd_h)
                    all_bssid.append(bssid_h)
                    all_ssid.append(ssid_h)
            h.close()
        except Exception as e:
            logging.error(
                f"[{self.__class__.__name__}] encountered a problem in onlinehashcrack.cracked:\n{e}"
            )

        # save all the wifi-qrcodes
        security = "WPA"
        for ssid, password in zip(all_ssid, all_passwd):

            filename = ssid + "-" + password + ".txt"
            filepath = "/home/pi/qrcodes/" + filename

            if os.path.exists(filepath):
                continue

            wifi_config = "WIFI:S:" + ssid + ";T:" + security + ";P:" + password + ";;"

            # Create the QR code object
            qr_code = qrcode.QRCode(
                version=None,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            qr_code.add_data(wifi_config)
            qr_code.make(fit=True)

            try:
                with open(filepath, "w+") as file:
                    qr_code.print_ascii(out=file)
                    q = io.StringIO()
                    qr_code.print_ascii(out=q)
                    q.seek(0)
                    logging.info(filename)
                    logging.info(q.read())
            except:
                logging.error(
                    f"[{self.__class__.__name__}] something went wrong generating qrcode"
                )
            logging.info(f"[{self.__class__.__name__}] qrcode generated.")

            # start with blank file
            open("/etc/pwnagotchi/wordlists/passwords/mycracked.txt", "w+").close()

            # create pw list
            new_lines = sorted(set(all_passwd))
            with open("/etc/pwnagotchi/wordlists/passwords/mycracked.txt", "w+") as g:
                for i in new_lines:
                    g.write(i + "\n")

            logging.info(f"[{self.__class__.__name__}] pw list updated")

    def on_unload(self, ui):
        with ui._lock:
            logging.info(f"[{self.__class__.__name__}] plugin unloaded")

    def on_webhook(self, path, request):
        logging.info(f"[{self.__class__.__name__}] webhook pressed")
        self._update_all()
        pass
