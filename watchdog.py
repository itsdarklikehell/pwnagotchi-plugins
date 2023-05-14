import os
import logging
import re
import subprocess
from io import TextIOWrapper
from pwnagotchi import plugins
from pwnagotchi.utils import StatusFile


class Watchdog(plugins.Plugin):
    __author__ = '33197631+dadav@users.noreply.github.com'
    __version__ = '1.0.0'
    __license__ = 'GPL3'
    __description__ = 'Restart pwnagotchi when blindbug is detected.'
    __defaults__ = {
        'enabled': False,
    }

    def __init__(self):
        self.options = dict()
        self.pattern = re.compile(r'brcmf_cfg80211_nexmon_set_channel.*?Set Channel failed')
        self.status = StatusFile('/root/.pwnagotchi-watchdog')
        self.status.update()

    def on_loaded(self):
        """
        Gets called when the plugin gets loaded
        """
        logging.info("Watchdog plugin loaded.")

    def on_epoch(self, agent, epoch, epoch_data):
        if self.status.newer_then_minutes(5):
            return

        data_keys = ['num_deauths', 'num_associations', 'num_handshakes']
        has_interactions = any([epoch_data[x]
                                for x in data_keys
                                if x in epoch_data])

        if has_interactions:
            return

        epoch_duration = epoch_data['duration_secs']

        # get last 10 lines
        last_lines = ''.join(list(TextIOWrapper(subprocess.Popen(['journalctl','-n10','-k', '--since', f"{epoch_duration} seconds ago"],
                                                stdout=subprocess.PIPE).stdout))[-10:])

        if len(self.pattern.findall(last_lines)) >= 5:
            display = agent.view()
            display.set('status', 'Blind-Bug detected. Restarting.')
            display.update(force=True)
            logging.info('[WATCHDOG] Blind-Bug detected. Restarting.')
            mode = 'MANU' if agent.mode == 'manual' else 'AUTO'
            import pwnagotchi
            pwnagotchi.reboot(mode=mode)
