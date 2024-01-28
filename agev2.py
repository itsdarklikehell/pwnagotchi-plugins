import os
import json
import logging
from datetime import datetime

import pwnagotchi
import pwnagotchi.plugins as plugins
import pwnagotchi.ui.faces as faces
import pwnagotchi.ui.fonts as fonts
from pwnagotchi.ui.components import LabeledValue
from pwnagotchi.ui.view import BLACK


class Age(plugins.Plugin):
    __author__ = 'Kaska'
    __version__ = '1.1.0'
    __license__ = 'MIT'
    __description__ = 'A plugin that will add age and strength stats based on epochs and trained epochs'

    def __init__(self):
        self.epochs = 0
        self.train_epochs = 0
        self.access_points_seen = 0
        self.deauths_sent = 0
        self.device_start_time = datetime.now()

    def on_loaded(self):
        data_path = '/root/brain.json'
        self.load_data(data_path)

    def on_ui_setup(self, ui):
        ui.add_element('Age', LabeledValue(color=BLACK, label='♥ Age', value='',
                                           position=(int(self.options["age_x_coord"]),
                                                     int(self.options["age_y_coord"])),
                                           label_font=fonts.Bold, text_font=fonts.Medium))
        ui.add_element('Strength', LabeledValue(color=BLACK, label='Str', value=0,
                                                position=(int(self.options["str_x_coord"]),
                                                          int(self.options["str_y_coord"])),
                                                label_font=fonts.Bold, text_font=fonts.Medium))
        ui.add_element('Access Points', LabeledValue(color=BLACK, label='APs', value=0,
                                                     position=(int(self.options["ap_x_coord"]),
                                                               int(self.options["ap_y_coord"])),
                                                     label_font=fonts.Bold, text_font=fonts.Medium))
        ui.add_element('Deauths Sent', LabeledValue(color=BLACK, label='Deauths', value=0,
                                                    position=(int(self.options["deauth_x_coord"]),
                                                              int(self.options["deauth_y_coord"])),
                                                    label_font=fonts.Bold, text_font=fonts.Medium))

    def on_unload(self, ui):
        with ui._lock:
            ui.remove_element('Age')
            ui.remove_element('Strength')
            ui.remove_element('Access Points')
            ui.remove_element('Deauths Sent')

    def on_ui_update(self, ui):
        ui.set('Age', self.calculate_device_age())
        ui.set('Strength', str(self.train_epochs))
        ui.set('Access Points', str(self.access_points_seen))
        ui.set('Deauths Sent', str(self.deauths_sent))

    def on_ai_training_step(self, agent, _locals, _globals):
        self.train_epochs += 1
        self.access_points_seen += len(agent.view().access_points())
        self.deauths_sent += agent.stats('deauth')
        if self.train_epochs % 100 == 0:
            self.strength_checkpoint(agent)

    def on_epoch(self, agent, epoch, epoch_data):
        self.epochs += 1
        if self.epochs % 100 == 0:
            self.age_checkpoint(agent)

    def abrev_number(self, num):
        if num < 100000:
            return str(num)
        else:
            magnitude = 0
            while abs(num) >= 1000:
                magnitude += 1
                num /= 1000.0
                abbr = ['', 'K', 'M', 'B', 'T', 'P'][magnitude]
            return '{}{}'.format('{:.2f}'.format(num).rstrip('0').rstrip('.'), abbr)

    def age_checkpoint(self, agent):
        view = agent.view()
        view.set('face', faces.HAPPY)
        view.set('status', "Wow, I've lived for " + self.calculate_device_age())
        view.update(force=True)

    def strength_checkpoint(self, agent):
        view = agent.view()
        view.set('face', faces.MOTIVATED)
        view.set('status', "Look at my strength go up! \n"
                           "I've trained for " + str(self.train_epochs) + " epochs")
        view.update(force=True)

    def load_data(self, data_path):
        if os.path.exists(data_path):
            with open(data_path) as f:
                data = json.load(f)
                self.epochs = data['epochs_lived']
                self.train_epochs = data['epochs_trained']

    def calculate_device_age(self):
        current_time = datetime.now()
        age_delta = current_time - self.device_start_time

        years = age_delta.days // 365
        remaining_days = age_delta.days % 365
        months = remaining_days // 30
        days = remaining_days % 30

        age_str = f'{years}y {months}m {days}d'
        return age_str


# Instantiate the plugin
age_plugin = Age()

# Example usage (replace this with the actual Pwnagotchi usage)
# For example, calling on_ai_training_step and on_ui_update methods
# age_plugin.on_ai_training_step(your_agent, your_locals, your_globals)
# age_plugin.on_ui_update(your_ui)
