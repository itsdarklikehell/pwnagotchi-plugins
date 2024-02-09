# display-password shows recently cracked passwords on the pwnagotchi display as a qrcode.
#
#
###############################################################
#
# Inspired by, and code shamelessly yoinked from
# the pwnagotchi memtemp.py plugin by https://github.com/xenDE
#
###############################################################
import pwnagotchi
import logging
import os
import logging
import json
import glob
from pwnagotchi.ui.components import LabeledValue
from pwnagotchi.ui.view import BLACK
import pwnagotchi.ui.fonts as fonts
import pwnagotchi.plugins as plugins


TEMPLATE = """
{% extends "base.html" %}
{% set active_page = "qr-password" %}

{% block title %}
    {{ title }}
{% endblock %}

{% block styles %}
    {{ super() }}
    <style>
        #filter {
            width: 100%;
            font-size: 16px;
            padding: 12px 20px 12px 40px;
            border: 1px solid #ddd;
            margin-bottom: 12px;
        }
    </style>
{% endblock %}
{% block script %}
    var shakeList = document.getElementById('list');
    var filter = document.getElementById('filter');
    var filterVal = filter.value.toUpperCase();

    filter.onkeyup = function() {
        document.body.style.cursor = 'progress';
        var table, tr, tds, td, i, txtValue;
        filterVal = filter.value.toUpperCase();
        li = shakeList.getElementsByTagName("li");
        for (i = 0; i < li.length; i++) {
            txtValue = li[i].textContent || li[i].innerText;
            if (txtValue.toUpperCase().indexOf(filterVal) > -1) {
                li[i].style.display = "list-item";
            } else {
                li[i].style.display = "none";
            }
        }
        document.body.style.cursor = 'default';
    }

{% endblock %}

{% block content %}
    <input type="text" id="filter" placeholder="Search for ..." title="Type in a filter">
    <ul id="list" data-role="listview" style="list-style-type:disc;">
        {% for handshake in handshakes %}
            <li class="file">
                <a href="/home/pi/qrcodes/{{handshake}}">{{handshake}}</a>
            </li>
        {% endfor %}
    </ul>
{% endblock %}
"""


class DisplayPassword(plugins.Plugin):
    __author__ = "(edited by: itsdarklikehell bauke.molenaar@gmail.com), @nagy_craig"
    __version__ = "1.0.0"
    __license__ = "GPL3"
    __description__ = "A plugin to display recently cracked passwords"
    __name__ = "DisplayPassword"
    __help__ = "A plugin to display recently cracked passwords"
    __dependencies__ = {
        "apt": ["none"],
        "pip": ["scapy"],
    }
    __defaults__ = {
        "enabled": False,
        "orientation": "horizontal",
        "potfile": "/root/handshakes/wpa-sec.cracked.potfile",
    }

    def __init__(self):
        self.ready = False
        logging.debug(f"[{self.__class__.__name__}] plugin init")
        self.title = ""

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

    def on_loaded(self):
        logging.info(f"[{self.__class__.__name__}] plugin loaded")
        if not os.path.exists("/etc/pwnagotchi/wordlists/passwords/"):
            os.makedirs("/etc/pwnagotchi/wordlists/passwords/")
        if not os.path.exists("/home/pi/qrcodes/"):
            os.makedirs("/home/pi/qrcodes/")
        self._update_all()

    def on_ui_setup(self, ui):
        if ui.is_waveshare_v2():
            h_pos = (0, 95)
            v_pos = (180, 61)
        elif ui.is_waveshare_v1():
            h_pos = (0, 95)
            v_pos = (170, 61)
        elif ui.is_waveshare144lcd():
            h_pos = (0, 92)
            v_pos = (78, 67)
        elif ui.is_inky():
            h_pos = (0, 83)
            v_pos = (165, 54)
        elif ui.is_waveshare27inch():
            h_pos = (0, 153)
            v_pos = (216, 122)
        elif ui.is_waveshare35lcd():
            h_pos = (0, 150)
            v_pos = (200, 152)
        else:
            h_pos = (0, 91)
            v_pos = (180, 61)

        if self.options["orientation"] == "vertical":
            ui.add_element(
                "display-password",
                LabeledValue(
                    color=BLACK,
                    label="",
                    value="",
                    position=v_pos,
                    label_font=fonts.Bold,
                    text_font=fonts.Small,
                ),
            )
        else:
            # default to horizontal
            ui.add_element(
                "display-password",
                LabeledValue(
                    color=BLACK,
                    label="",
                    value="",
                    position=h_pos,
                    label_font=fonts.Bold,
                    text_font=fonts.Small,
                ),
            )

    def on_unload(self, ui):
        with ui._lock:
            try:
                ui.remove_element("display-password")
                logging.info(f"[{self.__class__.__name__}] plugin unloaded")
            except Exception as e:
                logging.error(f"[{self.__class__.__name__}] unload: %s" % e)

    def on_ui_update(self, ui):
        last_line = "tail -n 1 /root/handshakes/wpa-sec.cracked.potfile | awk -F: '{print $3 \" - \" $4}'"
        ui.set("display-password", "%s" %
               (os.popen(last_line).read().rstrip()))

    def on_webhook(self, ui, path, request):
        logging.info(f"[{self.__class__.__name__}] webhook pressed")
        last_line = "tail -n 1 /root/handshakes/wpa-sec.cracked.potfile | awk -F: '{print $3 \" - \" $4}'"
        ui.set("display-password", "%s" %
               (os.popen(last_line).read().rstrip()))
