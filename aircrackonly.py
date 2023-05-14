from pwnagotchi import plugins

import logging
import subprocess
import string
import os


class AircrackOnly(plugins.Plugin):
    __author__ = 'pwnagotchi [at] rossmarks [dot] uk'
    __version__ = '2.0.0'
    __license__ = 'GPL3'
    __description__ = 'confirm pcap contains handshake/PMKID or delete it'
    __dependencies__ = {
        'apt': ['aircrack-ng'],
    }
    __defaults__ = {
        'enabled': False,
        'face': '(>.<)',
    }

    def __init__(self):
        self.text_to_set = ""

    def on_loaded(self):
        logging.info('[aircrackonly] plugin loaded')

        if 'face' not in self.options:
            self.options['face'] = '(>.<)'

        check = subprocess.run(
            ('/usr/bin/dpkg -l aircrack-ng | grep aircrack-ng | awk \'{print $2, $3}\''), shell=True, stdout=subprocess.PIPE)
        check = check.stdout.decode('utf-8').strip()
        if check != "aircrack-ng <none>":
            logging.info('[aircrackonly] Found %s', check)
        else:
            logging.warning('[aircrackonly] aircrack-ng is not installed!')

    def on_handshake(self, agent, filename, access_point, client_station):
        display = agent._view
        todelete = 0
        handshakeFound = 0

        result = subprocess.run(('/usr/bin/aircrack-ng ' + filename + ' | grep "1 handshake" | awk \'{print $2}\''),
                                shell=True, stdout=subprocess.PIPE)
        result = result.stdout.decode('utf-8').translate({ord(c): None for c in string.whitespace})
        if result:
            handshakeFound = 1
            logging.info('[aircrackonly] contains handshake')

        if handshakeFound == 0:
            result = subprocess.run(('/usr/bin/aircrack-ng ' + filename + ' | grep "PMKID" | awk \'{print $2}\''),
                                    shell=True, stdout=subprocess.PIPE)
            result = result.stdout.decode('utf-8').translate({ord(c): None for c in string.whitespace})
            if result:
                logging.info('[aircrackonly] contains PMKID')
            else:
                todelete = 1

        if todelete == 1:
            os.remove(filename)
            self.text_to_set = "Removed an uncrackable pcap"
            logging.warning('[aircrackonly] Removed uncrackable pcap %s', filename)
            display.update(force=True)

    def on_ui_update(self, ui):
        if self.text_to_set:
            ui.set('face', self.options['face'])
            ui.set('status', self.text_to_set)
            self.text_to_set = ""
