import logging
import json
import toml
import _thread
from datetime import datetime, timezone
from pwnagotchi import restart, plugins
from pwnagotchi.utils import save_config
from flask import abort
from flask import render_template_string
from flask import Response
import pwnagotchi.ui.fonts as fonts
from pwnagotchi.ui.components import LabeledValue
from pwnagotchi.ui.view import BLACK


def serializer(obj):
    if isinstance(obj, set):
        return list(obj)
    raise TypeError

class MyGPS(plugins.Plugin):
    __author__ = 'inbux.development@gmail.com'
    __version__ = '0.0.1'
    __license__ = 'MIT'
    __description__ = 'This plugin allows the user to receive GPS information from a connected phone using GPSLogger App.'
    
    LINE_SPACING = 10
    LABEL_SPACING = 0
    
    

    def __init__(self):
        self.timestamp = 0
        self.lat = 0
        self.long = 0
        
       

    def on_ready(self, agent):
        pass

    def on_internet_available(self, agent):
        pass

    def on_loaded(self):
        """
        Gets called when the plugin gets loaded
        """
        logging.info("myGPS: Plugin loaded.")
        self.timestamp = datetime.utcnow()



    def on_webhook(self, path, request):
        """
        Store current position
        """
        
        self.lat = float(request.args.get('lat', default=0))
        self.long = float(request.args.get('long', default=0))
        self.timestamp = request.args.get('time', default="0.0").split(".", 1)[0]
       
        if (self.lat !=0): 
            response_text= 'success'
        else:
            response_text='<html><body><h1>Use this URL for the <a href="https://gpslogger.app/" target="_blank">GPSLogger App</a></h1></body></html>' 
            
        ###logging.info('myGPS: Lat=%s Long=%s', self.lat,self.long )
        
        r = Response(response=response_text, status=200, mimetype='text/html')
        return r

    def on_handshake(self, agent, filename, access_point, client_station):
        
        gps_filename = filename.replace('.pcap', '.gps.json')
        
        data = {}
        data['Latitude'] = self.lat
        data['Longitude'] = self.long
        data['Updated'] = self.timestamp;
        
        gps = json.dumps(data)
        
        if all([self.lat, self.long]):
            logging.info("myGPS: saving GPS to %s (%s)" % (gps_filename, gps))
            with open(gps_filename, 'w+t') as f:
                f.write(gps)
            
    def on_ui_setup(self, ui):
        try:
            # Configure line_spacing
            line_spacing = int(self.options['linespacing'])
        except Exception:
            # Set default value
            line_spacing = self.LINE_SPACING

        try:
            # Configure position
            pos = self.options['position'].split(',')
            pos = [int(x.strip()) for x in pos]
            lat_pos = (pos[0] + 5, pos[1])
            lon_pos = (pos[0], pos[1] + line_spacing)
            alt_pos = (pos[0] + 5, pos[1] + (2 * line_spacing))
        except Exception:
            # Set default value based on display type
            if ui.is_waveshare_v2():
                lat_pos = (132, 74)
                lon_pos = (127, 84)
                alt_pos = (127, 94)
            elif ui.is_waveshare_v3():
                lat_pos = (135, 70)
                lon_pos = (200, 70)
                alt_pos = (130, 90)    
            elif ui.is_waveshare_v1():
                lat_pos = (130, 70)
                lon_pos = (125, 80)
                alt_pos = (130, 90)
            elif ui.is_inky():
                lat_pos = (127, 60)
                lon_pos = (122, 70)
                alt_pos = (127, 80)
            elif ui.is_waveshare144lcd():
                # guessed values, add tested ones if you can
                lat_pos = (67, 73)
                lon_pos = (62, 83)
                alt_pos = (67, 93)
            elif ui.is_dfrobot_v2():
                lat_pos = (127, 74)
                lon_pos = (122, 84)
                alt_pos = (127, 94)
            elif ui.is_waveshare27inch():
                lat_pos = (6, 120)
                lon_pos = (1, 135)
                alt_pos = (6, 150)
            else:
                # guessed values, add tested ones if you can
                lat_pos = (127, 51)
                lon_pos = (122, 61)
                alt_pos = (127, 71)

        ui.add_element(
            "latitude",
            LabeledValue(
                color=BLACK,
                label="Pos:",
                value="-",
                position=lat_pos,
                label_font=fonts.Small,
                text_font=fonts.Small,
                label_spacing=self.LABEL_SPACING,
            ),
        )
        ui.add_element(
            "longitude",
            LabeledValue(
                color=BLACK,
                label="",
                value="-",
                position=lon_pos,
                label_font=fonts.Small,
                text_font=fonts.Small,
                label_spacing=self.LABEL_SPACING,
            ),
        )
        

    def on_unload(self, ui):
        try:
            with ui._lock:
                ui.remove_element('latitude')
                ui.remove_element('longitude')
        except:
            pass        

    def on_ui_update(self, ui):
        
          if all([self.lat, self.long]):
                time_diff =  (((datetime.utcnow() - datetime.fromisoformat(self.timestamp)).seconds) / 60) 
                if (time_diff < 5):
                    ui.set("latitude", "%.4f " % self.lat)
                    ui.set("longitude", "%.4f " % self.long)
                else:
                    ui.set("latitude", "???")
                    ui.set("longitude", "???")
                    self.lat = 0
                    self.long = 0
