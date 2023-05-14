import os
import logging
import threading
import requests
import json

from pwnagotchi.utils import StatusFile
from pwnagotchi import plugins
from json.decoder import JSONDecodeError


class dropbox(plugins.Plugin):
	__author__ = 'menglish99@gmail.com'
	__version__ = '0.0.1'
	__license__ = 'GPL3'
	__description__ = 'This plugin automatically uploads handshakes to a dropbox app'

	def __init__(self):
		self.ready = False
		self.lock = threading.Lock()
		try:
			self.report = StatusFile('/root/.dropbox_ul_uploads', data_format='json')
		except JSONDecodeError as json_err:
			os.remove("/root/.dropbox_ul_uploads")
			self.report = StatusFile('/root/.dropbox_ul_uploads', data_format='json')

		self.options = dict()
		self.skip = list()

	def _upload_to_dropbox(self, path, timeout=30):
		"""
		Uploads the file to dropbox
		"""		
		head, tail = os.path.split(path)
		destFile = self.options['path'] + '/' + tail
		dbOpts = {'path': destFile, 'mode': 'add','autorename': True,'mute': False,'strict_conflict': False}
		
		headers = {
			'Authorization': 'Bearer ' + self.options['app_token'],
			'Dropbox-API-Arg': json.dumps(dbOpts),
			'Content-Type': 'application/octet-stream',
		}
		data = open(path, 'rb').read()	
					
		try:
			response = requests.post('https://content.dropboxapi.com/2/files/upload', headers=headers, data=data)                
			logging.error(response)		
		except requests.exceptions.RequestException as e:
			logging.error(f"OHC: Got an exception while uploading {path} -> {e}")
			raise e


	def on_loaded(self):
		"""
		Gets called when the plugin gets loaded
		"""
		if 'app_token' not in self.options or ('app_token' in self.options and self.options['app_token'] is None):
			logging.error("dropbox_ul: APP-TOKEN isn't set.")
			return
		logging.info(" [dropbox_ul] plugin loaded")
		self.ready = True

	def on_internet_available(self, agent):
		"""
		Called in manual mode when there's internet connectivity
		"""
		with self.lock:
			if self.ready:
				config = agent.config()
				display = agent.view()
				reported = self.report.data_field_or('reported', default=list())

				handshake_dir = config['bettercap']['handshakes']
				handshake_filenames = os.listdir(handshake_dir)
				handshake_paths = [os.path.join(handshake_dir, filename) for filename in handshake_filenames if
								   filename.endswith('.pcap')]
				handshake_new = set(handshake_paths) - set(reported) - set(self.skip)

				if handshake_new:
					logging.info("dropbox_ul: Internet connectivity detected. Uploading new handshakes")

					for idx, handshake in enumerate(handshake_new):
						display.set('status', f"Uploading handshake to dropbox ({idx + 1}/{len(handshake_new)})")
						display.update(force=True)
						try:
							self._upload_to_dropbox(handshake)
							reported.append(handshake)
							self.report.update(data={'reported': reported})
							logging.info("dropbox_ul: Successfully uploaded %s", handshake)
						except requests.exceptions.RequestException as req_e:
							self.skip.append(handshake)
							logging.error("dropbox_ul: %s", req_e)
							continue
						except OSError as os_e:
							logging.error("dropbox_ul: %s", os_e)
							continue


