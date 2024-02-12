"""
## Plugin Setup
If you have not set up a directory for custom plugins, create the directory and add its path to your config.toml. main.custom_plugins = "/usr/local/share/pwnagotchi/custom-plugins/"
Install dependencies
Put plugin to your custom folder
Restart pwnagotchi service

## MQTT Plugin
Sends info about your Pwnagotchi to local MQTT broker.
Tested on 1.5.5 official version.

## Dependencies
sudo apt install python3-psutil python3-paho-mqtt mosquitto mosquitto-clients && sudo pip3 install paho-mqtt==1.4.0

## Defaults
MQTT host: localhost
Topic: pwnagotchi
"""

import pwnagotchi.plugins as plugins
import pwnagotchi.ui as ui
import pwnagotchi
import os
import json
import logging
import paho.mqtt.client as mqtt


class MqttPlugin(plugins.Plugin):

    __author__ = "https://github.com/mavotronik/pwnagotchi-plugins"
    __version__ = "1.0.0"
    __license__ = "MIT"
    __description__ = "A plugin that sends info about your pwnagotchi to MQTT"
    __name__ = "MqttPlugin"
    __help__ = "A plugin that sends info about your pwnagotchi to MQTT"
    __dependencies__ = {
        "apt": ["none"],
        "pip": ["scapy"],
    }
    __defaults__ = {
        "enabled": False,
    }

    def __init__(self):
        #        self.options = {
        #        'host': 'localhost',
        #        'topic': 'pwnagotchi'
        #        }

        super().__init__()
        self.client = mqtt.Client()
        self.client.connect("localhost", 1883, 60)

    def on_ui_update(self, ui):
        mem = f"{int(pwnagotchi.mem_usage() * 100)}"
        cpu_load = f"{int(pwnagotchi.cpu_load() * 100)}"
        temp = int(open("/sys/class/thermal/thermal_zone0/temp").read()) / 1000
        points = len(os.listdir("/root/handshakes/"))

        #        self.mqtt_publish()
        self.client.publish("pwnagotchi/mem", f"{mem}")
        self.client.publish("pwnagotchi/cpu_load", f"{cpu_load}")
        self.client.publish("pwnagotchi/temp", f"{temp}")
        self.client.publish("pwnagotchi/points", f"{points}")

    def on_stats_update(self, stats):
        logging.info("MQTT Plugin: stats updated")

    def on_loaded(self):
        logging.info("MQTT Plugin: loaded")
        ui.set("face", "(✜‿‿✜)")
        ui.set("status", "MQTT is ready!")

    def on_unloaded(self):
        logging.info("MQTT Plugin: unloaded")


#    def mqtt_publish(self):
#        self.client.publish("pwnagotchi/mem", f"{mem}")
#        self.client.publish("pwnagotchi/cpu_load", f"{cpu_load}")
#        self.client.publish("pwnagotchi/temp", f"{temp}")
#        self.client.publish("pwnagotchi/points", f"{points}")
