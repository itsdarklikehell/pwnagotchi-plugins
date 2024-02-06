import json
import logging
import os
import pwnagotchi.plugins as plugins


class Tracker(plugins.Plugin):
    __author__ = "sliim@mailoo.org"
    __version__ = "1.0.0"
    __license__ = "GPL3"
    __description__ = """
    Track seen access points & clients.
    If gps plugin is enabled, position will be saved.
    """

    def __init__(self):
        self.gps = None
        self.tracker_dir = "/var/local/pwnagotchi/tracker"
        self.known_devices = {}

    def _coords(self):
        if self.gps and self.gps.running:
            coordinates = self.gps.coordinates
            if coordinates and all([coordinates["Latitude"], coordinates["Longitude"]]):
                return coordinates
        return None

    def _save_device(self, filename, data):
        filename = filename.replace("/", "_").replace(" ", "_")
        if not os.path.isdir(self.tracker_dir):
            logging.error(
                "[tracker] %s is not a directory. Device not saved." % self.tracker_dir
            )
            return False

        olddata = {}

        if data["mac"] in self.known_devices:
            olddata = self.known_devices[data["mac"]]
        elif os.path.exists("%s/%s" % (self.tracker_dir, filename)):
            with open("%s/%s" % (self.tracker_dir, filename), "r") as f:
                olddata = json.load(f)
            self.known_devices[olddata["mac"]] = olddata

        if "rssi" not in data:
            logging.debug(
                "[tracker] Device %s not saved because rssi key is missing"
                % data["mac"]
            )
            return False

        if (
            olddata
            and "rssi" in olddata
            and olddata["rssi"] > data["rssi"]
            and "coordinates" in olddata
        ):
            logging.debug(
                "[tracker] Known device %s not updated because new rssi (%d) < old rssi (%d) and GPS position is already known"
                % (data["mac"], data["rssi"], olddata["rssi"])
            )
            return False

        coords = self._coords()
        if coords:
            data["coordinates"] = coords
        elif olddata:
            logging.debug(
                "[tracker] Known device %s not updated because we don't have new GPS position"
                % data["mac"]
            )
            return False

        olddata.update(data)

        self.known_devices[olddata["mac"]] = olddata
        with open("%s/%s" % (self.tracker_dir, filename), "w") as f:
            f.write(json.dumps(olddata))
        logging.debug("[tracker] Updated device %s" % data["mac"])

    def _save_ap(self, ap):
        self._save_device(
            "%s_%s.json" % (ap["hostname"], ap["mac"].replace(":", "").lower()), ap
        )

    def _save_client(self, ap, client):
        self._save_device(
            "%s_client_%s.json"
            % (ap["hostname"], client["mac"].replace(":", "").lower()),
            client,
        )

    def on_loaded(self):
        try:
            if not os.path.exists(self.tracker_dir):
                os.makedirs(self.tracker_dir, exist_ok=True)
            logging.info("[tracker] plugin loaded")
        except Exception as e:
            logging.error("tracker.on_loaded: %s" % e)

    def on_ready(self, agent):
        try:
            self.gps = plugins.loaded["gps"]
            if not self.gps:
                logging.warning(
                    "[tracker] gps plugin not loaded! Coordinates will not be saved."
                )
        except Exception as e:
            logging.error("tracker.on_ready: %s" % e)

    def on_wifi_update(self, agent, aps):
        try:
            for ap in aps:
                self._save_ap(ap)
                if ap["clients"]:
                    for client in ap["clients"]:
                        self._save_client(ap, client)
        except Exception as e:
            logging.error("tracker.on_wifi_update: %s" % e)

    def on_association(self, agent, ap):
        try:
            self._save_ap(ap)
            if ap["clients"]:
                for client in ap["clients"]:
                    self._save_client(ap, client)
        except Exception as e:
            logging.error("tracker.on_association: %s" % e)

    def on_deauthentication(self, agent, ap, client):
        try:
            self._save_ap(ap)
            self._save_client(ap, client)
            if ap["clients"]:
                for client in ap["clients"]:
                    self._save_client(ap, client)
        except Exception as e:
            logging.error("tracker.on_deauthentication: %s" % e)

    def on_handshake(self, agent, filename, ap, client):
        try:
            self._save_ap(ap)
            self._save_client(ap, client)
            if ap["clients"]:
                for client in ap["clients"]:
                    self._save_client(ap, client)
        except Exception as e:
            logging.error("tracker.on_handshake: %s" % e)
