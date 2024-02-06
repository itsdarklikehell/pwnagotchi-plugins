# See readme at @'https://github.com/rai68/gpsd-easy'
# for installation

# * How to install gpsd with PPS time syncing (requires a non USB GPS that has a PPS pin, but will give you sub microsecond time accuracy (1.000_0##_###s))
#
# to be written

# * example config
# | main.plugins.gpsdeasy.enabled = true
# | main.plugins.gpsdeasy.host = '127.0.0.1'
# | main.plugins.gpsdeasy.port = 2947
# | main.plugins.gpsdeasy.device = '/dev/ttyS0' #<-- change to serial port of device
# | main.plugins.gpsdeasy.fields = ['fix','lat','lon','alt','speed'] #<-- Any order or amount, you can also use custom values from POLL.TPV; on gpsd documents (https://gpsd.gitlab.io/gpsd/gpsd_json.html#_tpv)
# | main.plugins.gpsdeasy.speedUnit = 'kph' or 'mph'
# | main.plugins.gpsdeasy.distanceUnit = 'm' or 'ft'
# | main.plugins.gpsdeasy.bettercap = true #<--- report to bettercap

import numpy as np
import base64
import io

from matplotlib.pyplot import rc, grid, figure, plot, rcParams, savefig, close
from math import radians

from flask import abort
from flask import render_template_string

import subprocess

import time
import json
import logging

import socket

import requests

import pwnagotchi.plugins as plugins
import pwnagotchi.ui.fonts as fonts
from pwnagotchi.ui.components import LabeledValue
from pwnagotchi.ui.view import BLACK

import pwnagotchi


def is_connected():
    try:
        # check DNS
        host = 'https://api.opwngrid.xyz/api/v1/uptime'
        r = requests.get(host, headers=None, timeout=(30.0, 60.0))
        if r.json().get('isUp'):
            return True
    except:
        pass
    return False


class GPSD:
    def __init__(self, gpsdhost, gpsdport, plugin):
        self.socket = None
        self.stream = None
        self.connect(host=gpsdhost, port=gpsdport)
        self.running = True
        self.spacing = 0
        self.plugin = plugin

    def connect(self, host="127.0.0.1", port=2947):
        """ Connect to a GPSD instance
        :param host: hostname for the GPSD server
        :param port: port for the GPSD server
        "
)
        
        logging.info("[gpsdeasy] Connecting to gpsd socket at {}:{}".format(host, port))
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((host, port))
            self.stream = self.socket.makefile(mode="rw")
        except:
            logging.warning("[gpseasy] error occured during socket setup, try power cycle the device")

        self.stream.write('?WATCH={"enable":true}\n')
        self.stream.flush()

        welcome_raw = self.stream.readline()
        welcome = json.loads(welcome_raw)
        if welcome['class'] != "VERSION":
            raise Exception(
                "Unexpected data received as welcome. Is the server a gpsd 3 server?")
        logging.info("[gpsdeasy] connected")

    def get_current(self,poll):
        """ Poll gpsd for a new position ("tpv") and or sats ("sky")
        :return: GpsResponse
        "
)
        if self.running != True:
            return None
        
        self.stream.write("?POLL;\n")
        self.stream.flush()
        raw = self.stream.readline()
        data = json.loads(raw)
        
        if 'class' in data:
            if data['class'] == 'POLL':
                # if poll is one of these give it
                if 'tpv' in data and poll == 'tpv':
                    return data['tpv'][0]
                elif 'sky' in data and poll == 'sky':
                    return data['sky'][0]
                else: return None # else return None

            elif data['class'] == 'DEVICES':
                return None
        else:
            return None


class Gpsdeasy(plugins.Plugin):
    __author__ = "discord@rai68"
    __version__ = "1.3.0"
    __license__ = "LGPL"
    __description__ = "uses gpsd to report lat/long on the screen and setup bettercap pcap gps logging"

    def __init__(self):
        self.gpsd = None
        self.fields = ['fix','lat','lon','alt','spd']
        self.speedUnit = 'ms'
        self.distanceUnit = 'm'
        self.element_pos_x = 130
        self.element_pos_y = 47
        self.host = '127.0.0.1'
        self.port = 2947
        self.spacing = 12
        self.agent = None
        self.bettercap = True
        self.loaded = False
        self.ui_setup = False
        self.valid_device = False
        self.running = False
        
        # display setup
        self._black = 0x00
        
        self.pps_device = ''
        self.device = ''
        self.baud = 9600
        
        # auto setup
        self.auto = True

    def setup(self):
        # will run every load but only finish once if services haven't been set up.
        if self.auto is False:
            return
        
        aptRes = subprocess.run(['apt', '-qq', 'list', 'gpsd'],
                                stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True)
        if 'installed' not in aptRes.stdout:
            logging.info('[gpsdeasy] GPSd not installed, trying now. This may take up to 5minutes just let me run')
            if is_connected():
                subprocess.run(['apt', 'install', '-y', 'gpsd', 'gpsd-clients'])
            else:
                logging.error('[gpsdeasy] GPSd not installed, no internet. Please connect and reload pwnagotchi')
                return False
                
        logging.info('[gpsdeasy] GPSd should be installed')
        baseConf = [
            'GPSD_OPTIONS="-n -N -b"\n',
            f'BAUDRATE="{self.baud}"\n',
            f'MAIN_GPS="{self.device}"\n',
            f'PPS_DEVICES="{self.pps_device}"\n',
            'GPSD_SOCKET="/var/run/gpsd.sock"\n',
            '/bin/stty -F ${MAIN_GPS} ${BAUDRATE}\n',
            '/bin/setserial ${MAIN_GPS} low_latency\n'
        ]
        baseService = [
            '[Unit]\n',
            'Description=GPS (Global Positioning System) Daemon for pwnagotchi\n',
            'Requires=gpsd.socket\n',
            '[Service]\n',
            'EnvironmentFile=/etc/default/gpsd\n',
            'ExecStart=/usr/sbin/gpsd $GPSD_OPTIONS $MAIN_GPS $PPS_DEVICES\n',
            '[Install]\n',
            'WantedBy=multi-user.target\n',
            'Also=gpsd.socket\n',
        ]
        
        logging.info("[gpsdeasy] Updating autoconfig if changed")
        with open("/etc/default/gpsd", 'a+', newline="\n") as gpsdConf:
            fileLinesConf = gpsdConf.readlines()
            changedConf = baseConf != fileLinesConf
            if changedConf:
                gpsdConf.seek(0)
                gpsdConf.truncate()
                for line in baseConf:
                    gpsdConf.write(line)

        with open("/etc/systemd/system/gpsd.service", 'a+', newline="\n") as gpsdService:
            fileLinesService = gpsdService.readlines()
            changedService = baseService != fileLinesService
            if changedService:
                gpsdService.seek(0)
                gpsdService.truncate()
                for line in baseService:
                    gpsdService.write(line)

        changed = changedConf or changedService
        logging.info(f"[gpsdeasy] finished updating configs, Updated: {changed}")

        if changed:
            subprocess.run(["systemctl", "stop", "gpsd.service"])
            subprocess.run(["systemctl", "daemon-reload"])

        serRes = subprocess.run(['systemctl', "status","gpsd.service"],stdout = subprocess.PIPE,stderr = subprocess.STDOUT,universal_newlines = True)
        if 'active (running)' not in serRes.stdout:
            subprocess.run(["systemctl", "start","gpsd.service"])
        return True

    def on_loaded(self):
        #gpsd host:port
        logging.info("[gpsdeasy] plugin loading begin")
        if 'host' in self.options:
            self.host = self.options['host']
            
        if 'port' in self.options:
            self.port = self.options['port']
        
        #auto setup variables
        if 'disableAutoSetup' in self.options:
            self.auto = self.options['disableAutoSetup']
            
        if 'baud' in self.options:
            self.baud = self.options['baud']
            
        if 'device' in self.options:
            self.device = self.options['device']
            
        if 'pps_device' in self.options:
            self.pps_device = self.options['pps_device']
            
        logging.debug("[gpsdeasy] starting major setup function")
        res = self.setup()
        logging.debug("[gpsdeasy] ended major setup function, status: {res}")
        # starts gpsd after setting up
        self.gpsd = GPSD(self.host, self.port, self)

        # other variables like display and bettercap
        if 'bettercap' in self.options:
            self.bettercap = self.options['bettercap']
        
        if 'fields' in self.options:
            self.fields = self.options['fields']
            
        if 'speedUnit' in self.options:
            self.speedUnit = self.options['speedUnit']
        
        if 'distanceUnit' in self.options:
            self.distanceUnit = self.options['distanceUnit']

        if 'topleft_x' in self.options:
            self.element_pos_x = self.options['topleft_x']
            
        if 'topleft_y' in self.options:
            self.element_pos_y = self.options['topleft_y']

        if 'invert' in pwnagotchi.config['ui'] and pwnagotchi.config['ui']['invert'] == 1 or BLACK == 0xFF:
            self._black = 0xFF

        self.loaded = True
        logging.info("[gpsdeasy] plugin loading finished!")

    def on_ready(self, agent):
        while not self.loaded:
            time.sleep(0.1)
        self.agent = agent
        if self.bettercap:
            logging.info(f"[gpsdeasy] enabling bettercap's gps module for {self.options['host']}:{self.options['port']}")
            try:
                agent.run("gps off")
            except Exception:
                logging.info(f"[gpsdeasy] bettercap gps was already off")
                pass

            agent.run(f"set gps.device {self.options['host']}:{self.options['port']}; set gps.baudrate 9600; gps on")
            logging.info("[gpsdeasy] bettercap set and on")
            self.running = True
        else:
            try:
                agent.run("gps off")
            except Exception:
                logging.info(f"[gpsdeasy] bettercap gps was already off")
                pass
            logging.info("[gpsdeasy] bettercap gps reporting disabled")

    def on_handshake(self, agent, filename, access_point, client_station):
        coords = self.gpsd.get_current('tpv')
        if 'lat' and 'lon' in coords:
            gps_filename = filename.replace(".pcap", ".gps.json")
            logging.info(f"[gpsdeasy] saving GPS to {gps_filename} ({coords})")
            with open(gps_filename, "w+t") as fp:
                struct = {
                    'Longitude': coords['lon'],
                    'Latitude': coords['lat']
                }
                json.dump(struct, fp)
        else:
            logging.info("[gpsdeasy] not saving GPS: no fix")

    def on_ui_setup(self, ui):
        # add coordinates for other displays
        while not self.loaded:
            time.sleep(0.1)
        label_spacing = 0
        logging.info(f"[gpsdeasy] setting up UI elements: {self.fields}")
        for i,item in enumerate(self.fields):
            element_pos_x = self.element_pos_x
            element_pos_y = self.element_pos_y + (self.spacing * i)
            if len(item) == 4:
                element_pos_x = element_pos_x - 5

            pos = (element_pos_x, element_pos_y)
            ui.add_element(
                item,
                LabeledValue(
                    color=self._black,
                    label=f"{item}:",
                    value="-",
                    position=pos,
                    label_font=fonts.Small,
                    text_font=fonts.Small,
                    label_spacing=label_spacing,
                ),
            )
        logging.info(f"[gpsdeasy] done setting up UI elements: {self.fields}")
        self.ui_setup = True

    def on_unload(self, ui):
        logging.info("[gpsdeasy] bettercap gps reporting disabled")
        try:
            self.agent.run("gps off")
        except Exception:
            logging.info(f"[gpsdeasy] bettercap gps was already off")

        subprocess.run(["systemctl", "stop","gpsd.service"])
        
        with ui._lock:
            for element in self.fields:
                try:
                    ui.remove_element(element)
                except:
                    logging.warning("[gpsdeasy] Element would not be removed skipping")
                    pass
                
        logging.info("[gpsdeasy] plugin disabled")

    def on_ui_update(self, ui):
        if self.ui_setup is False:
            return
        
        coords = self.gpsd.get_current('tpv')
        if coords is None:
            return
        
        for item in self.fields:
            # create depending on fields option
            
            if item == 'fix':
                try:
                    if coords['mode'] == 0:
                        ui.set("fix", f"-")
                    elif coords['mode'] == 1:
                        ui.set("fix", f"0D")
                    elif coords['mode'] == 2:
                        ui.set("fix", f"2D")
                    elif coords['mode'] == 3:
                        ui.set("fix", f"3D")
                    else:
                        ui.set("fix", f"err")
                except: ui.set("fix", f"err")

            elif item == 'lat':
                try:
                    if coords['mode'] == 0:
                        ui.set("lat", f"{0:.4f} ")
                    elif coords['mode'] == 1:
                        ui.set("lat", f"{0:.4f} ")
                    elif coords['mode'] == 2:
                        ui.set("lat", f"{coords['lat']:.4f} ")
                    elif coords['mode'] == 3:
                        ui.set("lat", f"{coords['lat']:.4f} ")
                    else:
                        ui.set("lat", f"err")
                except: ui.set("lat", f"err")

            elif item == 'lon':
                try:
                    if coords['mode'] == 0:
                        ui.set("lon", f"{0:.4f} ")
                    elif coords['mode'] == 1:
                        ui.set("lon", f"{0:.4f} ")
                    elif coords['mode'] == 2:
                        ui.set("lon", f"{coords['lon']:.4f} ")
                    elif coords['mode'] == 3:
                        ui.set("lon", f"{coords['lon']:.4f} ")
                    else:
                        ui.set("lon", f"err")
                except: ui.set("lon", f"err")

            elif item == 'alt':
                try: 
                    if 'speed' in coords:
                        if self.distanceUnit == 'ft':
                            coords['altMSL'] == coords['altMSL'] * 3.281

                        if coords['mode'] == 0:
                            ui.set("alt", f"{0:.1f}{self.distanceUnit}")
                        elif coords['mode'] == 1:
                            ui.set("alt", f"{0:.1f}{self.distanceUnit}")
                        elif coords['mode'] == 2:
                            ui.set("alt", f"{0:.2f}{self.distanceUnit}")
                        elif coords['mode'] == 3:
                            ui.set("alt", f"{coords['altMSL']:.1f}{self.distanceUnit}")
                        else:
                            ui.set("alt", f"err")
                    else:
                        ui.set("alt", f"{0:.1f}{self.distanceUnit}")
                except: ui.set("alt", f"err")
        
            elif item == 'spd':
                try:
                    if 'speed' in coords:
                        if self.speedUnit == 'kph':
                            coords['speed'] == coords['speed'] * 3.6
                        elif self.speedUnit == 'mph':
                            coords['speed'] == coords['speed'] * 2.237
                        else:
                            coords['speed']
                        
                    else:
                        coords['speed'] = 0
                    
                    if self.speedUnit == 'kph':
                        displayUnit = 'km/h'
                    elif self.speedUnit == 'mph':
                        displayUnit = 'mi/h'
                    elif self.speedUnit == 'ms':
                        displayUnit = 'm/s'
                    else:
                        coords['mode'] = -1  # err mode

                    if coords['mode'] == 0:
                        ui.set("spd", f"{0:.2f}{displayUnit}")
                    elif coords['mode'] == 1:
                        ui.set("spd", f"{0:.2f}{displayUnit}")
                    elif coords['mode'] == 2:
                        ui.set("spd", f"{coords['speed']:.2f}{displayUnit}")
                    elif coords['mode'] == 3:
                        ui.set("spd", f"{coords['speed']:.2f}{displayUnit}")
                    else:
                        ui.set("spd", f"err")

                except:
                    ui.set("spd", f"err")
                    
            else:
                if item:
                    # custom item add unit after f}
                    try:
                        if coords[item] == 0:
                            ui.set(item, f"{0:.1f}")
                        elif coords[item] == 1:
                            ui.set(item, f"{coords[item]:.2f}")
                        elif coords[item] == 2:
                            ui.set(item, f"{coords[item]:.2f}")
                        elif coords[item] == 3:
                            ui.set(item, f"{coords[item]:.2f}")
                        else:
                            ui.set(item, f"err")
                    except: ui.set(item, f"err")

    def generatePolarPlot(self,data):
        try:
            rc('grid', color='#316931', linewidth=1, linestyle='-')
            rc('xtick', labelsize=15)
            rc('ytick', labelsize=15)

            # force square figure and square axes looks better for polar, IMO
            width, height = rcParams['figure.figsize']
            size = min(width, height)
            # make a square figure
            fig = figure(figsize=(size, size))

            ax = fig.add_axes([0.1, 0.1, 0.8, 0.8], polar=True, facecolor='#d5de9c')
            ax.set_theta_zero_location('N')
            ax.set_theta_direction(-1)

            if 'satellites'in data:
                for sat in data['satellites']:
                    fc = 'green'
                    if sat['used']:
                        fc = 'blue'
                    ax.annotate(str(sat['PRN']),
                        xy=(radians(sat['az']), 90-sat['el']),  # theta, radius
                        bbox=dict(boxstyle="round", fc = fc, alpha = 0.5),
                        horizontalalignment='center',
                        verticalalignment='center')

            ax.set_yticks(range(0, 90+10, 10))                   # Define the yticks
            yLabel = ['90', '', '', '60', '', '', '30', '', '', '0']
            ax.set_yticklabels(yLabel)
            grid(True)
            
            image = io.BytesIO()
            savefig(image, format='png')
            close(fig)
            return base64.b64encode(image.getvalue()).decode("utf-8")
        except Exception as e: 
            logging.error(e)
            return None
        
    def on_webhook(self, path, request):
        if request.method == "GET":
            # all gets below
            try:
                logging.debug(path)
                if path is None:
                    if self.loaded is False:
                        return "<html><head><title>GPSD Easy: Error</title></head><body><code>%s</code></body></html>" % "Plugin not loaded try again soon"
                    # root get
                    polarImage = self.generatePolarPlot(self.gpsd.get_current("sky"))
                    logging.debug(polarImage)
                    if polarImage is None:
                        return "<html><head><title>GPSD Easy: Error</title></head><body><code>%s</code></body></html>" % "Error forming sat data"

                    html = [
                        '<html><head><title>GPSD Easy: Sky View</title><meta name="csrf_token" content="{{ csrf_token() }}">',
                        '<script>document.getElementById("refreshPolar")?.addEventListener("click", async () => (await fetch(window.location.origin + "/plugins/gpsdeasy/getImage/polar")).ok && (document.getElementById("polarImage").src = "data:image/png;base64," + await (await fetch(window.location.origin + "/plugins/gpsdeasy/getImage/polar")).text()));</script>'
                        '</head><body>',
                        '<h1>Polar Image</h1>',
                        f'<img id="polarImage" src="data:image/png;base64, {polarImage}"/>', 
                        '<button id="refreshPolar">Refresh</button>',
                        '</body></html>']
                    return render_template_string(''.join(html))
                
                elif path == 'getImage/polar':
                    return self.generatePolarPlot(self.gpsd.get_current("sky"))
                
            except Exception as e:
                logging.warning("webhook err: %s" % repr(e))
                return "<html><head><title>GPSD Easy: Error</title></head><body><code>%s</code></body></html>" % repr(e)
