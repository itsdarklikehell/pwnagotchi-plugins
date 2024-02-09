# wifi_adventures.py

# Disclaimer
# **Note:** This plugin is created for educational purposes
# The author does not take responsibility for any misuse or unauthorized activities conducted with this plugin.
# Be aware of and comply with legal and ethical standards when using this software.
# Always respect privacy, adhere to local laws, and ensure that your actions align with the intended educational purpose of the plugin.
# Use this plugin responsibly and ethically.
# Any actions that violate laws or infringe upon the rights of others are not endorsed or supported.
# By using this software, you acknowledge that the author is not liable for any consequences resulting from its misuse.
# If you have any concerns or questions regarding the ethical use of this plugin, please contact the author for guidance.

# Need to Install ( pip install requests )

import logging
import os
import subprocess
from threading import Timer
import pwnagotchi.plugins as plugins
import pwnagotchi.ui.fonts as fonts
from pwnagotchi.ui.components import LabeledValue
from pwnagotchi.ui.view import BLACK
import datetime
import json
import random
import re
import requests


class AdventureType:
    HANDSHAKE = "handshake"
    NEW_NETWORK = "new_network"
    PACKET_PARTY = "packet_party"
    PIXEL_PARADE = "pixel_parade"
    DATA_DAZZLE = "data_dazzle"
    SPEEDY_SCAN = "speedy_scan"


class FunAchievements(plugins.Plugin):
    __GitHub__ = ""
    __author__ = "(edited by: itsdarklikehell bauke.molenaar@gmail.com), https://github.com/MaliosDark/"
    __version__ = "1.3.9"
    __license__ = "GPL3"
    __description__ = (
        "Taking Pwnagotchi on WiFi adventures and collect fun achievements."
    )
    __name__ = "FunAchievements"
    __help__ = "Taking Pwnagotchi on WiFi adventures and collect fun achievements."
    __dependencies__ = {
        "apt": ["none"],
        "pip": ["scapy"],
    }
    __defaults__ = {
        "enabled": False,
    }

    def __init__(self):
        self.ready = False
        logging.debug(f"[{self.__class__.__name__}] plugin init")
        self.fun_achievement_count = 0
        self.handshake_count = 0
        self.new_networks_count = 0
        self.packet_party_count = 0
        self.pixel_parade_count = 0
        self.data_dazzle_count = 0
        self.treasure_chests_count = 0
        self.title = ""
        self.last_claimed = None
        self.daily_quest_target = 3
        self.current_adventure = self.choose_random_adventure()
        self.data_path = os.path.join(
            os.path.dirname(os.path.realpath(__file__)
                            ), "fun_achievements.json"
        )

    def get_label_based_on_adventure(self):
        if self.current_adventure == AdventureType.NEW_NETWORK:
            return "New Adventure:  "
        elif self.current_adventure == AdventureType.PACKET_PARTY:
            return "Party Time:  "
        elif self.current_adventure == AdventureType.PIXEL_PARADE:
            return "Pixel Parade:  "
        elif self.current_adventure == AdventureType.DATA_DAZZLE:
            return "Data Dazzle:  "
        elif self.current_adventure == AdventureType.SPEEDY_SCAN:
            return "Speedy Scan:  "
        else:
            return "Mysterious Quest:  "

    def load_from_json(self):
        logging.info(f"[{self.__class__.__name__}] Loading data from JSON...")
        if os.path.exists(self.data_path):
            with open(self.data_path, "r") as file:
                data = json.load(file)
                self.handshake_count = data.get("handshake_count", 0)
                self.fun_achievement_count = data.get(
                    "fun_achievement_count", 0)
                self.new_networks_count = data.get("new_networks_count", 0)
                self.packet_party_count = data.get("packet_party_count", 0)
                self.pixel_parade_count = data.get("pixel_parade_count", 0)
                self.data_dazzle_count = data.get("data_dazzle_count", 0)
                self.treasure_chests_count = data.get(
                    "treasure_chests_count", 0)
                self.daily_quest_target = data.get("daily_quest_target", 5)
                self.last_claimed = (
                    datetime.datetime.strptime(
                        data["last_claimed"], "%Y-%m-%d").date()
                    if "last_claimed" in data
                    else None
                )
                self.current_adventure = FunAchievements.choose_random_adventure()
        logging.info(
            f"[{self.__class__.__name__}] Loaded data from JSON: {data}")

    @staticmethod
    def choose_random_adventure():
        return random.choice(
            [
                AdventureType.HANDSHAKE,
                AdventureType.NEW_NETWORK,
                AdventureType.PACKET_PARTY,
                AdventureType.PIXEL_PARADE,
                AdventureType.DATA_DAZZLE,
                AdventureType.SPEEDY_SCAN,
            ]
        )

    def on_loaded(self):
        logging.info(f"[{self.__class__.__name__}] plugin loaded")

    def on_ui_setup(self, ui):
        title_label = self.get_label_based_on_adventure()
        achievement_label = f"{self.handshake_count}/{self.daily_quest_target} ({self.get_title_based_on_achievements()})"
        ui.add_element(
            "showFunAchievements",
            LabeledValue(
                color=BLACK,
                label=title_label,
                value=achievement_label,
                position=(0, 95),
                label_font=fonts.Medium,
                text_font=fonts.Medium,
            ),
        )

    def on_ui_update(self, ui):
        if self.ready:
            ui.set(
                "showFunAchievements",
                f"{self.handshake_count}/{self.daily_quest_target} ({self.get_title_based_on_achievements()})",
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
            0: "WiFi Whisperer",
            4: "Signal Maestro",
            8: "Adventure Artisan",
            16: "Byte Buccaneer",
            20: "Data Dynamo",
            24: "Network Nomad",
            28: "Binary Bard",
            32: "Code Commander",
            40: "Cyber Corsair",
            48: "Protocol Pioneer",
            60: "Bit Bazaar",
            68: "Digital Druid",
            80: "Epic Explorer",
            120: "System Sorcerer",
            130: "Crypto Crusader",
            150: "Digital Dynamo",
            160: "Cyber Celestial",
            180: "Bitlord of the Bits",
            190: "Master of the Matrix",
            200: "Legendary Adventurer",
        }

        # Duplicar los puntos necesarios para cada título
        titles = {key * 2: value for key, value in titles.items()}

        # Buscar el título más alto alcanzado
        current_title = None
        for threshold in sorted(titles.keys(), reverse=True):
            if self.fun_achievement_count >= threshold:
                current_title = titles[threshold]
                break

        # Actualizar el atributo 'title'
        if current_title is not None and current_title != self.title:
            self.title = current_title
            logging.info(
                f"[{self.__class__.__name__}] Updated title: {self.title}")

    def get_title_based_on_achievements(self):
        # Llamar a update_title para asegurarse de que el atributo 'title' esté actualizado
        self.update_title()

        # Retornar el título actualizado
        return self.title

    def save_to_json(self):
        data = {
            "handshake_count": self.handshake_count,
            "new_networks_count": self.new_networks_count,
            "packet_party_count": self.packet_party_count,
            "pixel_parade_count": self.pixel_parade_count,
            "data_dazzle_count": self.data_dazzle_count,
            "treasure_chests_count": self.treasure_chests_count,
            "last_claimed": (
                self.last_claimed.strftime(
                    "%Y-%m-%d") if self.last_claimed else None
            ),
            "daily_quest_target": self.daily_quest_target,
            "current_adventure": self.current_adventure,
            "fun_achievement_count": self.fun_achievement_count,
        }
        with open(self.data_path, "w") as file:
            json.dump(data, file)

    def send_adventure_states_to_server(self, adventure, status):
        # Cambia la URL a la de tu servidor
        server_url = "http://192.168.68.16:5000/get-adventure-state/{}".format(
            adventure
        )

        payload = {
            "adventure": adventure,
            "status": status,
            "handshake_count": self.handshake_count,
            "new_networks_count": self.new_networks_count,
            "packet_party_count": self.packet_party_count,
            "pixel_parade_count": self.pixel_parade_count,
            "data_dazzle_count": self.data_dazzle_count,
            "treasure_chests_count": self.treasure_chests_count,
            "last_claimed": (
                self.last_claimed.strftime(
                    "%Y-%m-%d") if self.last_claimed else None
            ),
            "daily_quest_target": self.daily_quest_target,
            "current_adventure": self.current_adventure,
            "fun_achievement_count": self.fun_achievement_count,
        }

        try:
            response = requests.post(server_url, json=payload)
            response.raise_for_status()
            logging.info(
                f"Estado de la aventura enviado al servidor: {response.text}")
        except requests.exceptions.RequestException as e:
            logging.error(
                f"Error al enviar estado de la aventura al servidor: {e}")

    def on_handshake(self, agent, filename, access_point, client_station):
        logging.info(
            f"[{self.__class__.__name__}] on_handshake - Current Adventure: {self.current_adventure}, Handshake Count: {self.handshake_count}"
        )

        difficulty_multiplier = {
            AdventureType.HANDSHAKE: 1,
            AdventureType.NEW_NETWORK: 1,
            AdventureType.PACKET_PARTY: 2,
            AdventureType.PIXEL_PARADE: 1,
            AdventureType.DATA_DAZZLE: 1,
            AdventureType.SPEEDY_SCAN: 1,
        }

        self.handshake_count += difficulty_multiplier.get(
            self.current_adventure, 1)
        self.check_and_update_daily_quest_target()
        self.check_treasure_chest()

        if self.is_adventure_completed():
            self.fun_achievement_count += 1
            self.update_title()

            # Enviar estado de la aventura al servidor
            self.send_adventure_states_to_server(
                self.current_adventure, "Completed")

        self.save_to_json()

        # Add status message
        status_message = f"Handshake adventure in progress! Current count: {self.handshake_count}/{self.daily_quest_target}"
        self.show_status_message(status_message)

    def on_packet_party(self, agent, party_count):
        if self.current_adventure == AdventureType.PACKET_PARTY:
            self.packet_party_count += party_count
            self.check_and_update_daily_quest_target()
            self.check_treasure_chest()

            # Check if the current adventure is Packet Party
            if self.current_adventure == AdventureType.PACKET_PARTY:
                # Simulate the capture of different types of packets during the party
                for _ in range(party_count):
                    captured_packet_type = random.choice(
                        ["Data Packet", "Control Packet", "Management Packet"]
                    )

                    # Process the captured packet based on its type
                    self.process_captured_packet(captured_packet_type)

        self.save_to_json()

    def process_captured_packet(self, packet_type):
        # Logic for processing a captured packet during the Packet Party
        logging.info(
            f"[{self.__class__.__name__}] Captured a {packet_type} during the Packet Party!"
        )

        # Determine the effects or challenges based on the captured packet type
        if packet_type == "Data Packet":
            # Example: Gain experience points for capturing data packets
            self.gain_experience(10)
        elif packet_type == "Control Packet":
            # Example: Temporarily boost Pwnagotchi's speed for control packets
            self.temporarily_boost_speed()
        elif packet_type == "Management Packet":
            # Example: Encounter a challenge or puzzle related to management packets
            self.encounter_management_challenge()

    def gain_experience(self, experience_points):
        # Logic for gaining experience points
        logging.info(
            f"[{self.__class__.__name__}] Gained {experience_points} experience points!"
        )

        # Update Pwnagotchi's experience points attribute (assuming it exists)
        self.experience_points += experience_points

    def temporarily_boost_speed(self):
        # Logic for temporarily boosting Pwnagotchi's speed
        logging.info(
            f"[{self.__class__.__name__}] Pwnagotchi's speed is temporarily boosted!"
        )

        # Increase speed attribute for a short duration
        self.speed += 5  # adjust as needed

        # Schedule the end of the speed boost after a specified duration (e.g., 60 seconds)
        Timer(60, self.end_speed_boost).start()

    def end_speed_boost(self):
        # Logic for ending the temporary speed boost
        logging.info(
            f"[{self.__class__.__name__}] Temporary speed boost has ended.")

        # Reset the boosted speed attribute to its original value
        self.speed -= 5  # adjust as needed

    def encounter_management_challenge(self):
        # Logic for encountering a challenge or puzzle related to management packets
        logging.info(
            f"[{self.__class__.__name__}] Encountered a management packet challenge!"
        )

        # Implement a challenge or puzzle scenario
        # For example, prompt the player to solve a puzzle or answer a question related to networking concepts.
        # You can use input() to get user responses and determine the outcome.

        # Example:
        user_response = input(
            f"[{self.__class__.__name__}] Solve the puzzle: What is the purpose of a management packet? "
        )

        if user_response.lower() == "network_management":
            logging.info(
                f"[{self.__class__.__name__}] Puzzle solved! Gain a reward.")
            self.gain_reward()
        else:
            logging.info(
                f"[{self.__class__.__name__}] Incorrect answer. Face a consequence."
            )
            self.face_consequence()

    def gain_reward(self):
        # Logic for gaining a reward after successfully solving a challenge
        logging.info(
            f"[{self.__class__.__name__}] Congratulations! You've earned a reward."
        )

        # Determine and apply the reward (e.g., gain virtual coins, unlock an achievement, etc.)
        self.virtual_coins += 20
        self.unlock_achievement("Packet Party Master")

    def face_consequence(self):
        # Logic for facing a consequence after an incorrect answer
        logging.info(
            f"[{self.__class__.__name__}] Oh no! Incorrect answer comes with consequences."
        )

        # Determine and apply the consequence (e.g., decrease virtual coins, face a setback, etc.)
        self.virtual_coins -= 10

    def on_speedy_scan(self, agent):
        # Lógica para la aventura Speedy Scan
        scan_duration = 30  # segundos
        # ejemplo de paquetes capturados
        packets_captured = random.randint(10, 50)
        self.packet_party_count += packets_captured

        self.check_and_update_daily_quest_target()
        self.check_treasure_chest()

        if self.is_adventure_completed():
            self.fun_achievement_count += 1
            self.update_title()

        self.save_to_json()

    def on_pixel_parade(self, agent, pixel_count):
        if self.current_adventure == AdventureType.PIXEL_PARADE:
            self.pixel_parade_count += pixel_count
            self.check_and_update_daily_quest_target()
            self.check_treasure_chest()

            # Set a threshold for the special event (adjust as needed)
            special_event_threshold = 100

            # Check if the threshold for the special event is reached
            if self.pixel_parade_count >= special_event_threshold:
                self.trigger_special_pixel_event()

        self.save_to_json()

    def trigger_special_pixel_event(self):
        # Logic for the special Pixel Parade event
        logging.info(
            f"[{self.__class__.__name__}] Special Pixel Parade event reached!")

        # Determine the type of special event based on random chance
        special_event_type = random.choice(
            ["Treasure Hunt", "Stat Boost", "New Ability"]
        )

        # Execute actions based on the type of special event
        if special_event_type == "Treasure Hunt":
            logging.info(
                f"[{self.__class__.__name__}] You've triggered a Treasure Hunt! Search for hidden treasures."
            )
            self.start_treasure_hunt()
        elif special_event_type == "Stat Boost":
            logging.info(
                f"[{self.__class__.__name__}] Your Pwnagotchi receives a temporary stat boost!"
            )
            self.boost_pwnagotchi_stats()
        elif special_event_type == "New Ability":
            logging.info(
                f"[{self.__class__.__name__}] Your Pwnagotchi gains a new special ability!"
            )
            self.give_new_ability()

        # Reset the Pixel Parade count
        self.pixel_parade_count = 0

    def start_treasure_hunt(self):
        # Logic for starting a treasure hunt
        logging.info(
            f"[{self.__class__.__name__}] Welcome to the Treasure Hunt!")

        # Generate a random number of hidden treasures (adjust as needed)
        num_hidden_treasures = random.randint(3, 8)

        # Initialize the player's progress
        treasures_found = 0

        # Loop until the player finds all treasures or decides to end the hunt
        while treasures_found < num_hidden_treasures:
            # Present clues or prompts to guide the player
            user_input = input(
                f"[{self.__class__.__name__}] Clue: Enter 'hunt' to search for treasure or 'end' to end the hunt: "
            )

            if user_input.lower() == "hunt":
                # Player chooses to search for treasure
                if random.random() < 0.4:  # 40% chance of finding a treasure
                    logging.info(
                        f"[{self.__class__.__name__}] You found a hidden treasure!"
                    )
                    treasures_found += 1
                else:
                    logging.info(
                        f"[{self.__class__.__name__}] No treasure found this time."
                    )

            elif user_input.lower() == "end":
                # Player chooses to end the treasure hunt
                break

        logging.info(
            f"[{self.__class__.__name__}] Treasure Hunt ended. You found {treasures_found} treasures!"
        )

    def boost_pwnagotchi_stats(self):
        # Logic for boosting Pwnagotchi stats
        logging.info(
            f"[{self.__class__.__name__}] Your Pwnagotchi receives a temporary stat boost!"
        )

        # Increase relevant attributes for a limited time (adjust values as needed)
        boost_duration = 120  # seconds
        boost_amount = 2  # arbitrary boost factor

        # Apply the stat boost
        self.speed += boost_amount
        self.intelligence += boost_amount
        self.luck += boost_amount

        # Schedule the end of the boost after the specified duration
        Timer(boost_duration, self.end_stat_boost,
              args=(boost_amount,)).start()

    def end_stat_boost(self, boost_amount):
        # Logic for ending the temporary stat boost
        logging.info(
            f"[{self.__class__.__name__}] Temporary stat boost has ended.")

        # Reset boosted attributes to their original values
        self.speed -= boost_amount
        self.intelligence -= boost_amount
        self.luck -= boost_amount

    def give_new_ability(self):
        # Logic for giving the Pwnagotchi a new special ability
        logging.info(
            f"[{self.__class__.__name__}] Your Pwnagotchi gains a new special ability!"
        )

        # Define a list of possible abilities (customize as needed)
        abilities = [
            "Electric Surge",
            "Mind Control",
            "Time Warp",
            "Shadow Walk",
            "Gravity Manipulation",
            "Energy Absorption",
            "Telepathic Communication",
            "Molecular Reconstruction",
            "Illusion Casting",
            "Technomancy",
        ]

        # Randomly assign a new ability to the Pwnagotchi
        new_ability = random.choice(abilities)

        logging.info(f"[{self.__class__.__name__}] New Ability: {new_ability}")

        # Add the new ability to the Pwnagotchi's list of abilities (assuming you have such a list)
        self.abilities.append(new_ability)

    def on_data_dazzle(self, agent, dazzle_count):
        if self.current_adventure == AdventureType.DATA_DAZZLE:
            self.data_dazzle_count += dazzle_count
            self.check_and_update_daily_quest_target()
            self.check_treasure_chest()

            # Set a threshold for the special event (adjust as needed)
            special_event_threshold = 50

            # Check if the threshold for the special event is reached
            if self.data_dazzle_count >= special_event_threshold:
                self.trigger_special_data_dazzle_event()

        self.save_to_json()

    def trigger_special_data_dazzle_event(self):
        # Logic for the special Data Dazzle event
        logging.info(
            f"[{self.__class__.__name__}] Special Data Dazzle event reached!")

        # Offer the player options for data to dazzle
        data_options = ["Email", "Password",
                        "Credit Card Number", "Secret Message"]

        # Randomly choose a data type to dazzle
        chosen_data = random.choice(data_options)
        logging.info(f"[{self.__class__.__name__}] Dazzle: {chosen_data}")

        # Depending on the chosen data type, grant different rewards or present challenges to the player
        if chosen_data == "Email":
            # Example: Unlock a new achievement related to cybersecurity
            self.fun_achievement_count += 1
            self.update_title()
        elif chosen_data == "Password":
            # Example: Increase the Pwnagotchi's security level
            self.security_level += 1
        elif chosen_data == "Credit Card Number":
            # Example: Grant virtual coins to the player
            self.virtual_coins += 10
        elif chosen_data == "Secret Message":
            # Example: Present a special message or challenge to the player
            logging.info(
                f"[{self.__class__.__name__}] Decode the secret message for an additional reward!"
            )

        # Reset the Data Dazzle count
        self.data_dazzle_count = 0

    def is_adventure_completed(self):
        if self.current_adventure == AdventureType.HANDSHAKE:
            if self.handshake_count >= self.daily_quest_target:
                self.fun_achievement_count += 1
                self.update_title()
                return True
            return False
        elif self.current_adventure == AdventureType.NEW_NETWORK:
            if self.new_networks_count >= self.daily_quest_target:
                self.fun_achievement_count += 1
                self.update_title()
                return True
        elif self.current_adventure == AdventureType.PACKET_PARTY:
            if self.packet_party_count >= self.daily_quest_target:
                self.fun_achievement_count += 1
                self.update_title()
                return True
        elif self.current_adventure == AdventureType.PIXEL_PARADE:
            if self.pixel_parade_count >= self.daily_quest_target:
                self.fun_achievement_count += 1
                self.update_title()
                return True
        elif self.current_adventure == AdventureType.DATA_DAZZLE:
            if self.data_dazzle_count >= self.daily_quest_target:
                self.fun_achievement_count += 1
                self.update_title()
                return True
        return False

    def check_and_update_daily_quest_target(self):
        today = datetime.date.today()
        if self.last_claimed is None or self.last_claimed < today:
            self.last_claimed = today
            self.daily_quest_target += 2

            # Incrementar el título después de actualizar la aventura actual
            self.update_title()

            if self.is_adventure_completed():
                self.fun_achievement_count += 1

                # Change the adventure to the next one
                self.current_adventure = self.choose_random_adventure()

                # Increase the difficulty for the new adventure
                self.increase_adventure_difficulty()

                # Show a status message indicating the new adventure
                status_message = f"New adventure started: {self.current_adventure}! Difficulty increased."
                self.show_status_message(status_message)

            # Save changes to JSON after updating data
            self.save_to_json()

    def increase_adventure_difficulty(self):
        difficulty_multiplier = {
            AdventureType.HANDSHAKE: 1.1,
            AdventureType.NEW_NETWORK: 1.2,
            AdventureType.PACKET_PARTY: 1.5,
            AdventureType.PIXEL_PARADE: 1.3,
            AdventureType.DATA_DAZZLE: 1.4,
            AdventureType.SPEEDY_SCAN: 1.2,
        }

        # Increase the difficulty multiplier for the current adventure
        multiplier = difficulty_multiplier.get(self.current_adventure, 1.0)
        self.daily_quest_target = max(
            int(self.daily_quest_target * multiplier), 1)

        # Log the updated difficulty
        logging.info(
            f"[{self.__class__.__name__}] Difficulty increased for {self.current_adventure}. New daily quest target: {self.daily_quest_target}"
        )

    def show_status_message(self, ui, message):
        try:
            # Check if the 'statusMessage' UI element already exists
            if "statusMessage" in ui.elements:
                # Update the existing 'statusMessage' element with the new message
                ui.get("statusMessage").set_value(message)
            else:
                # Add a new 'statusMessage' UI element to display the status message
                ui.add_element(
                    "statusMessage",
                    LabeledValue(
                        color=BLACK,
                        label="Status:",
                        value=message,
                        position=(0, 110),
                        label_font=fonts.Small,
                        text_font=fonts.Small,
                    ),
                )

            # Ensure to call ui.update() after modifying the UI to refresh the display
            ui.update()

        except Exception as e:
            logging.error(f"Error updating status message on UI: {e}")

    def on_unfiltered_ap_list(self, agent):
        self.new_networks_count += 1

    def get_password_from_potfile(self, ssid):
        try:
            # Assuming the potfile is located at /root/handshakes/wpa-sec.cracked.potfile
            potfile_path = "/root/handshakes/wpa-sec.cracked.potfile"

            # Using grep to find the password for the given SSID
            result = subprocess.run(
                ["grep", f"^{ssid}:", potfile_path], capture_output=True, text=True
            )

            # If there is a match, extract the password
            if result.stdout:
                password = result.stdout.strip().split(":")[1]
                return password
            else:
                return None
        except Exception as e:
            logging.error(f"Error getting password from potfile: {e}")
            return None

    def connect_to_wifi(self, ssid, password):
        try:
            # List available Wi-Fi interfaces
            result = subprocess.run(
                ["iw", "dev"], capture_output=True, text=True, check=True
            )
            interfaces = re.findall(r"Interface (\w+)", result.stdout)

            # Choose the interface with the strongest signal for the specified network
            best_interface = self.choose_best_wifi_interface(ssid, interfaces)

            if best_interface:
                # using wpa_supplicant:
                subprocess.run(
                    [
                        "wpa_supplicant",
                        "-B",
                        "-i",
                        best_interface,
                        "-c",
                        "/etc/wpa_supplicant/wpa_supplicant.conf",
                        "-D",
                        "nl80211,wext",
                    ],
                    check=True,
                )

                # Add a sleep to allow time for the connection to be established before proceeding
                import time

                time.sleep(5)

                # Bring up the interface
                subprocess.run(["ifconfig", best_interface, "up"], check=True)

                # Connect to the specified Wi-Fi network with the provided password
                subprocess.run(
                    ["wpa_cli", "-i", best_interface, "add_network"], check=True
                )
                subprocess.run(
                    [
                        "wpa_cli",
                        "-i",
                        best_interface,
                        "set_network",
                        "0",
                        "ssid",
                        f'"{ssid}"',
                    ],
                    check=True,
                )
                subprocess.run(
                    [
                        "wpa_cli",
                        "-i",
                        best_interface,
                        "set_network",
                        "0",
                        "psk",
                        f'"{password}"',
                    ],
                    check=True,
                )
                subprocess.run(
                    ["wpa_cli", "-i", best_interface, "enable_network", "0"], check=True
                )
                subprocess.run(
                    ["wpa_cli", "-i", best_interface, "reassociate"], check=True
                )
            else:
                logging.info(
                    f"No suitable Wi-Fi interface found for network: {ssid}")

        except subprocess.CalledProcessError as e:
            logging.error(f"Error connecting to WiFi: {e}")
        except Exception as e:
            logging.error(f"Unexpected error connecting to WiFi: {e}")

    def choose_best_wifi_interface(self, ssid, interfaces):
        # Choose the Wi-Fi interface with the strongest signal for the specified network
        best_interface = None
        best_signal_strength = -100  # Initialize with a weak signal strength

        for interface in interfaces:
            result = subprocess.run(
                ["iw", "dev", interface, "link"], capture_output=True, text=True
            )
            signal_strength_match = re.search(
                r"signal: (-\d+) dBm", result.stdout)

            if signal_strength_match:
                signal_strength = int(signal_strength_match.group(1))

                # Check if the network is available on this interface and signal strength is stronger
                if ssid in result.stdout and signal_strength > best_signal_strength:
                    best_signal_strength = signal_strength
                    best_interface = interface

        return best_interface

    def check_treasure_chest(self):
        if random.random() < 0.1:  # 10% chance to find a treasure chest
            self.treasure_chests_count += 1
            logging.info(
                f"[{self.__class__.__name__}] You found a treasure chest!")

    def on_unload(self, ui):
        with ui._lock:
            try:
                ui.remove_element("showFunAchievements")
                ui.remove_element("statusMessage")
                logging.info(f"[{self.__class__.__name__}] plugin unloaded")
            except Exception as e:
                logging.error(f"[{self.__class__.__name__}] unload: %s" % e)

    def on_webhook(self, path, request):
        logging.info(f"[{self.__class__.__name__}] webhook pressed")
