import sys, os, subprocess, json, logging
import requests
import urllib.request
from shutil import copyfile
from datetime import datetime

import pwnagotchi
import pwnagotchi.plugins as plugins
import pwnagotchi.ui.faces as faces
import pwnagotchi.ui.fonts as fonts
from pwnagotchi.ui.components import LabeledValue
from pwnagotchi.ui.view import BLACK

class potfilesorter(plugins.Plugin):
    __author__ = "Bauke Molenaar"
    __version__ = "1.0.1"
    __license__ = "MIT"
    __description__ = (
        "A plugin that will sort a potfile and output its to a usable wpa_supplicant.conf."
	)
    __name__ = 'potfilesorter'
    __help__ = """
    A plugin that will sort a potfile and output its to a usable wpa_supplicant.conf.
    """
    __dependencies__ = {
        'pip': ['scapy', 'shutil'],
    }
    __defaults__ = {
        'enabled': False,
        'potfile_source': '/root/wpa-sec.founds.potfile',
        'api_key': '',
        'api_url': 'https://wpa-sec.stanev.org',
        'wpa_source': '/etc/wpa_supplicant/wpa_supplicant.conf',
        'download_results': True
    }

    # potfile_source = '/home/pi/wpa-sec.founds.potfile'
    # dlurl = 'https://wpa-sec.stanev.org/?api&dl=1'

    wpa_backup = "/tmp/wpa_supplicant.bak"
    wpa_tmp = "/tmp/wpa_supplicant.tmp"

    wificonfigstore_source = "/home/pi/WiFiConfigStore.xml"
    wificonfigstore_backup = "/tmp/wificonfigstore.bak"
    wificonfigstore_tmp = "/tmp/wificonfigstore.tmp"

    wificonfigstoresoftap_source = "/home/pi/WiFiConfigStoreSoftAp.xml"
    wificonfigstoresoftap_backup = "/tmp/wificonfigstoresoftap.bak"
    wificonfigstoresoftap_tmp = "/tmp/wificonfigstoresoftap.tmp"

    def __init__(self):
        logging.info("Potfilesorter plugin created")
        self.epochs = 0
        self.train_epochs = 0

    def on_loaded(self):
        logging.info("Potfilesorter plugin loaded")
        if not self.options['api_key']:
            logging.error('[wpasec] API-KEY isn\'t set. Can\'t upload.')
            return
        if not self.options['api_url']:
            logging.error('[wpasec] API-URL isn\'t set. Can\'t upload, no endpoint configured.')
            return
        data_path = "/root/brain.json"
        self.load_data(data_path)
        self.ready = True

    def on_webhook(self, _download_from_wpasec, backup_configs, copy_config, checkwpaconfig, readpotfiledata, agent):
        logging.info("Webhook clicked!")
        _download_from_wpasec()
        backup_configs()
        copy_config()
        checkwpaconfig()
        readpotfiledata()

    def on_internet_available(self, agent):
        config = agent.config()
        handshake_dir = config['bettercap']['handshakes']
        if 'download_results' in self.options and self.options['download_results']:
            cracked_file = os.path.join(handshake_dir, 'wpa-sec.founds.potfile')
            if os.path.exists(cracked_file):
                last_check = datetime.fromtimestamp(os.path.getmtime(cracked_file))
                if last_check is not None and ((datetime.now() - last_check).seconds / (60 * 60)) < 1:
                    return
            try:
                self._download_from_wpasec(os.path.join(handshake_dir, 'wpa-sec.founds.potfile'))
                logging.info('[wpasec] Downloaded cracked passwords.')
            except requests.exceptions.RequestException as req_e:
                logging.debug('[wpasec] %s', req_e)
            except OSError as os_e:
                logging.debug('[wpasec] %s', os_e)

    def _download_from_wpasec(self, output, timeout=30):
        """
        Downloads the results from wpasec and safes them to output

        Output-Format: bssid, station_mac, ssid, password
        """
        logging.info("Downloading wpa-sec clicked!")
        api_url = self.options['api_url']
        if not api_url.endswith('/'):
            api_url = f"{api_url}/"
        api_url = f"{api_url}?api&dl=1"

        cookie = {'key': self.options['api_key']}
        try:
            result = requests.get(api_url, cookies=cookie, timeout=timeout)
            with open(output, 'wb') as output_file:
                output_file.write(result.content)
        except requests.exceptions.RequestException as req_e:
            raise req_e
        except OSError as os_e:
            raise os_e

    def backup_configs(self, wpa_tmp,wpa_source, wpa_backup, wificonfigstore_tmp, wificonfigstore_source, wificonfigstore_backup, wificonfigstoresoftap_tmp, wificonfigstoresoftap_source, wificonfigstoresoftap_backup):
        if os.path.exists(wpa_tmp):
            os.remove(wpa_tmp)
        else:
            logging.info('Backing up: ' + wpa_source)
            logging.info('To: ' + wpa_backup)
            copyfile(wpa_source, wpa_backup)
            logging.info('Create tempfile to work with in: ' + wpa_tmp)
            copyfile(wpa_source, wpa_tmp)

        if os.path.exists(wificonfigstore_tmp):
            os.remove(wificonfigstore_tmp)
        else:
            logging.info('Backing up: ' + wificonfigstore_source)
            logging.info('To: ' + wpa_backup)
            copyfile(wificonfigstore_source, wificonfigstore_backup)
            logging.info('Create tempfile to work with in: ' + wificonfigstore_tmp)
            copyfile(wificonfigstore_source, wificonfigstore_tmp)

        if os.path.exists(wificonfigstoresoftap_tmp):
            os.remove(wificonfigstoresoftap_tmp)
        else:
            logging.info('Backing up: ' + wificonfigstoresoftap_source)
            logging.info('To: ' + wificonfigstoresoftap_backup)
            copyfile(wificonfigstoresoftap_source, wificonfigstoresoftap_backup)
            logging.info('Create tempfile to work with in: ' + wificonfigstoresoftap_tmp)
            copyfile(wificonfigstoresoftap_source, wificonfigstoresoftap_tmp)

    def copy_config(self, wpa_tmp,wpa_source, wificonfigstore_tmp, wificonfigstore_source, wificonfigstoresoftap_tmp, wificonfigstoresoftap_source):
        if os.path.exists(wpa_tmp):
            logging.info('Copying new created config to: ' + wpa_source)
            copyfile(wpa_tmp, wpa_source)
            os.remove(wpa_tmp)
        else:
            logging.info('Cannot copy: ' + wpa_tmp + ' to: ' + wpa_source)
            logging.info('Are you ROOT?')
            exit()

        if os.path.exists(wificonfigstore_tmp):
            logging.info('Copying new created config to: ' + wificonfigstore_source)
            copyfile(wificonfigstore_tmp, wificonfigstore_source)
            os.remove(wificonfigstore_tmp)
        else:
            logging.info('Cannot copy: ' + wpa_tmp + ' to: ' + wpa_source)
            logging.info('Are you ROOT?')
            exit()

        if os.path.exists(wificonfigstoresoftap_tmp):
            logging.info('Copying new created config to: ' + wificonfigstore_source)
            copyfile(wificonfigstoresoftap_tmp, wificonfigstoresoftap_source)
            os.remove(wificonfigstoresoftap_tmp)
            exit()

    def checkwpaconfig(self, wpa_tmp, search_str):
        with open(wpa_tmp, 'r') as checklines:
            for line in checklines:
                if search_str in line:
                    logging.info(search_str + ' is already in the file: ' + checklines.name)
                    return True
        logging.info(search_str + ' is not found in: ' + checklines.name)
        return False

    def readpotfiledata(self, checkwpaconfig, potfile_source, wpa_tmp, wificonfigstore_tmp, wificonfigstoresoftap_tmp):
        with open(os.path.join(handshake_dir, 'wpa-sec.founds.potfile'), 'r') as checkpotfile:
            logging.info('Reading: ' + checkpotfile.name + ' Data.')
            for line in checkpotfile:
                potfiledata = line.split(':')
                latitude = potfiledata[0].rstrip()
                longitude = potfiledata[1].rstrip()
                bssid = potfiledata[2].rstrip()
                wpapassword = potfiledata[3].rstrip()
                logging.info('FOUND:')
                logging.info('BSSID: ' + bssid)
                logging.info('WpaPassword: ' + wpapassword)
                logging.info('Latitude: ' + latitude)
                logging.info('Longitude: ' + longitude)
                if checkwpaconfig(wpa_tmp, bssid):
                    logging.info(bssid + ' Found, Skipping.')
                else:
                    with open(wpa_tmp, 'a+') as outputfile:
                        logging.info('Found new network: ' + bssid)
                        logging.info('Appending to: ' + outputfile.name)
                        outputfile.writelines('\n')
                        outputfile.writelines('network={' + '\n')
                        outputfile.writelines('  scan_ssid=1' + '\n')
                        outputfile.writelines('  ssid="' + bssid + '"\n')
                        outputfile.writelines('  psk="' + wpapassword + '"\n')
                        outputfile.writelines('}\n')
                        outputfile.writelines('\n')

                    with open(wificonfigstore_tmp, 'a+') as outputfile:
                        logging.info('Found new network: ' + bssid)
                        logging.info('Appending to: ' + outputfile.name)
                        outputfile.writelines('\n')
                        outputfile.writelines('network={' + '\n')
                        outputfile.writelines('  scan_ssid=1' + '\n')
                        outputfile.writelines('  ssid="' + bssid + '"\n')
                        outputfile.writelines('  psk="' + wpapassword + '"\n')
                        outputfile.writelines('}\n')
                        outputfile.writelines('\n')

                    with open(wificonfigstoresoftap_tmp, 'a+') as outputfile:
                        logging.info('Found new network: ' + bssid)
                        logging.info('Appending to: ' + outputfile.name)
                        outputfile.writelines('\n')
                        outputfile.writelines('network={' + '\n')
                        outputfile.writelines('  scan_ssid=1' + '\n')
                        outputfile.writelines('  ssid="' + bssid + '"\n')
                        outputfile.writelines('  psk="' + wpapassword + '"\n')
                        outputfile.writelines('}\n')
                        outputfile.writelines('\n')