# Crack_house
#
# Inspiration:
# educational-purposes-only.py
# by @cnagy
# https://github.com/c-nagy/pwnagotchi-educational-purposes-only-plugin/blob/main/educational-purposes-only.py
#
# display-password.py
# by @abros0000
# https://github.com/abros0000/pwnagotchi-display-password-plugin/blob/master/display-password.py
#
# If their is no cracked network nearby the plugins show the last cracked password by wpa-sec
# If cracked networks are nearby it will she the nearest on the screen
# It can show time from the last wifi update and the number of cracked networks nearby on the total number of cracked networks ('display_stats' option)
#
# Inside config.toml:
# ```
# main.plugins.crack_house.enabled = true
# main.plugins.crack_house.orientation = "vertical"
# main.plugins.crack_house.files = [
#  '/root/handshakes/wpa-sec.cracked.potfile',
#  '/root/handshakes/my.potfile',
#  '/root/handshakes/OnlineHashCrack.cracked',
# ]
# main.plugins.crack_house.saving_path = '/root/handshakes/crack_house.potfile'
# main.plugins.crack_house.display_stats = true
# ```
# The plugin manage .potfile from wpa-sec & .cracked from OnlineHashCrack
# .potfile
# BSSID:STAMAC:ESSID:password
# .cracked
# datetime,ESSID,BSSID,STAMAC,password,note

from pwnagotchi.ui.components import LabeledValue
from pwnagotchi.ui.view import BLACK
import pwnagotchi.ui.fonts as fonts
import pwnagotchi.plugins as plugins
import pwnagotchi
import logging
import os
import subprocess
import requests
import time
from pwnagotchi.ai.reward import RewardFunction

READY = 0

# the list with hostname:password without duplicate for the plugin
CRACK_MENU = list()

BEST_RSSI = -1000
BEST_CRACK = [""]

TOTAL_CRACK = 0

TIME_WIFI_UPDATE = "00:00"


class crack_house(plugins.Plugin):
    __author__ = "SgtStroopwafel, @V0rT3x"
    __version__ = "1.0.0"
    __license__ = "GPL3"
    __description__ = "A plugin to display closest cracked network & it password."
    __name__ = "crack_house"
    __help__ = "A plugin to display closest cracked network & it password."
    __dependencies__ = {
        "apt": ["none"],
        "pip": ["requests"],
    }
    __defaults__ = {
        "enabled": False,
    }

    def __init__(self):
        self.ready = False
        logging.info(f"[{self.__class__.__name__}] plugin init")
        self.title = ""

    def on_loaded(self):
        global READY
        global CRACK_MENU
        tmp_line = ""
        tmp_list = list()
        crack_line = list()
        clist = list()
        logging.info(f"[{self.__class__.__name__}] plugin loaded")
        #       loop to retreive all passwords of all files into a big list without dulicate
        for file_path in self.options["files"]:
            if file_path.lower().endswith(".potfile"):
                with open(file_path) as f:
                    for line in f:
                        tmp_line = str(line.rstrip().split(":", 2)[-1:])[2:-2]
                        tmp_list.append(tmp_line)
            elif file_path.lower().endswith(".cracked"):
                with open(file_path) as f:
                    for line in f:
                        tmp_first = str(line.rstrip().split(",")[:3][1:-1])[3:-3]
                        tmp_last = str(line.rstrip().split(",")[3:][1:-1])[3:-3]
                        tmp_line = "%s:%s" % (tmp_first, tmp_last)
                        tmp_list.append(tmp_line)
            else:
                logging.info(
                    f"[{self.__class__.__name__}] %s type is not managed"
                    % (os.path.splitext(file_path))
                )

        #        logging.info(str(tmp_list))
        for line in tmp_list:
            if line.rstrip().split(":")[1] != "":
                clist.append(line)
        CRACK_MENU = list(set(clist))
        #       write all name:password inside a file as backup for the run
        with open(self.options["saving_path"], "w") as f:
            for crack in CRACK_MENU:
                f.write(crack + "\n")
        READY = 1
        logging.info(f"[{self.__class__.__name__}] Successfully loaded")
        logging.info(
            f"[{self.__class__.__name__}] all paths: " + str(self.options["files"])
        )

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
        elif (
            ui.is_lcdhat()
        ):  # This position is for my custom display, maybe you can change it for inky values
            h_pos = (0, 203)
            v_pos = (-10, 185)
            s_pos = (-10, 170)
        elif ui.is_waveshare27inch():
            h_pos = (0, 153)
            v_pos = (216, 122)
        else:
            h_pos = (0, 91)
            v_pos = (180, 61)

        if self.options["orientation"] == "vertical":
            ui.add_element(
                "crack_house",
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
                "crack_house",
                LabeledValue(
                    color=BLACK,
                    label="",
                    value="",
                    position=h_pos,
                    label_font=fonts.Bold,
                    text_font=fonts.Small,
                ),
            )

        if self.options["display_stats"]:
            logging.info(f"[{self.__class__.__name__}] display stats loaded")

            ui.add_element(
                "crack_house_stats",
                LabeledValue(
                    color=BLACK,
                    label="",
                    value="",
                    position=s_pos,
                    label_font=fonts.Bold,
                    text_font=fonts.Small,
                ),
            )

    def on_unload(self, ui):
        with ui._lock:
            try:
                ui.remove_element("crack_house")
                ui.remove_element("crack_house_stats")
                logging.info(f"[{self.__class__.__name__}] plugin unloaded")
            except Exception as e:
                logging.error(f"[{self.__class__.__name__}] unload: %s" % e)

    def on_wifi_update(self, agent, access_points):
        global READY
        global CRACK_MENU
        global TOTAL_CRACK
        global BEST_RSSI
        global BEST_CRACK
        global TIME_WIFI_UPDATE
        tmp_crack = list()
        TIME_WIFI_UPDATE = str(time.strftime("%H:%M", time.localtime()))
        # logging.info(f"[{self.__class__.__name__}] Total cracks: %d" % (len(CRACK_MENU)))

        if READY == 1 and "Not-Associated" in os.popen("iwconfig wlan0").read():
            BEST_RSSI = -1000
            count_crack = 0
            for network in access_points:
                hn = str(network["hostname"])
                ssi = network["rssi"]
                for crack in CRACK_MENU:
                    tmp_crack = crack.rstrip().split(":")
                    tc = str(tmp_crack[0])
                    if hn == tc:
                        # logging.info('[CRACK HOUSE] %s, pass: %s, RSSI: %d' % (tmp_crack[0], tmp_crack[1], ssi))
                        count_crack += 1
                        # logging.info(count_crack)
                        if ssi > BEST_RSSI:
                            BEST_RSSI = ssi
                            BEST_CRACK = tmp_crack
            TOTAL_CRACK = count_crack
            # logging.info(TOTAL_CRACK)
            # logging.info('\n !!!! BEST CRACK HOUSE !!!! \n [CRACK HOUSE] %s, pass: %s, RSSI: %d' % (BEST_CRACK[0], BEST_CRACK[1], BEST_RSSI))

    def on_ui_update(self, ui):
        global CRACK_MENU
        global TOTAL_CRACK
        global BEST_RSSI
        global BEST_CRACK
        global TIME_WIFI_UPDATE
        near_rssi = str(BEST_RSSI)

        if BEST_RSSI != -1000:
            if self.options["orientation"] == "vertical":
                msg_ch = str(
                    BEST_CRACK[0] + "(" + near_rssi + ")" + "\n" + BEST_CRACK[1]
                )
            else:
                msg_ch = str(BEST_CRACK[0] + ":" + BEST_CRACK[1])
            ui.set("crack_house", "%s" % (msg_ch))
        else:
            last_line = "tail -n 1 /root/handshakes/wpa-sec.cracked.potfile | awk -F: '{printf $3 \"\\n\" $4}'"
            ui.set("crack_house", "%s" % (os.popen(last_line).read().rstrip()))

        if self.options["display_stats"]:
            msg_stats = "(%s)%d/%d" % (TIME_WIFI_UPDATE, TOTAL_CRACK, len(CRACK_MENU))
            ui.set("crack_house_stats", "%s" % (msg_stats))
