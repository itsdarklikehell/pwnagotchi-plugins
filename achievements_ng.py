import logging
from optparse import TitledHelpFormatter
import os
import pwnagotchi.plugins as plugins
import datetime
import json
import random

from pwnagotchi.ui.components import LabeledValue
from pwnagotchi.ui.view import BLACK
import pwnagotchi.ui.fonts as fonts


class ChallengeType:
    HANDSHAKE = "handshake"
    NEW_NETWORK = "new_network"


def choose_random_challenge():
    return random.choice([ChallengeType.HANDSHAKE, ChallengeType.NEW_NETWORK])


class Achievements(plugins.Plugin):
    __author__ = "SgtStroopwafel, luca.paulmann1@gmail.com"
    __version__ = "1.0.1"
    __license__ = "GPL3"
    __description__ = "Collect achievements for daily challenges."
    __name__ = "Achievements"
    __help__ = (
        "A plugin that will add Achievement stats based on epochs and trained epochs"
    )
    __dependencies__ = {
        "pip": ["none"],
    }
    __defaults__ = {
        "enabled": False,
    }

    def __init__(self):
        self.ready = False
        logging.debug(f"[{self.__class__.__name__}] plugin init")
        self.title = ""
        self.achievement_count = 0  # Overall achievements unlocked
        self.handshake_count = 0
        self.new_networks_count = 0  # Counter for new networks found
        self.last_claimed = None
        self.daily_target = 3
        self.current_challenge = choose_random_challenge()
        self.data_path = os.path.join(
            os.path.dirname(os.path.realpath(__file__)), "achievements.json"
        )  # Choose a challenge type at initialization

    def get_label_based_on_challenge(self):
        return (
            "New Wifi:"
            if self.current_challenge == ChallengeType.NEW_NETWORK
            else "PWND:"
        )

    def load_from_json(self):
        logging.info(f"[{self.__class__.__name__}] Loading data from JSON...")
        logging.info(f"[{self.__class__.__name__}] load_from_json method started.")
        if os.path.exists(self.data_path):
            with open(self.data_path, "r") as file:
                data = json.load(file)
                self.handshake_count = data.get("handshake_count", 0)
                self.achievement_count = data.get("achievement_count", 0)
                self.new_networks_count = data.get("new_networks_count", 0)
                self.daily_target = data.get("daily_target", 5)
                self.last_claimed = (
                    datetime.datetime.strptime(data["last_claimed"], "%Y-%m-%d").date()
                    if "last_claimed" in data
                    else None
                )
                self.current_challenge = data.get(
                    "current_challenge", choose_random_challenge()
                )
        logging.info(f"[{self.__class__.__name__}] Loaded data from JSON: {data}")

    def on_loaded(self):
        logging.info(f"[{self.__class__.__name__}] plugin loaded")
        # self.load_from_json()  # Load the data from JSON when the plugin is loaded

    def on_ui_setup(self, ui):
        title = self.get_title_based_on_achievements()
        label = self.get_label_based_on_challenge()

        logging.info(
            f"[{self.__class__.__name__}] Updating UI - Handshake Count: {self.handshake_count}, Daily Target: {self.daily_target}, Title: {self.get_title_based_on_achievements()}"
        )
        ui.add_element(
            "showAchievements",
            LabeledValue(
                color=BLACK,
                label=label,
                value=f"{self.handshake_count}/{self.daily_target} ({title})",
                position=(0, 83),
                label_font=fonts.Medium,
                text_font=fonts.Medium,
            ),
        )
        # logging.info(f"[{self.__class__.__name__}] Updating UI - Handshake Count: {self.handshake_count}, Daily Target: {self.daily_target}, Title: {self.get_title_based_on_achievements()}")

    def on_ui_update(self, ui):
        if self.ready:
            ui.set(
                "showAchievements",
                f"{self.handshake_count}/{self.daily_target} ({self.get_title_based_on_achievements()})",
            )

    def on_ready(self, agent):
        _ = agent
        self.ready = True
        if os.path.exists(self.data_path):
            self.load_from_json()
        else:
            self.save_to_json()

    def update_title(self):
        titles = {
            0: "Newbie",
            2: "Script Kiddie",
            4: "Keyboard Warrior",
            8: "Byte Wrangler",
            10: "Data Duelist",
            12: "Network Knight",
            14: "Binary Baron",
            16: "Code Commander",
            20: "Cyber Samurai",
            24: "Protocol Pirate",
            30: "Bit Bard",
            34: "Digital Dynast",
            40: "Elite Hacker",
            60: "System Sovereign",
            65: "Crypto King",
            75: "Digital Daemon",
            80: "Cyber Czar",
            90: "Bitlord",
            95: "Master of Metaverse",
            100: "1337",
        }
        for threshold, title in titles.items():
            if self.achievement_count >= threshold:
                return title

    def get_title_based_on_achievements(self):
        return self.update_title()

    def save_to_json(self):
        data = {
            "handshake_count": self.handshake_count,
            "new_networks_count": self.new_networks_count,  # Save the count for new networks
            "last_claimed": (
                self.last_claimed.strftime("%Y-%m-%d") if self.last_claimed else None
            ),
            "daily_target": self.daily_target,
            "current_challenge": self.current_challenge,  # Save the current challenge
            "achievement_count": self.achievement_count,
        }
        with open(self.data_path, "w") as file:
            json.dump(data, file)

    def on_handshake(self, agent, filename, access_point, client_station):
        if self.current_challenge == ChallengeType.HANDSHAKE:
            self.handshake_count += 1
            self.check_and_update_daily_target()
        self.save_to_json()

    def is_challenge_completed(self):
        if self.current_challenge == ChallengeType.HANDSHAKE:
            if self.handshake_count >= self.daily_target:
                self.achievement_count += 1
                return True
            return False
        elif self.current_challenge == ChallengeType.NEW_NETWORK:
            if self.new_networks_count >= self.daily_target:
                self.achievement_count += 1
                return True
        return False

    def check_and_update_daily_target(self):
        today = datetime.date.today()
        if self.last_claimed is None or self.last_claimed < today:
            self.last_claimed = today
            self.daily_target += 2
            if self.is_challenge_completed():
                self.achievement_count += 1  # Increase the overall achievement count
            self.current_challenge = choose_random_challenge()

    def on_unfiltered_ap_list(self, agent):
        self.new_networks_count += (
            1  # Increase the counter whenever a new network is found
        )

    def choose_random_challenge():
        return random.choice([ChallengeType.HANDSHAKE, ChallengeType.NEW_NETWORK])

    def on_unload(self, ui):
        with ui._lock:
            try:
                ui.remove_element("showAchievements")
                logging.info(f"[{self.__class__.__name__}] plugin unloaded")
            except Exception as e:
                logging.error(f"[{self.__class__.__name__}] unload: %s" % e)

    def on_webhook(self, path, request):
        logging.info(f"[{self.__class__.__name__}] webhook pressed")
