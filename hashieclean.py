import logging
import io
import subprocess
import os
import json
import pwnagotchi.plugins as plugins
from threading import Lock
from pwnagotchi.ui.components import LabeledValue
from pwnagotchi.ui.view import BLACK
import pwnagotchi.ui.fonts as fonts

"""
hcxpcapngtool needed, to install:
> git clone https://github.com/ZerBea/hcxtools.git
> cd hcxtools
> apt-get install libcurl4-openssl-dev libssl-dev zlib1g-dev
> make
> sudo make install
"""


class hashieclean(plugins.Plugin):
    __author__ = "SgtStroopwafel, Artur Oliveira"
    __version__ = "1.0.0"
    __license__ = "GPL3"
    __description__ = """
This version removes "lonely pcaps", those can't be converted
either to the formats .22000 (EAPOL) or .16800 (PMKID). As
the number of lonely pcaps increase the loading time increases
too. Besides that, the checking for completed handshakes
is done more efficiently, thus reducing even further 
the loading time of the plugin.

Based on hashi by junohea.mail@gmail.com:

Attempt to automatically convert pcaps to a crackable format.
If successful, the files  containing the hashes will be saved 
in the same folder as the handshakes. 
The files are saved in their respective Hashcat format:
    - EAPOL hashes are saved as *.22000
    - PMKID hashes are saved as *.16800
All PCAP files without enough information to create a hash are
    stored in a file that can be read by the webgpsmap plugin.

Why use it?:
    - Automatically convert handshakes to crackable formats! 
        We dont all upload our hashes online ;)
    - Repair PMKID handshakes that hcxpcapngtool misses
    - If running at time of handshake capture, on_handshake can
        be used to improve the chance of the repair succeeding
    - Be a completionist! Not enough packets captured to crack a network?
        This generates an output file for the webgpsmap plugin, use the
        location data to revisit networks you need more packets for!
    
Additional information:
    - Currently requires hcxpcapngtool compiled and installed
    - Attempts to repair PMKID hashes when hcxpcapngtool cant find the SSID
    - hcxpcapngtool sometimes has trouble extracting the SSID, so we 
        use the raw 16800 output and attempt to retrieve the SSID via tcpdump
    - When access_point data is available (on_handshake), we leverage 
        the reported AP name and MAC to complete the hash
    - The repair is very basic and could certainly be improved!
Todo:
    Make it so users dont need hcxpcapngtool (unless it gets added to the base image)
        Phase 1: Extract/construct 22000/16800 hashes through tcpdump commands
        Phase 2: Extract/construct 22000/16800 hashes entirely in python
    Improve the code, a lot
"""
    __name__ = "hashieclean"
    __help__ = """
This version removes "lonely pcaps", those can't be converted
either to the formats .22000 (EAPOL) or .16800 (PMKID). As
the number of lonely pcaps increase the loading time increases
too. Besides that, the checking for completed handshakes
is done more efficiently, thus reducing even further 
the loading time of the plugin.

Based on hashi by junohea.mail@gmail.com:

Attempt to automatically convert pcaps to a crackable format.
If successful, the files  containing the hashes will be saved 
in the same folder as the handshakes. 
The files are saved in their respective Hashcat format:
    - EAPOL hashes are saved as *.22000
    - PMKID hashes are saved as *.16800
All PCAP files without enough information to create a hash are
    stored in a file that can be read by the webgpsmap plugin.

Why use it?:
    - Automatically convert handshakes to crackable formats! 
        We dont all upload our hashes online ;)
    - Repair PMKID handshakes that hcxpcapngtool misses
    - If running at time of handshake capture, on_handshake can
        be used to improve the chance of the repair succeeding
    - Be a completionist! Not enough packets captured to crack a network?
        This generates an output file for the webgpsmap plugin, use the
        location data to revisit networks you need more packets for!
    
Additional information:
    - Currently requires hcxpcapngtool compiled and installed
    - Attempts to repair PMKID hashes when hcxpcapngtool cant find the SSID
    - hcxpcapngtool sometimes has trouble extracting the SSID, so we 
        use the raw 16800 output and attempt to retrieve the SSID via tcpdump
    - When access_point data is available (on_handshake), we leverage 
        the reported AP name and MAC to complete the hash
    - The repair is very basic and could certainly be improved!
Todo:
    Make it so users dont need hcxpcapngtool (unless it gets added to the base image)
        Phase 1: Extract/construct 22000/16800 hashes through tcpdump commands
        Phase 2: Extract/construct 22000/16800 hashes entirely in python
    Improve the code, a lot
"""
    __dependencies__ = {
        "apt": ["none"],
        "pip": ["scapy"],
    }
    __defaults__ = {
        "enabled": False,
    }

    def __init__(self):
        self.ready = False
        logging.debug(f"[{self.__class__.__name__}] plugin init")
        self.title = ""
        self.lock = Lock()

    def on_loaded(self):
        logging.info(f"[{self.__class__.__name__}] plugin loaded")

    # called when everything is ready and the main loop is about to start
    def on_config_changed(self, config):
        logging.info(f"[{self.__class__.__name__}] config changed")
        handshake_dir = config["bettercap"]["handshakes"]
        if "interval" not in self.options or not (
            self.status.newer_then_hours(self.options["interval"])
        ):
            logging.info(f"[{self.__class__.__name__}] Starting batch conversion of pcap files")
            with self.lock:
                self._process_stale_pcaps(handshake_dir)

    def is22000(self, filename):
        fullpathNoExt = filename.split(".")[0]
        return os.path.isfile(fullpathNoExt + ".22000")

    def is16800(self, filename):
        fullpathNoExt = filename.split(".")[0]
        return os.path.isfile(fullpathNoExt + ".16800")

    def on_handshake(self, agent, filename, access_point, client_station):
        with self.lock:
            handshake_status = []
            fullpathNoExt = filename.split(".")[0]
            name = filename.split("/")[-1:][0].split(".")[0]

            if self.is22000(filename) or self.is16800(filename):
                if self.is22000(filename):
                    handshake_status.append(
                        "Already have {}.22000 (EAPOL)".format(name)
                    )
                if self.is16800(filename):
                    handshake_status.append(
                        "Already have {}.16800 (PMKID)".format(name)
                    )
            else:
                if self._writeEAPOL(filename):
                    handshake_status.append(
                        "Created {}.22000 (EAPOL) from pcap".format(name)
                    )
                if self._writePMKID(filename, access_point):
                    handshake_status.append(
                        "Created {}.16800 (PMKID) from pcap".format(name)
                    )

            if handshake_status:
                logging.info(
                    f"[{self.__class__.__name__}] Good news:\n\t" + "\n\t".join(handshake_status)
                )

    def _writeEAPOL(self, fullpath):
        fullpathNoExt = fullpath.split(".")[0]
        filename = fullpath.split("/")[-1:][0].split(".")[0]
        result = subprocess.getoutput(
            "hcxpcapngtool -o {}.22000 {} >/dev/null 2>&1".format(
                fullpathNoExt, fullpath
            )
        )
        if os.path.isfile(fullpathNoExt + ".22000"):
            logging.debug(
                f"[{self.__class__.__name__}] [+] EAPOL Success: {}.22000 created".format(filename)
            )
            return True
        else:
            return False

    def _writePMKID(self, fullpath, apJSON):
        fullpathNoExt = fullpath.split(".")[0]
        filename = fullpath.split("/")[-1:][0].split(".")[0]
        result = subprocess.getoutput(
            "hcxpcapngtool -k {}.16800 {} >/dev/null 2>&1".format(
                fullpathNoExt, fullpath
            )
        )
        if os.path.isfile(fullpathNoExt + ".16800"):
            logging.debug(
                f"[{self.__class__.__name__}] [+] PMKID Success: {}.16800 created".format(filename)
            )
            return True
        else:  # make a raw dump
            result = subprocess.getoutput(
                "hcxpcapngtool -K {}.16800 {} >/dev/null 2>&1".format(
                    fullpathNoExt, fullpath
                )
            )
            if os.path.isfile(fullpathNoExt + ".16800"):
                if self._repairPMKID(fullpath, apJSON) == False:
                    logging.debug(
                        f"[{self.__class__.__name__}] [-] PMKID Fail: {}.16800 could not be repaired".format(
                            filename
                        )
                    )
                    return False
                else:
                    logging.debug(
                        f"[{self.__class__.__name__}] [+] PMKID Success: {}.16800 repaired".format(
                            filename
                        )
                    )
                    return True
            else:
                logging.debug(
                    f"[{self.__class__.__name__}] [-] Could not attempt repair of {} as no raw PMKID file was created".format(
                        filename
                    )
                )
                return False

    def _repairPMKID(self, fullpath, apJSON):
        hashString = ""
        clientString = []
        fullpathNoExt = fullpath.split(".")[0]
        filename = fullpath.split("/")[-1:][0].split(".")[0]
        logging.debug(f"[{self.__class__.__name__}] Repairing {}".format(filename))
        with open(fullpathNoExt + ".16800", "r") as tempFileA:
            hashString = tempFileA.read()
        if apJSON != "":
            clientString.append(
                "{}:{}".format(
                    apJSON["mac"].replace(":", ""), apJSON["hostname"].encode("hex")
                )
            )
        else:
            # attempt to extract the AP's name via hcxpcapngtool
            result = subprocess.getoutput(
                "hcxpcapngtool -X /tmp/{} {} >/dev/null 2>&1".format(filename, fullpath)
            )
            if os.path.isfile("/tmp/" + filename):
                with open("/tmp/" + filename, "r") as tempFileB:
                    temp = tempFileB.read().splitlines()
                    for line in temp:
                        clientString.append(
                            line.split(":")[0]
                            + ":"
                            + line.split(":")[1].strip("\n").encode().hex()
                        )
                os.remove("/tmp/{}".format(filename))
            # attempt to extract the AP's name via tcpdump
            tcpCatOut = subprocess.check_output(
                "tcpdump -ennr "
                + fullpath
                + " \"(type mgt subtype beacon) || (type mgt subtype probe-resp) || (type mgt subtype reassoc-resp) || (type mgt subtype assoc-req)\" 2>/dev/null | sed -E 's/.*BSSID:([0-9a-fA-F:]{17}).*\\((.*)\\).*/\\1\t\\2/g'",
                shell=True,
            ).decode("utf-8")
            if ":" in tcpCatOut:
                for i in tcpCatOut.split("\n"):
                    if ":" in i:
                        clientString.append(
                            i.split("\t")[0].replace(":", "")
                            + ":"
                            + i.split("\t")[1].strip("\n").encode().hex()
                        )
        if clientString:
            for line in clientString:
                if (
                    line.split(":")[0] == hashString.split(":")[1]
                ):  # if the AP MAC pulled from the JSON or tcpdump output matches the AP MAC in the raw 16800 output
                    hashString = hashString.strip("\n") + ":" + (line.split(":")[1])
                    if (len(hashString.split(":")) == 4) and not (
                        hashString.endswith(":")
                    ):
                        with open(fullpath.split(".")[0] + ".16800", "w") as tempFileC:
                            logging.debug(
                                f"[{self.__class__.__name__}] Repaired: {} ({})".format(
                                    filename, hashString
                                )
                            )
                            tempFileC.write(hashString + "\n")
                        return True
                    else:
                        logging.debug(
                            f"[{self.__class__.__name__}] Discarded: {} {}".format(line, hashString)
                        )
        else:
            os.remove(fullpath.split(".")[0] + ".16800")
            return False

    def _process_stale_pcaps(self, handshake_dir):
        handshakes_list = [
            os.path.join(handshake_dir, filename)
            for filename in os.listdir(handshake_dir)
            if filename.endswith(".pcap")
        ]
        failed_jobs = []
        successful_jobs = []
        lonely_pcaps = []
        failed_files = set()
        for num, handshake in enumerate(handshakes_list):
            fullpathNoExt = handshake.split(".")[0]
            pcapFileName = handshake.split("/")[-1:][0]
            lonely = True
            if self.is22000(handshake) or self.is16800(
                handshake
            ):  # Ignore completed handshakes
                lonely = False
                continue
            else:
                if self._writeEAPOL(handshake):
                    successful_jobs.append("22000: " + pcapFileName)
                    lonely = False
                else:
                    failed_jobs.append("22000: " + pcapFileName)
                if self._writePMKID(handshake, ""):
                    successful_jobs.append("16800: " + pcapFileName)
                    lonely = False
                else:
                    failed_jobs.append("16800: " + pcapFileName)
            if lonely:  # no 16800 AND no 22000
                lonely_pcaps.append(handshake)
                logging.debug(
                    f"[{self.__class__.__name__}] Batch job: added {} to lonely list".format(
                        pcapFileName
                    )
                )
            if ((num + 1) % 50 == 0) or (
                num + 1 == len(handshakes_list)
            ):  # report progress every 50, or when done
                logging.info(
                    f"[{self.__class__.__name__}] Batch job: {}/{} done ({} fails)".format(
                        num + 1, len(handshakes_list), len(lonely_pcaps)
                    )
                )
        if len(successful_jobs) > 0:
            logging.info(
                f"[{self.__class__.__name__}] Batch job: {} new handshake files created".format(
                    len(successful_jobs)
                )
            )
        if len(lonely_pcaps) > 0:
            logging.info(
                f"[{self.__class__.__name__}] Batch job: {} networks without enough packets to create a hash".format(
                    len(lonely_pcaps)
                )
            )
            logging.info(
                ff"[{self.__class__.__name__}] {len(lonely_pcaps)} lonely (failed) handshakes will be deleted."
            )
            self._getLocations(lonely_pcaps)
            for filename in lonely_pcaps:
                pcapFileName = filename.split("/")[-1:][0]
                logging.info(
                    f"[{self.__class__.__name__}] The pcap file is not a valid handshake. Deleting file:"
                    + pcapFileName.split("/")[0]
                )
                os.remove(filename)
                # Confirm the pcap file was deleted.
                if not os.path.exists(filename):
                    logging.debug(
                        f"[{self.__class__.__name__}] The pcap file was deleted for being incomplete. FILE: "
                        + pcapFileName
                    )
                # If the pcap file was not deleted, then send an error to the log.
                if os.path.exists(filename):
                    logging.error(
                        f"[{self.__class__.__name__}] Could not delete the pcap file. Please delete it manually. FILE: "
                        + pcapFileName
                    )

    def _getLocations(self, lonely_pcaps):
        # export a file for webgpsmap to load
        with open("/root/.incompletePcaps", "w") as isIncomplete:
            count = 0
            for pcapFile in lonely_pcaps:
                filename = pcapFile.split("/")[-1:][0]  # keep extension
                fullpathNoExt = pcapFile.split(".")[0]
                isIncomplete.write(filename + "\n")
                if (
                    os.path.isfile(fullpathNoExt + ".gps.json")
                    or os.path.isfile(fullpathNoExt + ".geo.json")
                    or os.path.isfile(fullpathNoExt + ".paw-gps.json")
                ):
                    count += 1
            if count != 0:
                logging.info(
                    f"[{self.__class__.__name__}] Used {} GPS/GEO/PAW-GPS files to find lonely networks, go check webgpsmap! ;)".format(
                        str(count)
                    )
                )
            else:
                logging.info(
                    f"[{self.__class__.__name__}] Could not find any GPS/GEO/PAW-GPS files for the lonely networks".format(
                        str(count)
                    )
                )

    def _getLocationsCSV(self, lonely_pcaps):
        # in case we need this later, export locations manually to CSV file, needs try/catch/paw-gps format/etc.
        locations = []
        for pcapFile in lonely_pcaps:
            filename = pcapFile.split("/")[-1:][0].split(".")[0]
            fullpathNoExt = pcapFile.split(".")[0]
            if os.path.isfile(fullpathNoExt + ".gps.json"):
                with open(fullpathNoExt + ".gps.json", "r") as tempFileA:
                    data = json.load(tempFileA)
                    locations.append(
                        filename
                        + ","
                        + str(data["Latitude"])
                        + ","
                        + str(data["Longitude"])
                        + ",50"
                    )
            elif os.path.isfile(fullpathNoExt + ".geo.json"):
                with open(fullpathNoExt + ".geo.json", "r") as tempFileB:
                    data = json.load(tempFileB)
                    locations.append(
                        filename
                        + ","
                        + str(data["location"]["lat"])
                        + ","
                        + str(data["location"]["lng"])
                        + ","
                        + str(data["accuracy"])
                    )
            elif os.path.isfile(fullpathNoExt + ".paw-gps.json"):
                with open(fullpathNoExt + ".paw-gps.json", "r") as tempFileC:
                    data = json.load(tempFileC)
                    locations.append(
                        filename
                        + ","
                        + str(data["lat"])
                        + ","
                        + str(data["long"])
                        + ",50"
                    )
        if locations:
            with open("/root/locations.csv", "w") as tempFileD:
                for loc in locations:
                    tempFileD.write(loc + "\n")
            logging.info(
                f"[{self.__class__.__name__}] Used {} GPS/GEO files to find lonely networks, load /root/locations.csv into a mapping app and go say hi!".format(
                    len(locations)
                )
            )

    def on_unload(self, ui):
        with ui._lock:
            logging.info(f"[{self.__class__.__name__}] plugin unloaded")

    def on_webhook(self, path, request):
        logging.info(f"[{self.__class__.__name__}] webhook pressed")