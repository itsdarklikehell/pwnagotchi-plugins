import logging
import requests, uuid, linecache
import subprocess
import os
import json
import pwnagotchi.plugins as plugins
from threading import Lock
from pwnagotchi.ui.components import LabeledValue
from pwnagotchi.utils import StatusFile, remove_whitelisted
from json.decoder import JSONDecodeError
'''
hcxpcapngtool needed, to install:
> git clone https://github.com/ZerBea/hcxtools.git
> cd hcxtools
> apt-get install libcurl4-openssl-dev libssl-dev zlib1g-dev
> make
> sudo make install
'''


class hashespwnagotchi(plugins.Plugin):
    __author__ = 'meow@hashes.pw'
    __version__ = '0.0.1'
    __license__ = 'GPL3'
    __description__ = 'uploads handshakes to https://hashes.pw'
    
    @property 
    def headers(self):
        return {'Authorization': "Bearer %s" % (self.token), 'Content-type': 'application/json'}
        
    def __init__(self):
        self.ready = False
        self.lock = Lock()
        try:
            self.report = StatusFile('/root/.hashespw_uploads', data_format='json')
        except JSONDecodeError:
            os.remove("/root/.hashespw_uploads")
            self.report = StatusFile('/root/.hashespw_uploads', data_format='json')
        self.options = dict()
        self.skip = list()
        self.token = None
        self.uuid = None
        
    def on_loaded(self):
        """
        Gets called when the plugin gets loaded
        """
        if 'api_key' not in self.options or ('api_key' in self.options and not self.options['api_key']):
            logging.error("hashespwnagotchi: api_key isn't set. Can't upload to hashes.pw")
            return

        if 'api_url' not in self.options or ('api_url' in self.options and not self.options['api_url']):
            logging.error("hashespwnagotchi: api_url isn't set. Can't upload, no endpoint configured.")
            return

        self.ready = True
        logging.info("hashespwnagotchi: plugin loaded")


    # called when everything is ready and the main loop is about to start
    def on_config_changed(self, config):
        handshake_dir = config['bettercap']['handshakes']
        self.uuid = str(uuid.uuid5(uuid.NAMESPACE_OID, config['main']['name']))
        
        try:
            self.report = StatusFile('/root/.hashespw_uploads', data_format='json')
        except JSONDecodeError:
            os.remove("/root/.hashespw_uploads")
            self.report = StatusFile('/root/.hashespw_uploads', data_format='json')
            
        if 'interval' not in self.options or not (self.status.newer_then_hours(self.options['interval'])):
            logging.info('[hashie] Starting batch conversion of pcap files')
            with self.lock:
                self._process_stale_pcaps(handshake_dir)
                
    def on_bored(self, agent):
        self._report_handshakes(agent)
          
    def on_internet_available(self, agent):
        self._report_handshakes(agent)

    def on_handshake(self, agent, filename, access_point, client_station):
        with self.lock:
            handshake_status = []
            fullpathNoExt = filename.split('.')[0]
            name = filename.split('/')[-1:][0].split('.')[0]
            
            if os.path.isfile(fullpathNoExt +  '.22000'):
                handshake_status.append('Already have {}.22000 (EAPOL)'.format(name))
            elif self._writeEAPOL(filename):
                handshake_status.append('Created {}.22000 (EAPOL) from pcap'.format(name))
                self._report_handshakes(agent)
            
            if os.path.isfile(fullpathNoExt +  '.16800'):
                handshake_status.append('Already have {}.16800 (PMKID)'.format(name))
            elif self._writePMKID(filename, access_point):
                handshake_status.append('Created {}.16800 (PMKID) from pcap'.format(name))
            
            if handshake_status:
                logging.info('[hashie] Good news:\n\t' + '\n\t'.join(handshake_status))
    
    def _writeEAPOL(self, fullpath):
        fullpathNoExt = fullpath.split('.')[0]
        filename = fullpath.split('/')[-1:][0].split('.')[0]
        result = subprocess.getoutput('hcxpcapngtool -o {}.22000 {} >/dev/null 2>&1'.format(fullpathNoExt,fullpath))
        if os.path.isfile(fullpathNoExt +  '.22000'):
            logging.debug('[hashie] [+] EAPOL Success: {}.22000 created'.format(filename))
            return True
        else:
            return False
        
    def _writePMKID(self, fullpath, apJSON):
        fullpathNoExt = fullpath.split('.')[0]
        filename = fullpath.split('/')[-1:][0].split('.')[0]
        result = subprocess.getoutput('hcxpcapngtool -k {}.16800 {} >/dev/null 2>&1'.format(fullpathNoExt,fullpath))
        if os.path.isfile(fullpathNoExt + '.16800'):
            logging.debug('[hashie] [+] PMKID Success: {}.16800 created'.format(filename))
            return True
        else: #make a raw dump
            result = subprocess.getoutput('hcxpcapngtool -K {}.16800 {} >/dev/null 2>&1'.format(fullpathNoExt,fullpath))
            if os.path.isfile(fullpathNoExt + '.16800'):
                if self._repairPMKID(fullpath, apJSON) == False:
                    logging.debug('[hashie] [-] PMKID Fail: {}.16800 could not be repaired'.format(filename))
                    return False
                else:
                    logging.debug('[hashie] [+] PMKID Success: {}.16800 repaired'.format(filename))
                    return True
            else:
                logging.debug('[hashie] [-] Could not attempt repair of {} as no raw PMKID file was created'.format(filename))
                return False
    
    def _repairPMKID(self, fullpath, apJSON):
        hashString = ""
        clientString = []
        fullpathNoExt = fullpath.split('.')[0]
        filename = fullpath.split('/')[-1:][0].split('.')[0]
        logging.debug('[hashie] Repairing {}'.format(filename))
        with open(fullpathNoExt + '.16800','r') as tempFileA:
            hashString = tempFileA.read()
        if apJSON != "": 
            clientString.append('{}:{}'.format(apJSON['mac'].replace(':',''), apJSON['hostname'].encode('hex')))
        else:
            #attempt to extract the AP's name via hcxpcapngtool
            result = subprocess.getoutput('hcxpcapngtool -X /tmp/{} {} >/dev/null 2>&1'.format(filename,fullpath))
            if os.path.isfile('/tmp/' + filename):
                with open('/tmp/' + filename,'r') as tempFileB:
                    temp = tempFileB.read().splitlines()
                    for line in temp:
                        clientString.append(line.split(':')[0] + ':' + line.split(':')[1].strip('\n').encode().hex())
                os.remove('/tmp/{}'.format(filename))
            #attempt to extract the AP's name via tcpdump
            tcpCatOut = subprocess.check_output("tcpdump -ennr " + fullpath  + " \"(type mgt subtype beacon) || (type mgt subtype probe-resp) || (type mgt subtype reassoc-resp) || (type mgt subtype assoc-req)\" 2>/dev/null | sed -E 's/.*BSSID:([0-9a-fA-F:]{17}).*\\((.*)\\).*/\\1\t\\2/g'",shell=True).decode('utf-8')
            if ":" in tcpCatOut:
                for i in tcpCatOut.split('\n'):
                    if ":" in i:
                        clientString.append(i.split('\t')[0].replace(':','') + ':' + i.split('\t')[1].strip('\n').encode().hex())
        if clientString:
            for line in clientString:
                if line.split(':')[0] == hashString.split(':')[1]: #if the AP MAC pulled from the JSON or tcpdump output matches the AP MAC in the raw 16800 output
                    hashString = hashString.strip('\n') + ':' + (line.split(':')[1])
                    if (len(hashString.split(':')) == 4) and not (hashString.endswith(':')):
                        with open(fullpath.split('.')[0] + '.16800','w') as tempFileC:
                            logging.debug('[hashie] Repaired: {} ({})'.format(filename,hashString))
                            tempFileC.write(hashString + '\n')
                        return True
                    else:
                        logging.debug('[hashie] Discarded: {} {}'.format(line, hashString))
        else:
            os.remove(fullpath.split('.')[0] + '.16800')
            return False
    
    def _process_stale_pcaps(self, handshake_dir):
        handshakes_list = [os.path.join(handshake_dir, filename) for filename in os.listdir(handshake_dir) if filename.endswith('.pcap')]
        failed_jobs = []
        successful_jobs = []
        lonely_pcaps = []
        for num, handshake in enumerate(handshakes_list):
            fullpathNoExt = handshake.split('.')[0]
            pcapFileName = handshake.split('/')[-1:][0]
            if not os.path.isfile(fullpathNoExt + '.22000'): #if no 22000, try
                if self._writeEAPOL(handshake):
                    successful_jobs.append('22000: ' + pcapFileName)
                else:
                    failed_jobs.append('22000: ' + pcapFileName)
            if not os.path.isfile(fullpathNoExt + '.16800'): #if no 16800, try
                if self._writePMKID(handshake, ""):
                    successful_jobs.append('16800: ' + pcapFileName)
                else:
                    failed_jobs.append('16800: ' + pcapFileName)
                    if not os.path.isfile(fullpathNoExt + '.22000'): #if no 16800 AND no 22000
                        lonely_pcaps.append(handshake)
                        logging.debug('[hashie] Batch job: added {} to lonely list'.format(pcapFileName))
            if ((num + 1) % 50 == 0) or (num + 1 == len(handshakes_list)): #report progress every 50, or when done
                logging.info('[hashie] Batch job: {}/{} done ({} fails)'.format(num + 1,len(handshakes_list),len(lonely_pcaps)))
        if successful_jobs:
            logging.info('[hashie] Batch job: {} new handshake files created'.format(len(successful_jobs)))
        if lonely_pcaps:
            logging.info('[hashie] Batch job: {} networks without enough packets to create a hash'.format(len(lonely_pcaps)))
            self._getLocations(lonely_pcaps)
        
    def _getLocations(self, lonely_pcaps):
        #export a file for webgpsmap to load
        with open('/root/.incompletePcaps','w') as isIncomplete:
            count = 0
            for pcapFile in lonely_pcaps:
                filename = pcapFile.split('/')[-1:][0] #keep extension
                fullpathNoExt = pcapFile.split('.')[0]
                isIncomplete.write(filename + '\n')
                if os.path.isfile(fullpathNoExt +  '.gps.json') or os.path.isfile(fullpathNoExt +  '.geo.json') or os.path.isfile(fullpathNoExt +  '.paw-gps.json'):
                    count +=1
            if count != 0:
                logging.info('[hashie] Used {} GPS/GEO/PAW-GPS files to find lonely networks, go check webgpsmap! ;)'.format(str(count)))
            else:
                logging.info('[hashie] Could not find any GPS/GEO/PAW-GPS files for the lonely networks'.format(str(count)))
        
    def _getLocationsCSV(self, lonely_pcaps):
        #in case we need this later, export locations manually to CSV file, needs try/catch/paw-gps format/etc.
        locations = []
        for pcapFile in lonely_pcaps:
            filename = pcapFile.split('/')[-1:][0].split('.')[0]
            fullpathNoExt = pcapFile.split('.')[0]
            if os.path.isfile(fullpathNoExt +  '.gps.json'):
                with open(fullpathNoExt + '.gps.json','r') as tempFileA:
                    data = json.load(tempFileA)
                    locations.append(filename + ',' + str(data['Latitude']) + ',' + str(data['Longitude']) + ',50')
            elif os.path.isfile(fullpathNoExt +  '.geo.json'):
                with open(fullpathNoExt + '.geo.json','r') as tempFileB:
                    data = json.load(tempFileB)
                    locations.append(filename + ',' + str(data['location']['lat']) + ',' + str(data['location']['lng']) + ',' + str(data['accuracy']))
            elif os.path.isfile(fullpathNoExt +  '.paw-gps.json'):
                with open(fullpathNoExt + '.paw-gps.json','r') as tempFileC:
                    data = json.load(tempFileC)
                    locations.append(filename + ',' + str(data['lat']) + ',' + str(data['long']) + ',50')
        if locations:
            with open('/root/locations.csv','w') as tempFileD:
                for loc in locations:
                    tempFileD.write(loc + '\n')
            logging.info('[hashie] Used {} GPS/GEO files to find lonely networks, load /root/locations.csv into a mapping app and go say hi!'.format(len(locations)))

    def _upload_EAPOL(self, path, pwnagotchi = None):
        #logging.info(path) 
        essid = self._essid_from_path(path)
        #logging.info(essid)
        payload = {
            'name': pwnagotchi,
            'essid': essid,
            'bssid': self._bssid_from_path(path, essid),
            'value': self._single_line_from_file(path) 
        }
        
        r = self._post("pwnagotchi", payload)
        
        if r.status_code != 200 and r.status_code != 204:
            try: 
                decode_error = json.loads(r.content)
                if decode_error['value'][0] == 'already exists':
                    return
            except Exception as e:
                logging.warn(e)
            
            raise ValueError("failure to create new handshake on hashes.pw: %s" % r.content)
            
        
    def _report_handshakes(self, agent):
        if not self.ready or self.lock.locked() or not self._connected_to_internet():
            return
        
        with self.lock:
            config = agent.config()
            display = agent.view()
            reported = self.report.data_field_or('reported', default=list())
            handshake_dir = config['bettercap']['handshakes']
            handshake_filenames = os.listdir(handshake_dir)
            handshake_paths = [os.path.join(handshake_dir, filename) for filename in handshake_filenames if
                               filename.endswith('.22000')]
            # handshake_paths = remove_whitelisted(handshake_paths, self.options['whitelist'])
            handshake_new = set(handshake_paths) - set(reported) - set(self.skip)
            
            if handshake_new:
                logging.info("hashespwnagotchi: have pwns to upload")
                for idx, handshake in enumerate(handshake_new):
                    display.on_uploading(f"hashes.pw ({idx + 1}/{len(handshake_new)})")

                    try:
                        logging.info("sending contents of %s to hashes.pw" % handshake)
                        self._upload_EAPOL(handshake, config['main']['name'])
                        reported.append(handshake)
                        self.report.update(data={'reported': reported})
                        logging.debug("hashespwnagotchi: successfully reported %s", handshake)
                    except requests.exceptions.RequestException as req_e:
                        self.skip.append(handshake)
                        logging.debug("hashespwnagotchi: %s", req_e)
                        continue
                    except OSError as os_e:
                        logging.debug("hashespwnagotchi: %s", os_e)
                        continue
                    except ValueError as v_e:
                        logging.warn("failure to send contents of %s to hashes.pw", handshake)
                        logging.warn(v_e)                        
                        continue
                        

                display.on_normal()
                
    def _validate_or_fetch_token(self) -> None:
        if self.token == None:
            full_path = self._uri_format(self.options['api_url'], 'agent/pwnagotchi')
            
            # let it raise
            r = requests.post(full_path, json={'uuid': self.uuid, 'auth_only': True}, headers={'Authorization': "Token token=%s" % (self.options['api_key'])})
            
            response = json.loads(r.content)
            self.token = response['token']
            # logging.info(self.token)
            if self.token == None:
                raise ValueError('Failed to obtain a token response')
                
    def _post(self, path, data = {}) -> requests.Response:
        self._validate_or_fetch_token()
        full_path = self._uri_format(self.options['api_url'], path)
        r = requests.post(full_path, json=data, headers=self.headers)
        if r.status_code == 403:
            self.token = None
            self._validate_or_fetch_token()
            r = requests.post(full_path, json=data, headers=self.headers)
        return r

    def _uri_format(self, root_path, route):
        uri = root_path
        if route:
            uri = "%s/%s" % (root_path, route)
        if uri.endswith('/'):
            uri = uri[:-1]
        return uri
        
    def _single_line_from_file(self, file):
        if os.path.isfile(file):
            with open( file, 'r', encoding="ISO-8859-1", errors="ignore" ) as fp:
                for _, line in enumerate(fp):
                    return line.strip()
    
    def _essid_from_path(self, path):
        file = path.split("/")[-1]
        if '_' in file:
            return file.split('_')[0]
        else:
            return None
            
    def _bssid_from_path(self, path, essid = None):
        file = path.split("/")[-1]
        if essid == None:
            return file.split(".")[0]
        else:
            return file.split(".")[0].replace(essid + "_", "")
    
    def _connected_to_internet(self):
        try:
            r = requests.get('https://google.com', timeout=5)
            return True
        except (requests.ConnectionError, requests.Timeout) as exception:
            return False
