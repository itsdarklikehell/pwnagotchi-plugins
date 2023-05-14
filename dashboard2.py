import datetime
import logging
import os
import pwnagotchi
import pwnagotchi.plugins as plugins
import pwnagotchi.ui.fonts as fonts

from pwnagotchi.ui.components import LabeledValue
from pwnagotchi.ui.view import BLACK

class Dashboard(plugins.Plugin):
    __author__ = 'doki'
    __version__ = '1.0.0'
    __license__ = 'GPL3'
    __description__ = 'Dashboard plugin is a consolidation of the clock, deauth counter, memtemp, pivoyager and added few features such as cracked handshake counter and internet status.'

    # Initiate deauthcounter plugin
    def __init__(self):
        self.deauth_counter = 0
        self.handshake_counter = 0

    def on_loaded(self):
        # Initiate clock plugin
        if 'date_format' in self.options:
            self.date_format = self.options['date_format']
        else:
            self.date_format = "%m/%d/%y"
        logging.debug("[Dashboard]: Clock plugin loaded.")
        logging.info("[Dashboard]: plugin loaded.")

    def mem_usage(self):
        return int(pwnagotchi.mem_usage() * 100)

    def cpu_load(self):
        return int(pwnagotchi.cpu_load() * 100)

    def cpu_temp(self):
        return int(pwnagotchi.temperature())

    def on_ui_setup(self, ui):
          ui.add_element('clock', LabeledValue(color=BLACK, label='', value='-/-/--:--',
                                               position=(int(self.options["clock_x_pos"]),
                                                         int(self.options["clock_y_pos"])),
                                               label_font=fonts.Small, text_font=fonts.Small))
          ui.add_element('ram', LabeledValue(color=BLACK, label='', value='mem',
                                             position=(int(self.options["mem_x_pos"]),
                                                       int(self.options["mem_y_pos"])),
                                             label_font=fonts.Small, text_font=fonts.Bold))
          ui.add_element('cpu', LabeledValue(color=BLACK, label='', value='cpu',
                                             position=(int(self.options["cpu_x_pos"]),
                                                        int(self.options["cpu_y_pos"])),
                                             label_font=fonts.Small, text_font=fonts.Bold))
          ui.add_element('tmp', LabeledValue(color=BLACK, label='', value='tmp',
                                             position=(int(self.options["tmp_x_pos"]),
                                                       int(self.options["tmp_y_pos"])),
                                             label_font=fonts.Small, text_font=fonts.Bold))
          ui.add_element('deauth', LabeledValue(color=BLACK, label='', value=str(self.deauth_counter),
                                                position=(int(self.options["deauth_x_pos"]),
                                                          int(self.options["deauth_y_pos"])),
                                                label_font=fonts.Bold, text_font=fonts.Bold))
          ui.add_element('hand', LabeledValue(color=BLACK, label='', value=str(self.handshake_counter),
                                              position=(int(self.options["hand_x_pos"]),
                                                        int(self.options["hand_y_pos"])),
                                              label_font=fonts.Bold, text_font=fonts.Bold))
          ui.add_element('cracked', LabeledValue(color=BLACK, label='', value='',
                                                 position=(int(self.options["cracked_x_pos"]),
                                                           int(self.options["cracked_y_pos"])),
                                                 label_font=fonts.Bold, text_font=fonts.Bold))
        
    def on_unload(self, ui):
        with ui._lock:
            ui.remove_element('clock')
            ui.remove_element('ram')
            ui.remove_element('cpu')
            ui.remove_element('tmp')
            ui.remove_element('deauth')
            ui.remove_element('hand')
            ui.remove_element('cracked')

    def on_ui_update(self, ui):
        now = datetime.datetime.now()
        time_rn = now.strftime(self.date_format + " %I:%M%p")
        status = self.get_status()
        total_cracked = 'uniq -i /root/handshakes/wpa-sec.cracked.potfile | wc -l'
   
        ui.set('clock', time_rn)
        ui.set('cracked', '%s' % (os.popen(total_cracked).read().rstrip()))
        ui.set('ram', str(self.mem_usage()) + "%")
        ui.set('cpu', str(self.cpu_load()) + "%")
        ui.set('tmp', str(self.cpu_temp()) + "°C")
        ui.set('deauth', str(self.deauth_counter))
        ui.set('hand', str(self.handshake_counter))
            
   # called when the agent is deauthenticating a client station from an AP
    def on_deauthentication(self, agent, access_point, client_station):
        self.deauth_counter += 1

    def on_handshake(self, agent, filename, access_point, client_station):
        self.handshake_counter += 1
