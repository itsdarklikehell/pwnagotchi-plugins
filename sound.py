
import pwnagotchi.plugins as plugins
import logging
import os, sys
from subprocess import call
from shlex import quote
import json
import re


class Sound(plugins.Plugin):
  __author__ = 'https://github.com/xenDE/pwnagotchi-plugin-sound'
  __version__ = '1.2.0'
  __name__ = 'sound'
  __license__ = 'GPL3'
  __description__ = 'An plugin for pwnagotchi that plays an wav file with aplay on events and uses a text2speech engine. tested with 1.0.0-RC4'
  __help__ = """
-this plugin needs a installed and working audio DAC HAT, USB-Soundcard or a connected bt-headset/headphone for audio output, like https://www.raspiaudio.com/
-for enable text2speech on raspberry-pi-zero with debian buster to speak the SSID on handshake and others, you need to install "pico2wave" as root:
⋅⋅⋅wget http://archive.raspberrypi.org/debian/pool/main/s/svox/libttspico-utils_1.0+git20130326-3+rpi1_armhf.deb
⋅⋅⋅wget http://archive.raspberrypi.org/debian/pool/main/s/svox/libttspico0_1.0+git20130326-3+rpi1_armhf.deb
⋅⋅⋅apt-get install -f ./libttspico0_1.0+git20130326-3+rpi1_armhf.deb ./libttspico-utils_1.0+git20130326-3+rpi1_armhf.deb
⋅⋅⋅# test:
⋅⋅⋅pico2wave -w lookdave.wav "Look Dave, I can see you're really upset about this." && aplay lookdave.wav
-with device https://www.raspiaudio.com/promo you can use the yellow button to shutdown your raspberry-pi. read sound/shutdown_button.py for help
-install: copy "sound.py" and "sound/" dir to your configured "custom_plugins" directory and add+edit sound config to /etc/pnagotchi/config.yml:
⋅⋅⋅    custom_plugins: /usr/local/pwnagotchi/plugins
⋅⋅⋅    plugins:
⋅⋅⋅      sound:
⋅⋅⋅        enabled: true
⋅⋅⋅        sound-dir: default
⋅⋅⋅        text2speech-use: false
⋅⋅⋅        text2speech-lang: en-US
"""


  def play_my_sound(self, event, say=""):
    "this function plays the event.wav file and if say is not empt, it talks this with text2speech after playing the event"
    sounddir = os.path.dirname(os.path.realpath(__file__))+"/sound/"+self.options['sound-dir']+"/"
    soundfile= sounddir+event+".wav"
    if say is not "":
#          https://stackoverflow.com/questions/199059/a-pythonic-way-to-insert-a-space-before-capital-letters
#      say = re.sub(r"(\w)([A-Z])", r"\1 \2", say)
      re_outer = re.compile(r'([^A-Z ])([A-Z])')
      re_inner = re.compile(r'(?<!^)([A-Z])([^A-Z])')
      say = re_outer.sub(r'\1 \2', re_inner.sub(r' \1\2', say))
      say = say.replace('FRIT Z!',' Fritz')
    if os.path.isfile(soundfile):
        t2s = quote(self.options['text2speech-lang'])
        if self.options['text2speech-use']:
            t2s += ' '+quote(say)
        command = ["/bin/bash", "bash", "-c", sounddir+"../do_play.sh "+quote(soundfile)+' '+t2s+" & disown"]
        logging.info("plugin.sound: event:"+event+" say:"+t2s)
        os.spawnlp(os.P_WAIT, *command)
    else:
        logging.debug("plugin.sound: file not exist: "+soundfile)
        pass


# called when the plugin is loaded
  def on_loaded(self):
    logging.info("sound plugin loaded")
    # sys._getframe().f_code.co_name = "on_loaded"  <<< the event/function name
    self.play_my_sound(sys._getframe().f_code.co_name)


# called when a new handshake is captured, access_point and client_station are json objects
  def on_handshake(self, agent, filename, access_point, client_station):
    #   access_point: {'ipv4': '0.0.0.0', 'ipv6': '', 'mac': '44:4e:6d:aa:aa:aa', 'hostname': 'FRITZ!Box 6430 Cable BX', 'alias': '', 'vendor': 'AVM Audiovisuelles Marketing und Computersysteme GmbH', 'first_seen': '2019-10-08T01:24:08.535091885+01:00', 'last_seen': '2019-10-08T01:24:32.879958989+01:00', 'meta': {'values': {}}, 'frequency': 2437, 'channel': 6, 'rssi': -85, 'sent': 161, 'received': 0, 'encryption': 'WPA2', 'cipher': 'CCMP', 'authentication': 'PSK', 'wps': {'Config Methods': 'Push Button, Keypad, Display', 'Device Name': 'FBox', 'Manufacturer': 'AVM', 'Model Name': 'FBox', 'Model Number': '0000', 'Primary Device Type': 'AP (oui:0050f204)', 'RF Bands': '2.4Ghz', 'Response Type': 'AP', 'Serial Number': '0000', 'State': 'Configured', 'UUID-E': '133567cc5f3d5060000000000000000', 'Version': '2.0'}, 'clients': [], 'handshake': True}
    #   client_station: {"mac": "b8:27:eb:07:ee:16", "vendor": ""}
    # talk the hostname after event.wav is played
    self.play_my_sound(sys._getframe().f_code.co_name, str(access_point["hostname"]))


# callend when the agent is deauthenticating a client station from an AP
  def on_deauthentication(self, agent, access_point, client_station):
#    logging.info( "deauth ap: " + str(json.dumps(access_point)) )
#    logging.info( "deauth client: " + str(json.dumps(client_station)) )
# deauth ap: {"ipv4": "0.0.0.0", "ipv6": "", "mac": "bc:4d:fb:00:00:00", "hostname": "my private wifi", "alias": "", "vendor": "Hitron Technologies. Inc", "first_seen": "2019-10-24T15:12:56.318186677+01:00", "last_seen": "2019-10-24T15:17:11.87380339+01:00", "meta": {"values": {}}, "frequency": 2412, "channel": 1, "rssi": -84, "sent": 0, "received": 2812, "encryption": "WPA2", "cipher": "CCMP", "authentication": "PSK", "wps": {"Config Methods": "Keypad, Display, Label", "Device Name": "RalinkAPS", "Manufacturer": "Ralink Technology, Corp.", "Model Name": "Ralink Wireless Access Point", "Model Number": "RT2860", "Primary Device Type": "AP (oui:0050f204)", "RF Bands": "2.4Ghz", "Response Type": "AP", "Serial Number": "12345678", "State": "Configured", "UUID-E": "2880288028801880a880bc4dfb0bedc8", "Version": "1.0"}, "clients": [{"ipv4": "0.0.0.0", "ipv6": "", "mac": "08:c5:e1:fd:c4:c7", "hostname": "", "alias": "", "vendor": "Samsung Electro-Mechanics(Thailand)", "first_seen": "2019-10-24T15:13:22.325777687+01:00", "last_seen": "2019-10-24T15:13:22.325777687+01:00", "meta": {"values": {}}, "frequency": 2412, "channel": 1, "rssi": -83, "sent": 52, "received": 0, "encryption": "", "cipher": "", "authentication": "", "wps": {}}, {"ipv4": "0.0.0.0", "ipv6": "", "mac": "90:8d:78:77:fd:ca", "hostname": "", "alias": "", "vendor": "D-Link International", "first_seen": "2019-10-24T15:13:00.403321941+01:00", "last_seen": "2019-10-24T15:17:07.74394858+01:00", "meta": {"values": {}}, "frequency": 2412, "channel": 1, "rssi": -81, "sent": 848, "received": 0, "encryption": "", "cipher": "", "authentication": "", "wps": {}}, {"ipv4": "0.0.0.0", "ipv6": "", "mac": "c8:02:10:05:63:e3", "hostname": "", "alias": "", "vendor": "LG Innotek", "first_seen": "2019-10-24T15:13:03.051655414+01:00", "last_seen": "2019-10-24T15:14:46.499714689+01:00", "meta": {"values": {}}, "frequency": 2412, "channel": 1, "rssi": -77, "sent": 1588, "received": 0, "encryption": "", "cipher": "", "authentication": "", "wps": {}}, {"ipv4": "0.0.0.0", "ipv6": "", "mac": "c4:12:f5:49:44:76", "hostname": "", "alias": "", "vendor": "D-Link International", "first_seen": "2019-10-24T15:13:11.717423772+01:00", "last_seen": "2019-10-24T15:17:15.911791352+01:00", "meta": {"values": {}}, "frequency": 2412, "channel": 1, "rssi": -87, "sent": 324, "received": 0, "encryption": "", "cipher": "", "authentication": "", "wps": {}}], "handshake": false}
# deauth client: {"ipv4": "0.0.0.0", "ipv6": "", "mac": "08:c5:e1:00:00:00", "hostname": "", "alias": "", "vendor": "Samsung Electro-Mechanics(Thailand)", "first_seen": "2019-10-24T15:13:22.325777687+01:00", "last_seen": "2019-10-24T15:13:22.325777687+01:00", "meta": {"values": {}}, "frequency": 2412, "channel": 1, "rssi": -83, "sent": 52, "received": 0, "encryption": "", "cipher": "", "authentication": "", "wps": {}}
    self.play_my_sound(sys._getframe().f_code.co_name)



  def on_cracked(self, agent, access_point):
    logging.info("on_cracked() called in sound-plugin!")
    self.play_my_sound(sys._getframe().f_code.co_name, str(access_point["hostname"]))


