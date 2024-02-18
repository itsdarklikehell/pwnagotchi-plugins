import logging
import io
import subprocess
import os
import json
import pwnagotchi
import pwnagotchi.plugins as plugins
from pwnagotchi.ui.components import LabeledValue
from pwnagotchi.ui.view import BLACK
import pwnagotchi.ui.fonts as fonts
from flask import jsonify
from flask import abort
from flask import Response

class pwnwatch(plugins.Plugin):
    __author__ = 'Artur Oliveira'
    __version__ = '1.0.0'
    __license__ = 'GPL3'
    __description__ = '''
    This plugin allows the pwnagotchi to receive
    commands from the pwnagotchi-watch and respond
    them properly.

    parseSessionStats and parseSessionStatsFile borrowed from:
    https://github.com/GaelicThunder/Experience-Plugin-Pwnagotchi/blob/f456040de4951de1e6ab3fcb4453d42a7da362d1/exp.py#L215

                        '''
    
    def __init__(self):
        logging.info("[PWNWATCH] plugin loaded")

    # called when everything is ready and the main loop is about to start
    def on_config_changed(self, config):
        # (note) I've just kept this here for reference
        #handshake_dir = config['bettercap']['handshakes']
        pass

    def parseSessionStats(self):
        dir = pwnagotchi.config['main']['plugins']['session-stats']['save_directory']
        for filename in os.listdir(dir):
            logging.debug("[PWNWATCH] Parsing " + filename + "...")
            if filename.endswith(".json") & filename.startswith("stats"):
                try:
                    self.parseSessionStatsFile(os.path.join(dir,filename))
                except:
                    logging.error("[PWNWATCH] ERROR parsing File: "+ filename)
    
    def parseSessionStatsFile(self, path):
        deauths = 0
        handshakes = 0
        associations = 0
        with open(path) as json_file:
            data = json.load(json_file)
            for entry in data["data"]:
                deauths += data["data"][entry]["num_deauths"]
                handshakes += data["data"][entry]["num_handshakes"]
                associations += data["data"][entry]["num_associations"]
            

        self.deauths = deauths
        self.handshakes = handshakes
        self.associations = associations


    def on_webhook(self, path, request):
        if not self.ready:
            return "Plugin not ready"

        if not path or path == "/":
            self.parseSessionStats()
            #(last_session.handshakes, utils.total_unique_handshakes(self._config['bettercap']['handshakes']))
            Response(str(self.handshakes), mimetype='text/plain')

        if path == 'stream':
            # Just for reference
            # def generate():
            #     with open(self.config['main']['log']['path']) as f:
            #         yield ''.join(f.readlines()[-self.options.get('max-lines', 4096):])
            #         while True:
            #             yield f.readline()

            # return Response(generate(), mimetype='text/plain')
            pass

        abort(404)
