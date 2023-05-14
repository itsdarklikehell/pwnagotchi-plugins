import logging
import pwnagotchi.plugins as plugins
import datetime
import pandas as pd


class Timer(plugins.Plugin):
    __author__ = 'idoloninmachina@gmail.com'
    __version__ = '0.1.0'
    __license__ = 'GPL3'
    __description__ = 'Measure the amount of time taken by the pwnagotchi to capture a handshake'

    def __init__(self):
        self.running = False
        self.data = {
            'Time to deauth': [],
            'Time to handshake': [],
            'Time between deauth and handshake': [],
        }
        self.reset_times()

    def on_epoch(self, agent, epoch, epoch_data):
        self.reset_times()

    def on_loaded(self):
        logging.info("[Timer] plugin loaded")

    def on_unload(self, ui):
        logging.info("[Timer] Plugin unloaded")

    def on_wifi_update(self, agent, access_points):
        time = datetime.datetime.now()
        self.wifi_update_time = time

    def on_deauthentication(self, agent, access_point, client_station):
        time = datetime.datetime.now()
        self.wifi_deauth_time = time

    def on_handshake(self, agent, filename, access_point, client_station):
        time = datetime.datetime.now()
        self.wifi_handshake_time = time

        self.process_data()
        self.reset_times()

    def process_data(self):
        # We have captured a handshake, so we need to check if it was a passive capture
        if self.wifi_deauth_time is None:
            # We haven't deauthed anyone, so this was just a passive capture
            # Not relevant to the data we want
            return

        self.data['Time to deauth'].append(
            self.calculate_difference_in_seconds(
                self.wifi_update_time, self.wifi_deauth_time))
        self.data['Time to handshake'].append(
            self.calculate_difference_in_seconds(
                self.wifi_update_time, self.wifi_handshake_time))
        self.data['Time between deauth and handshake'].append(
            self.calculate_difference_in_seconds(
                self.wifi_deauth_time, self.wifi_handshake_time))

        df = pd.DataFrame(self.data, columns=['Time to deauth',
                                              'Time to handshake',
                                              'Time between deauth and handshake', ])
        logging.info('[Timer] data saved')
        logging.info(df)
        df.to_csv('/home/pi/data/pwnagotchi_times.csv')

    def calculate_difference_in_seconds(self, past, future):
        difference = future - past
        return difference.total_seconds()

    def reset_times(self):
        self.wifi_update_time = None
        self.wifi_deauth_time = None
        self.wifi_handshake_time = None
