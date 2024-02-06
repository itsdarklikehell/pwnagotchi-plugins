import os
import sys
import argparse
import paramiko
from paramiko import SFTPClient
from subprocess import Popen, PIPE, STDOUT
import signal
import re

# ====================================
# SFTP Configuration - CHANGE THESE
# ====================================
config = {
    "host": "10.0.0.2",  # Set your Pwnagotchi IP
    "username": "pi",  # Set your SSH username
    "password": "raspberry",  # Set your SSH password
    "handshake_dir": "/home/pi/handshakes/",  # Set your handshake directory on the Pwnagotchi
    "local_dir": "./pcap/",
}


def create_local_dir():
    if not os.path.exists(config["local_dir"]):
        os.makedirs(config["local_dir"])


def get_files():
    try:
        transport = paramiko.Transport((config["host"], 22))
        transport.connect(username=config["username"], password=config["password"])
        sftp = SFTPClient.from_transport(transport)

        create_local_dir()

        print("Connecting to Pwnagotchi...")
        remote_files = sftp.listdir(config["handshake_dir"])

        for file in remote_files:
            if file.endswith(".pcap"):
                remote_file = os.path.join(config["handshake_dir"], file)
                local_file = os.path.join(config["local_dir"], file)
                print(f"Downloading {remote_file} to {local_file}")
                sftp.get(remote_file, local_file)

        sftp.close()
        transport.close()
    except paramiko.AuthenticationException:
        print("Authentication failed. Please check your SSH username and password.")
        sys.exit(1)
    except paramiko.SSHException as e:
        print(f"Unable to establish SSH connection: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"An error occurred: {e}")
        sys.exit(1)


def remove_files():
    print("Removing processed files from Pwnagotchi...")
    try:
        transport = paramiko.Transport((config["host"], 22))
        transport.connect(username=config["username"], password=config["password"])
        sftp = SFTPClient.from_transport(transport)

        file_list = sftp.listdir(config["handshake_dir"])
        for filename in file_list:
            if filename.endswith(".pcap"):
                sftp.remove(config["handshake_dir"] + filename)

        sftp.close()
        transport.close()
    except paramiko.AuthenticationException:
        print("Authentication failed. Please check your SSH username and password.")
        sys.exit(1)
    except paramiko.SSHException as e:
        print(f"Unable to establish SSH connection: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"An error occurred: {e}")
        sys.exit(1)


def grab_bssid(file):
    try:
        process = Popen(
            [
                "tshark",
                "-r",
                config["local_dir"] + file,
                "-T",
                "fields",
                "-e",
                "wlan.bssid",
            ],
            stdout=PIPE,
            stderr=PIPE,
        )
        stdout, _ = process.communicate()
        output = stdout.decode().splitlines()

        if output:
            return list(set(output))  # retourne la liste des BSSIDs uniques

        return None
    except Exception as e:
        print(f"Error occurred while grabbing BSSID: {e}")
        return None


def convert_file(file):
    try:
        print(f"Processing: {file}")

        process = Popen(
            [
                "hcxpcapngtool",
                "-o",
                f'./pmkid/{file.replace(".pcap", "")}.pmkid',
                config["local_dir"] + file,
            ],
            stdout=PIPE,
            stderr=PIPE,
        )
        _, stderr = process.communicate()

        if "PMKID(s) written" in stderr.decode():
            print("Found PMKID")
            return True
        else:
            process = Popen(
                [
                    "hcxpcapngtool",
                    "-o",
                    f'./hccapx/{file.replace(".pcap", "")}.hccapx',
                    config["local_dir"] + file,
                ],
                stdout=PIPE,
                stderr=PIPE,
            )
            _, stderr = process.communicate()

            if "handshake(s) written" in stderr.decode():
                print("Found Handshake")
                return True

        return "No PMKID or Handshake found."
    except Exception as e:
        print(f"Error occurred while converting file: {e}")
        return None


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-r",
        "--remove",
        action="store_true",
        help="delete handshake files after processing",
    )
    args = parser.parse_args()

    get_files()

    files = os.listdir(config["local_dir"])

    # If 'pmkid' directory doesn't exist, create it.
    if not os.path.exists("./pmkid"):
        os.mkdir("./pmkid")

    # If 'hccapx' directory doesn't exist, create it.
    if not os.path.exists("./hccapx"):
        os.mkdir("./hccapx")

    for file in files:
        bssids = grab_bssid(file)
        if not bssids:
            print(f"No BSSID found for {file}")
        else:
            for bssid in bssids:
                result = convert_file(file)
                if result is True:
                    print(f"Added {file} to database with BSSID: {bssid}")
                else:
                    print(result)

    if args.remove:
        remove_files()

    print("\n\n")
    print("===================")
    print("   All done.  ")
    print("===================")


if __name__ == "__main__":
    main()
