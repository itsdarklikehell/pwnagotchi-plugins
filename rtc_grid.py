import ctypes
import ctypes.util
import datetime
import logging
import smbus
import time
import pwnagotchi.grid as grid
import pwnagotchi.plugins as plugins
import pwnagotchi.ui.fonts as fonts
from pwnagotchi.ui.components import Text
from pwnagotchi.ui.view import BLACK

CLOCK = "◴"
CLOCK_REALTIME = 0


class timespec(ctypes.Structure):
    _fields_ = [("tv_sec", ctypes.c_long), ("tv_nsec", ctypes.c_long)]


class RTCGrid(plugins.Plugin):
    __author__ = "SgtStroopwafel, sliim@mailoo.org"
    __version__ = "1.0.0"
    __license__ = "GPL3"
    __description__ = "Share RTC clock with peers. Some part of this code is based from: https://stackoverflow.com/questions/12081310"
    __name__ = "RTCGrid"
    __help__ = "Share RTC clock with peers. Some part of this code is based from: https://stackoverflow.com/questions/12081310"
    __dependencies__ = {
        "apt": ["none"],
        "pip": ["scapy"],
    }
    __defaults__ = {
        "enabled": false,
    }

    def __init__(self):
        self.ready = False
        logging.debug(f"[{self.__class__.__name__}] plugin init")
        self.title = ""
        self.rtc = False
        self.peer_rtc = None
        self.friends = {}

    def _set_local_clock(self):
        if not self.peer_rtc or not self.peer_rtc.adv.get("rtc"):
            return False

        logging.info(
            f"[{self.__class__.__name__}] Set datetime from peer %s",
            self.peer_rtc.full_name(),
        )

        time_tuple = datetime.datetime.fromtimestamp(
            self.peer_rtc.adv.get("rtc")["timestamp"]
        ).timetuple()

        librt = ctypes.CDLL(ctypes.util.find_library("rt"))

        ts = timespec()
        ts.tv_sec = int(time.mktime(datetime.datetime(*time_tuple[:6]).timetuple()))
        ts.tv_nsec = time_tuple[6] * 1000000

        # http://linux.die.net/man/3/clock_settime
        librt.clock_settime(CLOCK_REALTIME, ctypes.byref(ts))

    def on_loaded(self):
        try:
            if (
                "position" not in self.options
                or not self.options["position"]
                or len(self.options["position"].split(",")) != 2
            ):
                self.options["position"] = "100,-1"
            if (
                "peer_position" not in self.options
                or not self.options["peer_position"]
                or len(self.options["peer_position"].split(",")) != 2
            ):
                self.options["peer_position"] = "242,94"
            logging.info(f"[{self.__class__.__name__}] plugin loaded")
        except Exception as e:
            logging.error("rtc_grid.on_loaded: %s" % e)

    def on_ready(self, agent):
        try:
            bus = smbus.SMBus(1)
            bus.read_byte(0x68)
            logging.info("RTC module found.")
            self.rtc = True
        except OSError as e:
            if e.errno == 16:
                logging.info("RTC module found (busy).")
                self.rtc = True
            else:
                logging.warn("RTC module not found: %s" % e)
        except Exception as e:
            logging.error("rtc_grid.on_ready: %s" % e)

    def on_epoch(self, agent, epoch, data):
        try:
            if self.rtc:
                grid.call("/mesh/data", {"rtc": {"timestamp": time.time()}})
        except Exception as e:
            logging.error("rtc_grid.on_epoch: %s" % e)

    def on_peer_detected(self, agent, peer):
        try:
            if not peer.identity() in self.friends and peer.is_good_friend(
                agent.config()
            ):
                self.friends[peer.identity()] = peer
        except Exception as e:
            logging.error("rtc_grid.on_peer_detected: %s" % e)

    def on_ui_setup(self, ui):
        try:
            pos = self.options["position"].split(",")
            ui.add_element(
                "rtc",
                Text(
                    color=BLACK,
                    value=None,
                    position=(int(pos[0]), int(pos[1])),
                    font=fonts.Bold,
                ),
            )
            pos = self.options["peer_position"].split(",")
            ui.add_element(
                "rtc_peer",
                Text(
                    color=BLACK,
                    value=None,
                    position=(int(pos[0]), int(pos[1])),
                    font=fonts.Bold,
                ),
            )
        except Exception as e:
            logging.error("rtc_grid.on_ui_setup: %s" % e)

    def on_ui_update(self, ui):
        try:
            if not self.rtc and not self.peer_rtc:
                for i, p in self.friends.items():
                    if p.adv.get("rtc"):
                        self.peer_rtc = p

            if self.rtc:
                ui.set("rtc", CLOCK)
            elif self.peer_rtc:
                friend = ui.get("friend_name")
                if not friend:
                    ui.set("rtc_peer", None)
                    return False

                peer = friend.split(" ")
                if (
                    self.peer_rtc.name() == peer[1]
                    and str(self.peer_rtc.pwnd_run()) == peer[2]
                    and "(%d)" % self.peer_rtc.pwnd_total() == peer[3]
                ):
                    ui.set("rtc_peer", CLOCK)
                else:
                    ui.set("rtc_peer", None)

                if time.time() < self.peer_rtc.adv.get("rtc")["timestamp"]:
                    self._set_local_clock()
        except Exception as e:
            logging.error("rtc_grid.on_ui_update: %s" % e)

    def on_unload(self, ui):
        try:
            with ui._lock:
                ui.remove_element("rtc")
                ui.remove_element("rtc_peer")
        except Exception as e:
            logging.error("rtc_grid.on_unload: %s" % e)

    def on_webhook(self, path, request):
        logging.info(f"[{self.__class__.__name__}] webhook pressed")
