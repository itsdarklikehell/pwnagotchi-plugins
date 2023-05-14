import logging
import pwnagotchi.plugins as plugins


class Cuffs(plugins.Plugin):
    __author__ = 'idoloninmachina@gmail.com'
    __version__ = '0.1.4'
    __license__ = 'GPL3'
    __description__ = 'Restricts the pwnagotchi to only attack specified ap\'s'

    def __init__(self):
        logging.debug("[Cuffs] Cuffs plugin created")
        self.filtered_ap_list = None
        self.agent = None

    def on_loaded(self):
        logging.info("[Cuffs] Plugin loading")

        if 'whitelist' not in self.options:
            self.options['whitelist'] = list()
        self.original_get_access_points = None
        logging.info("[Cuffs] Plugin loaded")

    def on_unload(self, ui):
        self.agent.get_access_points = self.original_get_access_points
        self.original_get_access_points = None
        logging.info("[Cuffs] Plugin unloaded")

    def on_unfiltered_ap_list(self, agent, access_points):
        # Store the original get_access_points function if we do not already have it
        if self.original_get_access_points is None:
            self.original_get_access_points = agent.get_access_points
            self.agent = agent
            # Overwrite the get_access_points function to be our custom one
            logging.info(
                "[Cuffs] Overwriting get_access_points to custom function\nPlease ignore any error messages from Cuffs this epoch.")
            agent.get_access_points = self.custom_get_access_points

        count = 0
        for ap in access_points:
            # If the ap is being restricted by cuffs, remove it
            if not self.is_whitelisted(ap):
                access_points.remove(ap)
                count += 1
        self.filtered_ap_list = access_points
        logging.info(f"[Cuffs] Removed {count} unrestricted ap's")

    def on_wifi_update(self, agent, access_points):
        for ap in access_points:
            # If the app is not being whitelisted by cuffs, it should not be here
            if not self.is_whitelisted(ap):
                logging.error(
                    f"[Cuffs] Cuffs is enabled, yet an unrestricted ap ({ap['hostname']} from {ap['vendor']}) made it past our filter.")
                logging.debug(f"[Cuffs] Unrestricted AP: {ap}")

    def on_deauthentication(self, agent, access_point, client_station):
        # If the ap is not being whitelisted by cuffs, it should not be here
        if not self.is_whitelisted(access_point):
            logging.error(
                f"[Cuffs] Cuffs is enabled, yet an unrestricted ap ({access_point['hostname']} from {access_point['vendor']})has made it past our filter and has been deauthenticated.")
            logging.debug(f"Unrestricted AP: {access_point}")

    def is_whitelisted(self, ap):
        '''
            Returns True if the ap is not being restricted by cuffs
        '''
        for whitelisted_ap in self.options['whitelist']:
            if whitelisted_ap.lower() == ap['mac'].lower() or whitelisted_ap.lower() == ap['hostname'].lower():
                return True
        return False

    def custom_get_access_points(self):
        aps = []
        try:
            s = self.agent.session()
            plugins.on("unfiltered_ap_list", self.agent, s['wifi']['aps'])
            for ap in s['wifi']['aps']:
                if ap['encryption'] == '' or ap['encryption'] == 'OPEN':
                    continue
                if self.is_whitelisted(ap):
                    aps.append(ap)
        except Exception as e:
            logging.exception(f"Error while getting access points ({e})")
        aps.sort(key=lambda ap: ap['channel'])
        return self.agent.set_access_points(aps)
