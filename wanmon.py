import logging
import json
import os

# import pwnagotchi.plugins as plugins
from pwnagotchi.ui.components import LabeledValue
from pwnagotchi.ui.view import BLACK
import pwnagotchi.ui.fonts as fonts

# For Dev
from pwnagotchi import pwnagotchi
import pwnagotchi.plugins as plugins

class WanMon(plugins.Plugin):
    __author__ = 'me@CyberGladius.com'
    __version__ = '0.0.1'
    __license__ = 'GPL3'
    __description__ = 'This Pwnagotchi plugin will check the Internet connection and display the status of the Internet connection on the Pwnagotchi\'s display.'

    def __init__(self):
        self.running = False
        self.internet_available = False
        self.dns_resolving = False
        self.internet_status = 0

    def on_loaded(self):
        if not os.path.exists('/bin/ping'):
            logging.error('Cannot access the ping command')
            self.running = False
            return
        self.running = True

    def on_ui_setup(self, ui):
        # Set the X,Y position of the icon on the Pwnagotchi's display. First check if the user has set the 'pos_x' and 'pos_y' options in the config.toml file.
        # If not, use the default guess values.
        pos_x = int(ui.width() / 2 - 23)
        pos_y = int(0)

        if self.options['position_x'] is not None:
            pos_x = int(self.options['position_x'])

        if self.options['position_y'] is not None:
            pos_y = int(self.options['position_y'])

        ui.add_element(
            'iIcon',
            LabeledValue(color=BLACK, label='WAN:', value='X', position=(pos_x, pos_y), label_font=fonts.Bold, text_font=fonts.Medium)
        )

    def on_unload(self, ui):
        with ui._lock:
            ui.remove_element('iIcon')

    def on_ui_update(self, ui):
        # If the internet_status equals, 2 == 'C', 1 == 'IP', 0 == 'X', then add the internet_status to the Pwnagotchi's display.
        if self.internet_status == 2:
            ui.set('iIcon', 'C')
        if self.internet_status == 1:
            ui.set('iIcon', 'IP')
        if self.internet_status == 0:
            ui.set('iIcon', 'X')

    # Test if the system can reach the Internet.
    def test_internet_connection(self):
        if self.running:
            # if self.options['testip'] is set to a valid IP address, use that instead of the default(8.8.8.8).
            # Use the test IP to test if the Internet is available using the ping command.
            test_ip = '8.8.8.8'

            if self.options['testip'] is not None:
                test_ip = self.options['testip']

            test_ip_cmd = 'ping -c 1 -W 1 %s' % test_ip
            logging.debug('[WanMon] running %s' % test_ip_cmd)
            test_ip_cmd_output = os.system(test_ip_cmd)

            if test_ip_cmd_output == 0:
                logging.debug('[WanMon] Internet is available')
                self.internet_available = True

            # if self.options['testdns'] is set to a valid domain name, use that instead of the default(google.com).
            # Use the test domain anme to test if DNS is reslving over the Internet, using the ping command.
            test_dns = 'google.com'

            if self.options['testdns'] is not None:
                test_dns = self.options['testdns']

            test_dns_cmd = 'ping -c 1 -W 1 %s' % test_dns
            logging.debug('[WanMon] running %s' % test_dns_cmd)
            test_dns_cmd_output = os.system(test_dns_cmd)

            if test_dns_cmd_output == 0:
                logging.debug('[WanMon] DNS is resolving over the Internet')
                self.dns_resolving = True

            # If self.internet_available and self.dns_resolving are both True, report global internet_status as 2.
            if self.internet_available and self.dns_resolving:
                return 2
            # if self.internet_available is True and self.dns_resolving is False, report global internet_status as 1.
            if self.internet_available and not self.dns_resolving:
                return 1
            # if self.internet_available and self.dns_resolving are both False, report global internet_status as 0.
            if not self.internet_available and not self.dns_resolving:
                return 0

    # Check for Internet connection on startup.
    def on_ready(self, agent):
        self.internet_status = self.test_internet_connection()

    # Check for Internet connection after each epoch. This was the only function that run periodically but not every second; trying to avoid overloading the system.
    def on_epoch(self, agent, epoch, epoch_data):
        self.internet_status = self.test_internet_connection()
