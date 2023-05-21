import pwnagotchi.plugins as plugins
import pwnagotchi
import logging
import subprocess
import time

class ext_wifi(plugins.Plugin):
    __author__ = 'chris@holycityhosting.com'
    __version__ = '1.0.0'
    __license__ = 'GPL3'
    __description__ = 'Activates external wifi adapter'

    def __init__(self):
        self.ready = 0
        self.status = ''
        self.network = ''

    def on_loaded(self):
        for opt in ['mode']:
            if opt not in self.options or (opt in self.options and self.options[opt] is None):
                logging.error(f"Set WiFi adapter mode configuration for internal or external.")
                return
        _log("plugin loaded")
        self.ready = 1
        mode = self.options['mode']
        interface = self.options['interface']
        if (mode == "external"):
            subprocess.run('sed -i s/mon0/{interface}/g /usr/bin/bettercap-launcher'.format(interface=interface), shell=True).stdout
            subprocess.run('sed -i s/mon0/{interface}/g /usr/local/share/bettercap/caplets/pwnagotchi-auto.cap'.format(interface=interface), shell=True).stdout
            subprocess.run('sed -i s/mon0/{interface}/g /usr/local/share/bettercap/caplets/pwnagotchi-manual.cap'.format(interface=interface), shell=True).stdout
            subprocess.run('sed -i s/mon0/{interface}/g /etc/pwnagotchi/config.toml'.format(interface=interface), shell=True).stdout
            subprocess.run('sed -i s/mon0/{interface}/g /usr/bin/pwnlib'.format(interface=interface), shell=True).stdout
            _log("External adapter activated")
        else:
            subprocess.run('sed -i s/{interface}/mon0/g /usr/bin/bettercap-launcher'.format(interface=interface), shell=True).stdout
            subprocess.run('sed -i s/{interface}/mon0/g /usr/local/share/bettercap/caplets/pwnagotchi-auto.cap'.format(interface=interface), shell=True).stdout
            subprocess.run('sed -i s/{interface}/mon0/g /usr/local/share/bettercap/caplets/pwnagotchi-manual.cap'.format(interface=interface), shell=True).stdout
            subprocess.run('sed -i s/{interface}/mon0/g /etc/pwnagotchi/config.toml'.format(interface=interface), shell=True).stdout
            subprocess.run('sed -i s/{interface}/mon0/g /usr/bin/pwnlib'.format(interface=interface), shell=True).stdout
            _log("Internal adapter activated")

def _run(cmd):
    result = subprocess.run(cmd, shell=True, stdin=None, stderr=None, stdout=subprocess.PIPE, executable="/bin/bash")
    return result.stdout.decode('utf-8').strip()

def _log(message):
    logging.info('[ext_wifi] %s' % message)
