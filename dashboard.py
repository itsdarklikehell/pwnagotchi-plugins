import datetime
import logging
import os
import pwnagotchi
import pwnagotchi.plugins as plugins
import pwnagotchi.ui.fonts as fonts

from pwnagotchi.ui.components import LabeledValue
from pwnagotchi.ui.view import BLACK
from threading import Thread
from subprocess import run, PIPE, DEVNULL
from time import sleep


class Dashboard(plugins.Plugin):
    __author__ = 'doki'
    __version__ = '1.0.0'
    __license__ = 'GPL3'
    __description__ = 'Dashboard plugin is a consolidation of the clock, deauth counter, memtemp, pivoyager and added few features such as cracked handshake counter and internet status.'

    # Initiate deauthcounter plugin
    def __init__(self):
        self.deauth_counter = 0
        self.handshake_counter = 0

    # Get the current status of the pivoyager
    def get_status(self):
        status = run([self.path, "status"], stdout=PIPE).stdout.decode().split("\n")
        stat_dict = {
                "stat": status[0].split(" ")[1:],
                "bat":  status[1].split(" ")[1],
                "vbat": status[2].split(" ")[1],
                "vref": status[3].split(" ")[1]
                }
        return stat_dict

    # Pivoyager: Thread for shutting down on low battery voltage or a button press
    def check_status(self):
        while True:
            status = self.get_status()
            if(not "pg" in status["stat"]  and "low battery" in status["bat"]):
                logging.warn("[Dashboard]: Pivoyager battery low! Shutting down...")
                break
            elif("button" in status["stat"]):
                logging.warn("[Dashboard]: Pivoyager button is pressed! Shutting down...")
                run([self.path, "clear", "button"])
                break
            sleep(self.refresh_time)
        # enable watchdog timer
        run([self.path, "watchdog", "30"])
        logging.warn("[Dashboard]: Shutdown Initiated... Enabling pivoyager watchdog timer.")
        pwnagotchi.shutdown()

    def on_loaded(self):
        # Initiate clock plugin
        if 'date_format' in self.options:
            self.date_format = self.options['date_format']
        else:
            self.date_format = "%m/%d/%y"
        logging.debug("[Dashboard]: Clock plugin loaded.")

        # Initialise pivoyager options
        self.path = self.options['path'] if 'path' in self.options else '/usr/local/bin/pivoyager'
        self.refresh_time = self.options['refresh_time'] if 'refresh_time' in self.options else 3

        self.status_thread = Thread(target=self.check_status, name="StatusThread")
        self.status_thread.start()

        status = self.get_status()
        if("inits" in status["stat"]):
            date = run([self.path, "date"], stdout=PIPE).stdout.decode()
            run(["date", "-s", date], stdout=DEVNULL)
            logging.debug("[Dashboard]: Pivoyager update local time from RTC.")
        else:
            logging.warning("[Dashboard]: Pivoyager RTC not set, could not sync local time.")

       # enable pivoyager power wakeup
        run([self.path, "enable", "power-wakeup"])
        logging.debug("[Dashboard]: Enable pivoyager power-wakeup function.")
        logging.debug("[Dashboard]: Pivoyager plugin loaded.")

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
          ui.add_element('pivoyager', LabeledValue(color=BLACK, label=' ', value='ups',
                                                   position=(int(self.options["bat_x_pos"]),
                                                             int(self.options["bat_y_pos"])),
                                                   label_font=fonts.Bold, text_font=fonts.Bold))
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
          ui.add_element('connection_status', LabeledValue(color=BLACK, label=' ', value='',
                                                 position=(int(self.options["netstat_x_pos"]),
                                                           int(self.options["netstat_y_pos"])),
                                                 label_font=fonts.Small, text_font=fonts.Small))

    def on_internet_available(self, agent):
        # pivoyager: Update RTC if local time is ntp-synced and if RTC is not initialised
        if(not "inits" in self.get_status()["stat"]):
            # Update RTC if local time is ntp-synced and RTC is not initialised
            run([self.path, "date", "sync"])
            logging.debug("[Dashboard]: Pivoyager update RTC from NTP")

    def on_unload(self, ui):
        with ui._lock:
            ui.remove_element('clock')
            ui.remove_element('ram')
            ui.remove_element('cpu')
            ui.remove_element('tmp')
            ui.remove_element('pivoyager')
            ui.remove_element('deauth')
            ui.remove_element('hand')
            ui.remove_element('cracked')
            ui.remove_element('connection_status')

    def on_ui_update(self, ui):
        now = datetime.datetime.now()
        time_rn = now.strftime(self.date_format + " %I:%M%p")
        status = self.get_status()
        total_cracked = 'uniq -i /root/handshakes/wpa-sec.cracked.potfile | wc -l'
        charge_mapping = {
                "charging": "▲",
                "discharging": "▼",
                "charge": "■",
                "fault": "×"
                }

        ui.set('clock', time_rn)
        ui.set('cracked', '%s' % (os.popen(total_cracked).read().rstrip()))
        ui.set('ram', str(self.mem_usage()) + "%")
        ui.set('cpu', str(self.cpu_load()) + "%")
        ui.set('tmp', str(self.cpu_temp()) + "°C")
        ui.set('deauth', str(self.deauth_counter))
        ui.set('hand', str(self.handshake_counter))
        ui.set('pivoyager', "{sbat}{voltage}".format(sbat=charge_mapping[status["bat"]], voltage=status["vbat"]))

        # check if there is an active Internet connection
        output = os.system('ping -c 1 ' + '8.8.8.8')
        if output == 0:
          ui.set('connection_status', 'online')
        else:
          ui.set('connection_status', 'offline')

    # called when the agent is deauthenticating a client station from an AP
    def on_deauthentication(self, agent, access_point, client_station):
        self.deauth_counter += 1

    def on_handshake(self, agent, filename, access_point, client_station):
        self.handshake_counter += 1
