import logging
import json
import os
import asyncio
import _thread

import pwnagotchi
import pwnagotchi.utils as utils

import pwnagotchi.plugins as plugins
import pwnagotchi.ui.fonts as fonts
from pwnagotchi.ui.components import LabeledValue
from pwnagotchi.ui.view import BLACK
from pwnagotchi.bettercap import Client

class PrivacyNightmare(plugins.Plugin):
    __author__ = 'glenn@pegden.com.com'
    __version__ = '0.0.1'
    __license__ = 'Private (for now)'
    __description__ = 'Private Nightmare. Eavesdropping metadata for fun and profit (well, education and awareness mostly)'

    def __init__(self):
        self.running = True
        self.second_ws_ready = False
        self.gps_up = False
        self.pn_count = 0
        self.pn_status = "Waiting....."
        self.pn_gps_coords = None

    def on_loaded(self):

        logging.info("privacy nightmare plugin loaded")

        if 'pn_output_path' not in self.options or ('pn_output_path' in self.options and self.options['pn_output_path'] is None):
            logging.debug("pn_output_path not set")
            return

        if not os.path.exists(self.options['pn_output_path']):
            os.makedirs(self.options['pn_output_path'])


    def on_ready(self, agent):

        self.hook_ws_events(agent)
        self.enable_gps(agent)

    def on_wifi_update(self, agent, access_points):
         self.aps_update('WU', agent, access_points)

    def on_association(self, agent, access_point):
         self.aps_update('AS', agent, [access_point])

    def on_deauthentication(self, agent, access_point, client_station):
         self.aps_update('DA', agent, [access_point])

    def on_handshake(self, agent, filename, access_point, client_station):
         self.aps_update('HS', agent, [access_point])


    def on_ui_setup(self, ui):
        pos = (1, 76)
        ui.add_element('pn_status', LabeledValue(color=BLACK, label='', value='PN: Active',
                                                   position=pos,
                                                   label_font=fonts.Small, text_font=fonts.Small))

        pos = (122, 94)
        ui.add_element('pn_count', LabeledValue(color=BLACK, label='', value='PN: Active',
                                                   position=pos,
                                                   label_font=fonts.Small, text_font=fonts.Small))



    def on_ui_update(self, ui):
            ui.set('pn_status', "PN: %s" % (self.pn_status))
            ui.set('pn_count', "PN: %s/%s" % (self.pn_count, self.pn_count))

    async def on_event(self, msg):

         jmsg = json.loads(msg)
         logging.info("PN: Event %s" % (jmsg['tag']))
         if jmsg['tag'] == "wifi.client.probe":

                self.pn_status = "Probe from %s" % jmsg['data']['essid']
                logging.info("PN: !!! Probe !!! %s" % (jmsg))

         if jmsg['tag'] == "wifi.ap.new":
             self.pn_status = "New AP %s" % jmsg['data']['essid']
             logging.info("PN: !!! NEW AP !!! %s" % (jmsg))
             self.aps_update('NE', None, jmsg['data'])



    def hook_ws_events(self,agent):
        # OK aading a second websocket listener is an ugly approach, but without modifying the core code, I cant think of a better way that starting my own thread with my own websock listener

        self.agent = agent
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        _thread.start_new_thread(self._event_poller, (asyncio.get_event_loop(),))


    def _event_poller(self, loop):

        while True:
            logging.info("Probe listener up!")
            self.pn_status = "Probe listner up!"
            try:
                loop.create_task(self.agent.start_websocket(self.on_event))
                loop.run_forever()
            except Exception as ex:
                logging.debug("Error while polling via websocket (%s)", ex)


    def enable_gps(self,agent):

        # TODO: Can I call the gps module direct? Would using gpsd be a better idea?
        if 'gps_device' in self.options:
            if os.path.exists(self.options["gps_device"]):
                logging.info(
                    f"enabling bettercap's gps module for {self.options['gps_device']}"
                )
                try:
                    agent.run("gps off")
                except Exception:
                    pass

                agent.run(f"set gps.device {self.options['gps_device']}")
                agent.run(f"set gps.baudrate {self.options['gps_speed']}")
                agent.run("gps on")
                self.gps_up = True
            else:
                logging.warning("PN: no GPS detected")
        else:
                logging.warning('PN: no GPS configured')



    def get_gps(self,agent):
        if self.gps_up:
            self.pn_gps_coords = agent["gps"]

            if self.pn_gps_coords and all([
               self.pn_gps_coords["Latitude"], self.pn_gps_coords["Longitude"]
            ]):
                logging.info("PN: GPS %s %s" % (self.pn_gps_coords["Latitude"], self.pn_gps_coords["Longitude"]))
                self.gps_hot = True
            else:
                logging.info("Unknown location")
                self.gps_hot = False
        else:
            logging.info("Unknown location (gps not up).")
            self.gps_hot = False

    def aps_update(self, update_type, agent, access_points):

        if self.running:

            #If we were called from the agent, update the gps, if not we'll have to make do with the last known ones
            if agent != None:
                self.get_gps(agent.session())

            if self.gps_hot ==  True:
               update_type = "%s <G>" % update_type
               latlong = "[%s][%s]" % (self.pn_gps_coords['Latitude'],self.pn_gps_coords['Longitude'])

            if not hasattr(self,'ap_list'):
                self.ap_list = {}

            if len(access_points) > 0:

              for ap in access_points:
                  if 'hostname' in ap:
                      hostname = ap['hostname']
                  else:
                      logging.info("PN: AP (Debug - %s): %s" % (update_type, str(ap)))
                      hostname = "Unknown-%s" % ap['vendor']

                  APUID = "%s%%%s" % (hostname,ap['mac'])
                  if APUID in self.ap_list:
                     logging.info("PN: We already know about %s, so ignoring" % APUID)
                     #TODO: Look at merging metadata here 
                  else:
                      logging.info("PN: NEW AP/mac combo %s" % APUID)
                      logging.info("PN: AP (%s): %s at %s" % (update_type, hostname, latlong))
                      self.ap_list[APUID] = str(ap)
                      self.pn_status = ("AP (%s): %s" % (update_type , hostname))
                      self.pn_count += 1
                      pn_filename = "%s/pn_ap_%s.json" % (self.options['pn_output_path'],hostname)
                      logging.info(f"saving GPS to {pn_filename} ({hostname} at {latlong})")
                      with open(pn_filename, "w+t") as fp:
                        json.dump(ap, fp)
                        json.dump(self.pn_gps_coords, fp)
            else:
                  logging.warning("PN: Empty AP list from %s list is %s" % (update_type , access_points))

    def clients_update(self, access_points):
       pass

