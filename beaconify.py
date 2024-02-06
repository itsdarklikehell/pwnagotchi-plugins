#!/usr/bin/python3
import logging
import sys
import json
import struct
import time
import subprocess
import threading
from threading import Thread
from pwnagotchi import grid
from pwnagotchi.mesh.peer import Peer

from scapy.all import Dot11, Dot11Beacon, Dot11Elt, RadioTap, sendp
import pwnagotchi
import pwnagotchi.plugins as plugins
from pwnagotchi.grid import call, get_advertisement_data


class Beaconify(plugins.Plugin):
    __author__ = "Artur Oliveira"
    __version__ = "1.0.6"
    __license__ = "GPL3"
    __description__ = "A plugin to send beacon frames more often and restarts pwngrid when it stops listening for other units' beacons."
    __name__ = "Beaconify"
    __help__ = "A plugin to send beacon frames more often and restarts pwngrid when it stops listening for other units' beacons."
    __defaults__ = {
        "enabled": False,
    }
    dependencies__ = {
        "pip": ["scapy"],
    }

    # Define the custom Information Element IDs
    # Taken from:
    # https://github.com/jayofelony/pwngrid/blob/6ff48395fa19257c8296f127f4bbdec1152ba5e1/wifi/defines.go#L21
    ID_WHISPER_PAYLOAD = 222
    ID_WHISPER_COMPRESSION = 223
    ID_WHISPER_IDENTITY = 224
    ID_WHISPER_SIGNATURE = 225
    ID_WHISPER_STREAM_HEADER = 226

    BroadcastAddr = "ff:ff:ff:ff:ff:ff"
    SignatureAddrStr = "de:ad:be:ef:de:ad"

    def __init__(self):
        self._lock = threading.Lock()
        self.options = dict()
        self.peer_id = None
        self.signature = None
        self.stream_id = 0
        self.seq_num = 0
        self.seq_tot = 0
        self.compress = False
        self.self_encounters = 0
        self.restart_pwngrid_retries = -1
        self.restart_pwngrid_time = 60
        self.init_pwngrid_time = 60
        self.cooldown_pwngrid_check = time.perf_counter()
        self.waiting_pwngrid = False
        self.beacon_thread = None
        self.pwngrid_thread = None
        self.title = ""

    def info_element(self, id, info):
        return Dot11Elt(ID=id, info=info)

    def on_loaded(self):
        logging.info(f"[{self.__class__.__name__}] plugin loaded")
        self.iface = pwnagotchi.config["main"]["iface"]
        self.sleeptime = self.options.get("sleeptime")
        if self.sleeptime is None:
            self.sleeptime = 5
            logging.info(
                f"[Beaconify] sleeptime not defined in config. Setting to default {self.sleeptime}"
            )
        self.beacontime = self.options.get("beacontime")
        if self.beacontime is None:
            self.beacontime = 0.1
            logging.info(
                f"[Beaconify] beacontime not defined in config. Setting to default {self.beacontime}"
            )

    def restart_pwngrid(self):
        def inner_func(obj):
            with obj._lock:
                self.waiting_pwngrid = True
                retries = obj.restart_pwngrid_retries
                while retries != 0:
                    process = subprocess.Popen(
                        f"systemctl restart pwngrid-peer",
                        shell=True,
                        stdin=None,
                        stdout=open("/dev/null", "w"),
                        stderr=None,
                        executable="/bin/bash",
                    )
                    process.wait()
                    if process.returncode > 0:
                        logging.warning(
                            f"[Beaconify] pwngrid restarted! Waiting {obj.init_pwngrid_time} for its initialization."
                        )
                        time.sleep(obj.init_pwngrid_time)
                        self.waiting_pwngrid = False
                        return
                    else:
                        logging.warning(
                            f"[Beaconify] Failed to restart pwngrid! Waiting {obj.restart_pwngrid_time} before trying again."
                        )
                        time.sleep(obj.restart_pwngrid_time)
                        retries -= 1
                logging.warning(
                    f"[Beaconify] Failed to restart pwngrid too many times! The unit probably won't send or receive beacons until reboot."
                )
                self.waiting_pwngrid = False

        if (self.pwngrid_thread is None) or (not self.pwngrid_thread.is_alive()):
            self.pwngrid_thread = Thread(target=inner_func, args=(self,))
            self.pwngrid_thread.start()
        else:
            logging.info(
                f"[Beaconify] Skipping pwngrid restart thread because there is one alive yet."
            )

    # called when a known peer is lost
    def on_peer_lost(self, agent, peer):
        pass

    # called when a new peer is detected
    def on_peer_detected(self, agent, peer):
        # Checks for self beacons to detect
        logging.info(
            f"[Beaconify] I'm {self.identity} and just detect {peer.identity()}."
        )
        if peer.identity() == self.identity:
            self.found_self = True
            logging.info(f"[Beaconify] Hey! I can hear my own echoes!.")

    def on_wait(self, agent, t):
        # Start sending beacons for t seconds
        logging.info(f"[Beaconify] Waiting for {t} seconds. Sending beacons!")
        self.send_beacon(agent, t)

    # called when the agent is sleeping for t seconds
    def on_sleep(self, agent, t):
        # Start sending beacons for t seconds
        logging.info(f"[Beaconify] Sleeping for {t} seconds. Sending beacons!")
        self.send_beacon(agent, t)

    def on_unload(self, ui):
        # Stop sending beacons
        pass

    def on_ready(self, agent):
        self.identity = agent.fingerprint()
        self.mon_iface = pwnagotchi.config["main"]["iface"]
        pass

    def on_config_changed(self, config):
        logging.info(f"[Beaconify] config changed")
        self.iface = config["main"]["iface"]
        if self.options.get("sleeptime") is not None:
            self.sleeptime = self.options.get("sleeptime")
            logging.info(
                f"[Beaconify] sleeptime not defined in config. Setting to default {self.sleeptime}"
            )
        if self.options.get("beacontime") is not None:
            self.beacontime = self.options.get("beacontime")
            logging.info(
                f"[Beaconify] beacontime not defined in config. Setting to default {self.beacontime}"
            )

    # def pack_one_of(from_addr, to_addr, peer_id, signature, stream_id, seq_num, seq_tot, payload, compress):
    def pack_one_of(self, payload):
        layers = [
            RadioTap(),
            Dot11(
                addr1=Beaconify.BroadcastAddr,
                addr2=Beaconify.SignatureAddrStr,
                addr3=Beaconify.SignatureAddrStr,
                type=0,
                subtype=8,
            ),
            Dot11Beacon(),
        ]

        if self.peer_id is not None:
            layers.append(
                self.info_element(Beaconify.ID_WHISPER_IDENTITY, self.peer_id)
            )

        if self.signature is not None:
            layers.append(
                self.info_element(Beaconify.ID_WHISPER_SIGNATURE, self.signature)
            )

        if self.stream_id > 0:
            stream_header = struct.pack(
                "<QQQ", self.stream_id, self.seq_num, self.seq_tot
            )
            layers.append(
                self.info_element(Beaconify.ID_WHISPER_STREAM_HEADER, stream_header)
            )

        # Compress if needed
        # if compress:
        #    compressed_payload = compress_payload(payload)  # Implement this function as needed
        #    layers.append(info_element(ID_WHISPER_COMPRESSION, b'\x01'))
        #    payload = compressed_payload

        # Add payload in chunks
        chunk_size = 0xFF
        for i in range(0, len(payload), chunk_size):
            chunk = payload[i : i + chunk_size]
            layers.append(self.info_element(Beaconify.ID_WHISPER_PAYLOAD, chunk))

        # Combine all layers into a single packet
        packet = layers[0]
        for layer in layers[1:]:
            packet = packet / layer

        # Serialize to bytes
        return packet

    def send_beacon(self, agent, time_duration):
        def inner_func(obj, time_duration, agent):
            starting_time = time.perf_counter()
            while time.perf_counter() - starting_time < time_duration:
                try:
                    if obj.waiting_pwngrid:
                        logging.info(
                            f"[Beaconify] Can't send beacon. Waiting pwngrid cooldown. Sleeping {obj.sleeptime} seconds."
                        )
                        time.sleep(obj.sleeptime)
                        logging.info(
                            f"[Beaconify] Restarting cooldown of {obj.init_pwngrid_time} sending beacons without checking self encounters."
                        )
                        obj.cooldown_pwngrid_check = time.perf_counter()
                        continue
                    payload = json.dumps(get_advertisement_data()).encode()
                    packet = obj.pack_one_of(payload)
                    sendp(packet, iface=obj.iface, verbose=0)
                    time.sleep(obj.beacontime)
                except Exception as e:
                    logging.warn(
                        f"[Beaconify] Interface {obj.iface} down? Sleeping {obj.sleeptime} seconds and retrying..."
                    )
                    logging.debug(e, exc_info=True)
                    time.sleep(obj.sleeptime)
                    logging.warn(f"[Beaconify] Slept {obj.sleeptime}. Retrying now.")
            # Check for deafness
            # If the unit stops hearing itself (and consequently other units),
            # we can fix it by restarting pwngrid.
            pwngrid_check_cooldown = time.perf_counter() - obj.cooldown_pwngrid_check
            if pwngrid_check_cooldown > obj.init_pwngrid_time:
                grid_peers = grid.peers()
                if len(grid_peers) == 0:
                    logging.info(
                        f"[Beaconify] No peers (not even myself!) Restarting pwngrid!"
                    )
                    self.restart_pwngrid()
                else:
                    logging.info(
                        f"[Beaconify] Found {len(grid_peers)} peers (including myself!)"
                    )
            else:
                logging.info(
                    f"[Beaconify] Cooldown of {pwngrid_check_cooldown} before checking pwngrid again."
                )

        if (self.beacon_thread is None) or (not self.beacon_thread.is_alive()):
            self.beacon_thread = Thread(
                target=inner_func, args=(self, time_duration, agent)
            )
            self.beacon_thread.start()
        else:
            logging.info(
                f"[Beaconify] Skipping beacon thread because there is one alive yet."
            )
