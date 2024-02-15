import os
import json
import logging

import pwnagotchi
import pwnagotchi.plugins as plugins
import pwnagotchi.ui.faces as faces
import pwnagotchi.ui.fonts as fonts
from pwnagotchi.ui.components import LabeledValue
from pwnagotchi.ui.view import BLACK

# only used to grab timestamps
from datetime import datetime   

# grab the t0 timestamp at module initialization
tzero=datetime.now()
start_time = tzero.strftime("%H:%M:%S")

class printp(plugins.Plugin):
    __author__ = 'Code taken from HannaDiamond Pwnagotchi Age script'
    __version__ = '1.0.0'
    __license__ = 'GPLv3'
    __description__ = 'Example plugin that simply prints to Pwnagotchi screen via labels and to the view area'

 # don't need this but keeping for reference
 #   def __init__(self):
 #       self.epochs = 0
 #       self.train_epochs = 0

       
    # Print the Labels on_ui_setup
    def on_ui_setup(self, ui):
        ui.add_element('t0', LabeledValue(color=BLACK, label='T0 ', value=0,
                                           position=(int(self.options["t0_x_coord"]),
                                                     int(self.options["t0_y_coord"])),
                                           label_font=fonts.Bold, text_font=fonts.Small))
        ui.add_element('tn', LabeledValue(color=BLACK, label='Tn ', value=0,
                                                position=(int(self.options["tn_x_coord"]),
                                                          int(self.options["tn_y_coord"])),
                                                label_font=fonts.Bold, text_font=fonts.Small))
        
    # Cleanup the labels on_unload    
    def on_unload(self, ui):
        with ui._lock:
            ui.remove_element('t0')
            ui.remove_element('tn')

    # Print to the labels on_ui_update refresh
    def on_ui_update(self, ui):
        
        # reprint the static t0 timestamp
        ui.set('t0', str(start_time) )
        
        # grab the current timestamp
        now = datetime.now()
        current_time = now.strftime("%H:%M:%S")
        
        # print the new tn timestamp
        ui.set('tn', str(current_time) )
        

    # Print to the View area of the Pwnagotchi
    def on_epoch(self, agent, epoch, epoch_data):
        view = agent.view()
        
        # Optional if you want to change the face
        view.set('face', faces.HAPPY)   
        
        view.set('status', "Say a bunch of stuff here...blah blah")
        view.update(force=True)


