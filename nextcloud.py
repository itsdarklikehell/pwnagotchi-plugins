import os
import logging
import threading
import requests
import json

from pwnagotchi.utils import StatusFile
from pwnagotchi import plugins
from json.decoder import JSONDecodeError

class nextcloud(plugins.Plugin):
    __author__ = 'github@disterhoft.de'
    __version__ = '0.0.1'
    __license__ = 'GPL3'
    __description__ = 'This plugin automatically uploads handshakes to a nextcloud webdav endpoint'

    def __init__(self):
        self.ready = False
        self.lock = threading.Lock()
        try:
            self.report = StatusFile('/root/.nextcloud_uploads', data_format='json')
        except JSONDecodeError as json_err:
            os.remove("/root/.nextcloud_uploads")
            self.report = StatusFile('/root/.nextcloud_uploads', data_format='json')

        self.options = dict()
        self.skip = list()

        self.session = None
        self.full_url = None

    def _make_path(self, dir):
        return f"{self.options['baseurl']}/remote.php/dav/files/{self.options['user']}/{dir}"

    def _make_session(self):
        s = requests.Session()
        s.auth = (self.options["user"], self.options["pass"])

        logging.info("[nextcloud] >> send first req!")

        # check if creds correct
        try:
            r = s.request("PROPFIND", self._make_path("./"))
            logging.info("[nextcloud] >> send first req 2!")

            if r.status_code == 401:
                logging.info("[nextcloud] >> wrong creds!")
                return False
            elif r.status_code == 404:
                logging.info("[nextcloud] >> path does not exist!")
                return False

            self.session = s
        except requests.exceptions.RequestException as e:
            logging.error("nextcloud: Got an exception checking credentials!")
            raise e

    def _make_dir(self, path):
        try:
            r = self.session.request("MKCOL", path)

            if r.status_code == 201:
                print("created new directory")
                return True
            else:
                return False
        except requests.exceptions.RequestException as e:
            logging.error("nextcloud: Got an exception while creating a dir.")
            raise e

    def _exists_dir(self, path):
        try:
            r = self.session.request("PROPFIND", path)

            if r.status_code == 404:
                return False
            else:
                return True
        except requests.exceptions.RequestException as e:
            logging.error("nextcloud: Got an exception while checking if a dir exists.")
            raise e

    def _upload_to_nextcloud(self, path, timeout=30):
        head, tail = os.path.split(path)
        destFile = self.full_url + '/' + tail

        with open(path, 'rb') as fp:
            try:
                r = self.session.put(destFile, data=fp.read())
            except requests.exceptions.RequestException as e:
                logging.error(f"nextcloud: Got an exception while uploading {path} -> {e}")
                raise e

    def on_loaded(self):
        for opt in ['baseurl', 'user', 'pass', 'path']:
            if opt not in self.options or (opt in self.options and self.options[opt] is None):
                logging.error(f"NEXTCLOUD: Option {opt} is not set.")
                return

        self.ready = True
        logging.info("NEXTCLOUD: Successfully loaded.")

    def on_internet_available(self, agent):
        with self.lock:
            if self.ready:
                config = agent.config()
                display = agent.view()

                reported = self.report.data_field_or('reported', default=dict())

                handshake_dir = config['bettercap']['handshakes']
                handshake_filenames = os.listdir(handshake_dir)
                handshake_paths = [os.path.join(handshake_dir, filename) for filename in handshake_filenames if
                                   filename.endswith('.pcap')]

                handshake_new = set(handshake_paths) - set(reported) - set(self.skip)

                # filter for new files
                handshake_new = []
                for hs in set(handshake_paths) - set(self.skip):
                    if hs not in reported:
                        handshake_new.append(hs)
                    else:
                        if os.path.getmtime(hs) > reported[hs]:
                            handshake_new.append(hs)

                logging.info(f"[nx]: found {len(handshake_new)} new handshakes")

                if handshake_new:
                    logging.info("nextcloud: Internet connectivity detected. Uploading new handshakes")

                    logging.info("[nextcloud] create session START")

                    self._make_session()

                    logging.info("[nextcloud] check for dir Half")

                    self.full_url = self._make_path(f"{self.options['path']}/")

                    logging.info("[nextcloud] create session DONE")
                    logging.info("[nextcloud] check for dir START")

                    if not self._exists_dir(self.full_url):
                        if not self._make_dir(self.full_url):
                            logging.info("[nextcloud] check for dir Fail")
                            logging.error("nextcloud: couldn't create necessary directory")
                            return

                    logging.info("[nextcloud] check for dir DONE")

                    for idx, handshake in enumerate(handshake_new):
                        logging.info(f"[nextcloud] uploading hs {handshake}, nr {idx + 1} out of {len(handshake_new)}")
                        display.set('status', f"Uploading handshake to nextcloud ({idx + 1}/{len(handshake_new)})")
                        display.update(force=True)
                        try:
                            logging.info("[nx] upload 1")
                            self._upload_to_nextcloud(handshake)
                            logging.info("[nx] upload 2")
                            reported[handshake] = os.path.getmtime(handshake)
                            logging.info("[nx] upload 3")
                            self.report.update(data={'reported': reported})
                            logging.info("nextcloud: Successfully uploaded %s", handshake)
                        except requests.exceptions.RequestException as req_e:
                            self.skip.append(handshake)
                            logging.error("nextcloud: %s", req_e)
                            continue
                        except OSError as os_e:
                            logging.error("nextcloud: %s", os_e)
                            continue
