import logging
import os
from datetime import datetime, timezone
import toml
import pwnagotchi.plugins as plugins
from pwnagotchi.ui.components import LabeledValue
from pwnagotchi.ui.view import BLACK
import pwnagotchi.ui.fonts as fonts
from threading import Lock
import requests

class Wardriver(plugins.Plugin):
    __author__ = 'CyberArtemio'
    __version__ = '1.1'
    __license__ = 'GPL3'
    __description__ = 'A wardriving plugin for pwnagotchi. Saves all networks seen and uploads data to WiGLE once internet is available'

    DEFAULT_PATH = '/root/wardriver'
    DATABASE_NAME = 'wardriver_db.csv' # File name where all networks seen will be saved (if sessions mergin is enabled)

    def __init__(self):
        logging.debug('[WARDRIVER] Plugin created')
    
    def on_loaded(self):
        logging.info('[WARDRIVER] Plugin loaded (join the Discord server: https://discord.gg/5vrJbbW3ve)')

        self.__lock = Lock()
        
        if 'whitelist' in self.options:
            self.__whitelist = self.options['whitelist']
        else:
            self.__whitelist = []
        
        if 'csv_path' in self.options:
            self.__csv_path = self.options['csv_path']
        else:
            self.__csv_path = self.DEFAULT_PATH
        
        if 'ui' in self.options:
            self.__ui_enabled = self.options['ui']['enabled'] if 'enabled' in self.options['ui'] else False
            try:
                self.__ui_position = (self.options['ui']['position']['x'], self.options['ui']['position']['y'])
            except Exception:
                self.__ui_position = (5, 95)
        else:
            self.__ui_enabled = False
            self.__ui_position = (0, 0)
        
        self.__merge_sessions = self.options['merge_sessions'] if 'merge_sessions' in self.options else False
                
        if 'wigle' in self.options:
            self.__wigle_enabled = self.options['wigle']['enabled'] if 'enabled' in self.options['wigle'] else False
            self.__wigle_api_key = self.options['wigle']['api_key'] if 'api_key' in self.options['wigle'] else None
            self.__wigle_donate = self.options['wigle']['donate'] if 'donate' in self.options['wigle'] else False
            if self.__wigle_enabled and (not self.__wigle_api_key or self.__wigle_api_key == ''):
                logging.error('[WARDRIVER] Wigle enabled but no api key provided!')
                self.__wigle_enabled = False
        else:
            self.__wigle_enabled = False
            self.__wigle_api_key = None
            self.__wigle_donate = False
        
        if not os.path.exists(self.__csv_path):
            os.makedirs(self.__csv_path)
            logging.warning('[WARDRIVER] Created CSV directory')
        else:
            self.__clean_csv_directory()

        logging.info(f'[WARDRIVER] Saving session files inside {self.__csv_path}')
        
        if self.__wigle_enabled:
            logging.info('[WARDRIVER] Previous sessions will be uploaded to WiGLE once internet is available')

        self.__new_wardriving_session()

        if len(self.__whitelist) > 0:
            logging.info(f'[WARDRIVER] Ignoring {len(self.__whitelist)} networks')
    
    def on_ui_setup(self, ui):
        if self.__ui_enabled:
            logging.info('[WARDRIVER] Adding status text to ui')
            ui.add_element('wardriver', LabeledValue(color = BLACK,
                                               label = 'wardrive:',
                                               value = "- nets",
                                               position = self.__ui_position,
                                               label_font = fonts.Small,
                                               text_font = fonts.Small))

    def on_ui_update(self, ui):
        if self.__ui_enabled and self.ready:
            ui.set('wardriver', f'{len(self.__session_reported)} net')

    def on_unload(self, ui):
        if self.__ui_enabled:
            with ui._lock:
                ui.remove_element('wardriver')
        logging.info('[WARDRIVER] Plugin unloaded')
    
    def __clean_csv_directory(self):
        '''
        Remove empty session files and, if enabled, merge all previous sessions into one single file
        '''
        if self.__merge_sessions:
            networks_db = [] # All networks seen so far
            try:
                if os.path.exists(os.path.join(self.__csv_path, self.DATABASE_NAME)):
                    with open(os.path.join(self.__csv_path, self.DATABASE_NAME), 'r') as file:
                        file.readline() # skip first line (CSV header)
                        while True:
                            line = file.readline().strip()
                            if not line:
                                break
                            data = line.split(',')
                            if len(data) == 11:
                                network = data[0] + data[1] # Concatenate MAC and SSID
                                networks_db.append(network)
                else:
                    # initialize database file
                    with open(os.path.join(self.__csv_path, self.DATABASE_NAME), 'w') as file:
                        file.write('MAC,SSID,AuthMode,FirstSeen,Channel,RSSI,CurrentLatitude,CurrentLongitude,AltitudeMeters,AccuracyMeters,Type\n')
            except Exception as e:
                logging.critical(f'[WARDRIVER] Error while opening {self.DATABASE_NAME} file: {e}')

        sessions = [ os.path.join(self.__csv_path, file) for file in os.listdir(self.__csv_path) if os.path.isfile(os.path.join(self.__csv_path, file)) and file.endswith(".csv") and file != self.DATABASE_NAME ]
        
        if len(sessions) > 0:
            logging.info('[WARDRIVER] Cleaning directory...')
            for file in sessions:
                try:
                    with open(file, 'r') as session_file:
                        session_data = session_file.readlines()
                        
                        if len(session_data) <= 3:
                            os.remove(file)
                            logging.info(f'[WARDRIVER] File {file} removed')
                        elif self.__merge_sessions and (not self.__wigle_enabled or (self.__wigle_enabled and 'uploaded' in os.path.basename(file))):
                            networks = session_data[2:] # Skip first 2 lines (header)
                            with open(os.path.join(self.__csv_path, self.DATABASE_NAME), 'a') as database:
                                for network in networks:
                                    data = network.strip().split(',')
                                    if len(data) == 11 and data[0] + data[1] not in networks_db:
                                        database.write(network)
                                        networks_db.append(network)
                            os.remove(file)
                            logging.info(f'[WARDRIVER] Merged {file} into {os.path.join(self.__csv_path, self.DATABASE_NAME)}')

                except Exception as e:
                    logging.error(f'[WARDRIVER] Error while processing {file}: {e}')
        
    def __wigle_info(self):
        '''
        Return info used in CSV pre-header
        '''
        with open('/etc/pwnagotchi/config.toml', 'r') as config_file:
            data = toml.load(config_file)
            
            # Whitelist global SSIDs
            for ssid in data['main']['whitelist']:
                if ssid not in self.__whitelist:
                    self.__whitelist.append(ssid)
            
            # Preheader formatting
            file_format = 'WigleWifi-1.4'
            app_release = self.__version__
            # Device model
            try:
                with open('/sys/firmware/devicetree/base/model', 'r') as model_info:
                    model = model_info.read()
            except Exception:
                model = 'unknown'
            # OS version
            try:
                with open('/etc/os-release', 'r') as release_info:
                    release = release_info.read().split('\n')[0].split('=')[-1].replace('"', '')
            except Exception:
                release = 'unknown'
            # Pwnagotchi name
            device = data['main']['name']
            # Pwnagotchi display model
            display = data['ui']['display']['type'] # Pwnagotchi display
            # CPU model
            try:
                with open('/proc/cpuinfo', 'r') as cpu_model:
                    board = cpu_model.read().split('\n')[1].split(':')[1][1:]
            except Exception:
                board = 'unknown'
            
            # Brand: currently set equal to model
            brand = model

            return {
                'file_format': file_format,
                'app_release': app_release,
                'model': model,
                'release': release,
                'device': device,
                'display': display,
                'board': board,
                'brand': brand
            }
 
    def __new_wardriving_session(self):
        self.ready = False
        now = datetime.now()
        self.__session_reported = []
        session_name = now.strftime('%Y-%m-%dT%H:%M:%S')
        session_file = os.path.join(self.__csv_path, f'{session_name}.csv')
        logging.info(f'[WARDRIVER] Initializing new session file {session_file}')
        self.__session_file = session_file
        try:
            with open(self.__session_file, 'w') as csv:
                # See: https://api.wigle.net/csvFormat.html
                # CSV pre-header
                preheader_data = self.__wigle_info()
                csv.write(f'{preheader_data["file_format"]},{preheader_data["app_release"]},{preheader_data["model"]},{preheader_data["release"]},{preheader_data["device"]},{preheader_data["display"]},{preheader_data["board"]},{preheader_data["brand"]}\n')
                # CSV header
                csv.write('MAC,SSID,AuthMode,FirstSeen,Channel,RSSI,CurrentLatitude,CurrentLongitude,AltitudeMeters,AccuracyMeters,Type\n')

                logging.info('[WARDRIVER] Session file initialized. Ready to wardrive!')
                self.ready = True
        except Exception as e:
            logging.critical(f'[WARDRIVER] Error while creating session file! {e}')

    def __filter_whitelist_aps(self, unfiltered_aps):
        '''
        Filter whitelisted networks
        '''
        filtered_aps = [ ap for ap in unfiltered_aps if ap['hostname'] not in self.__whitelist ]
        return filtered_aps
    
    def __filter_reported_aps(self, unfiltered_aps):
        '''
        Filter already reported networks
        '''
        filtered_aps = [ ap for ap in unfiltered_aps if (ap['mac'], ap['hostname']) not in self.__session_reported ]
        return filtered_aps
    
    def __ap_to_csv(self, ap, coordinates):
        bssid = ap['mac']
        ssid = ap['hostname'] if ap['hostname'] != '<hidden>' else ''
        capabilities = ''
        if ap['encryption'] != '':
            capabilities = f'{capabilities}[{ap["encryption"]}]'
        if ap['cipher'] != '':
            capabilities = f'{capabilities}[{ap["cipher"]}]'
        if ap['authentication'] != '':
            capabilities = f'{capabilities}[{ap["authentication"]}]'
        first_timestamp_seen = datetime.now().astimezone(timezone.utc).strftime('%Y-%m-%d %H:%M:%S') # Use now() instead of bettercap firstSeen
        channel = ap['channel']
        rssi = ap['rssi']
        latitude = coordinates['latitude']
        longitude = coordinates['longitude']
        altitude = coordinates['altitude']
        accuracy = coordinates['accuracy']
        type = 'WIFI'

        return f'{bssid},{ssid},{capabilities},{first_timestamp_seen},{channel},{rssi},{latitude},{longitude},{altitude},{accuracy},{type}\n'
    
    def __update_csv_file(self, aps, coordinates):
        with open(self.__session_file, '+a') as file:
            for ap in aps:
                try:
                    file.write(self.__ap_to_csv(ap, coordinates))
                    self.__session_reported.append((ap['mac'], ap['hostname']))
                except Exception as e:
                    logging.error(f'[WARDRIVER] Error while logging to csv file: {e}')

    def on_unfiltered_ap_list(self, agent, aps):
        info = agent.session()
        gps_data = info["gps"]

        if not self.ready: # it is ready once the session file has been initialized with pre-header and header
            logging.error('[WARDRIVER] Plugin not ready... skip wardriving log')

        if gps_data and all([
            # avoid 0.000... measurements
            gps_data["Latitude"], gps_data["Longitude"]
        ]):
            coordinates = {
                'latitude': gps_data["Latitude"],
                'longitude': gps_data["Longitude"],
                'altitude': gps_data["Altitude"],
                'accuracy': 50 # TODO: how can this be calculated?
            }

            filtered_aps = self.__filter_whitelist_aps(aps)
            filtered_aps = self.__filter_reported_aps(filtered_aps)

            if len(filtered_aps) > 0:
                logging.info(f'[WARDRIVER] Discovered {len(filtered_aps)} new networks')
                self.__update_csv_file(filtered_aps, coordinates)
        else:
            logging.warning("[WARDRIVER] GPS not available... skip wardriving log")
        
    def on_internet_available(self, agent):
        if self.__wigle_enabled and not self.__lock.locked():
            with self.__lock:
                sessions_to_upload = [ os.path.join(self.__csv_path, file) for file in os.listdir(self.__csv_path) if os.path.isfile(os.path.join(self.__csv_path, file)) and file.endswith(".csv") and file != os.path.basename(self.__session_file) and not 'uploaded' in file  and file != self.DATABASE_NAME ]
                if len(sessions_to_upload) > 0:
                    logging.info(f'[WARDRIVER] Uploading previous sessions on WiGLE ({len(sessions_to_upload)} sessions) - current session will not be uploaded')
                    headers = {
                        'Authorization': f'Basic {self.__wigle_api_key}',
                        'Accept': 'application/json'
                    }
                    
                    if self.__merge_sessions:
                        networks_db = [] # All networks seen so far
                        with open(os.path.join(self.__csv_path, self.DATABASE_NAME), 'r') as file:
                            file.readline() # skip first line (CSV header)
                            while True:
                                line = file.readline().strip()
                                if not line:
                                    break
                                data = line.split(',')
                                if len(data) == 11:
                                    network = data[0] + data[1] # Concatenate MAC and SSID
                                    networks_db.append(network)

                    for file in sessions_to_upload:
                        try:
                            with open(file, 'r') as session_file:
                                session_data = session_file.read()
                        except Exception as e:
                            logging.error(f'[WARDRIVER] Failed reading file {file}: {e}')
                            continue

                        data = {
                            'donate': 'on' if self.__wigle_donate else 'off'
                        }

                        file_form = {
                            'file': (os.path.basename(file), session_data)
                        }

                        try:
                            response = requests.post(
                                url = 'https://api.wigle.net/api/v2/file/upload',
                                headers = headers,
                                data = data,
                                files = file_form,
                                timeout = 300
                            )
                            response.raise_for_status()
                            try:
                                if not self.__merge_sessions:
                                    os.rename(file, file.replace('.csv', '_uploaded.csv'))
                                else:
                                    session_data = session_data.split('\n')
                                    networks = session_data[2:] # Skip first 2 lines (header)
                                    with open(os.path.join(self.__csv_path, self.DATABASE_NAME), 'a') as database:
                                        for network in networks:
                                            data = network.strip().split(',')
                                            if len(data) == 11 and data[0] + data[1] not in networks_db:
                                                database.write(network)
                                                networks_db.append(network)
                                    os.remove(file)
                                logging.info(f'[WARDRIVER] Uploaded successfully {file} on WiGLE')
                            except Exception as e:
                                logging.critical(f'[WARDRIVER] Error while marking {file} as uploaded {e}')
                        except Exception as e:
                            logging.error(f'[WARDRIVER] Failed uploading file {file}: {e}')
                            continue
