import os
import json
import time
import logging
import math, numpy as np
import pwnagotchi.plugins as plugins
from pwnagotchi.ui.components import Text, LabeledValue
from pwnagotchi.ui.view import BLACK
import pwnagotchi.ui.fonts as fonts
from flask import abort
from flask import render_template_string
from geopy import distance
from math import pi
from operator import itemgetter, attrgetter
from PIL import ImageFont

# should not be changed


class PWNAware(plugins.Plugin):
    __author__ = "SgtStroopwafel, evilsocket@gmail.com"
    __version__ = "1.0.0"
    __license__ = "GPL3"
    __description__ = "display information from dump1090 about nearby airplanes"
    __name__ = "PWNAware"
    __help__ = "display information from dump1090 about nearby airplanes"
    __dependencies__ = {
        "apt": ["none"],
        "pip": ["scapy", "geopy"],
    }
    __defaults__ = {
        "enabled": False,
    }

    def get_bearing(self, lat1, lon1, lat2, lon2):

        # convert to radians
        lat1 = (lat1 * pi) / 180.0
        lon1 = (lon1 * pi) / 180.0
        lat2 = (lat2 * pi) / 180.0
        lon2 = (lon2 * pi) / 180.0

        dLon = lon2 - lon1
        y = math.sin(dLon) * math.cos(lat2)
        x = math.cos(lat1) * math.sin(lat2) - math.sin(lat1) * math.cos(
            lat2
        ) * math.cos(dLon)
        brng = np.rad2deg(math.atan2(y, x))
        if brng < 0:
            brng += 360
        return brng

    def check_airplanes(self):
        plane_file = "/var/run/dump1090-fa/aircraft.json"
        if os.path.isfile(plane_file):
            f = open(plane_file)
            planes = json.load(f)
            clat = 0
            clong = 0
            pcount = 0
            realplanes = []

            m_lat = self.coordinates["Latitude"]
            m_long = self.coordinates["Longitude"]

            for p in planes["aircraft"]:
                if "flight" not in p:
                    p["flight"] = "*%-7s" % p["hex"].upper()
                if "lat" in p and "flight" in p:
                    # print(repr(p))
                    p["calc_dist"] = distance.geodesic(
                        (p["lat"], p["lon"]), (m_lat, m_long)
                    )
                    p["calc_bearing"] = self.get_bearing(
                        m_lat, m_long, p["lat"], p["lon"]
                    )
                    realplanes.append(p)
                else:
                    # print(p)
                    pass
            f.close()

            s_planes = sorted(realplanes, key=lambda plane: plane["calc_dist"])

            self.airplanes = s_planes

            return s_planes

    def update_scoreboard(self, agent):
        planes = self.check_airplanes()
        self.numplanes = len(planes)
        nb = ""

        try:
            for i in range(len(self.airplanes)):
                p = planes[i]
                alt = "{:,}".format(
                    p["alt_baro"] if not "alt_geom" in p else p["alt_geom"]
                )
                flight = p["flight"].strip()
                logging.debug(
                    f"[{self.__class__.__name__}] %s %s" % (i, len(self.ap_text))
                )
                if flight in self.watch_planes:
                    watch = self.watch_planes[flight]
                elif ("*" + p["hex"]) in self.watch_planes:
                    watch = self.watch_planes["*" + p[hex]]
                else:
                    watch = ""
                self.ap_text[i] = "%-8s%4.1f %3s\N{DEGREE SIGN} %6s %s\n" % (
                    ("*" + p["hex"]) if flight == "" else flight,
                    p["calc_dist"].miles,
                    int(p["calc_bearing"]),
                    alt,
                    watch,
                )
                logging.debug(
                    f"[{self.__class__.__name__}] %s %s" % (i, len(self.ap_text))
                )
                nb += self.ap_text[i]

            self.scoreboard = nb
        except Exception as e:
            logging.error(
                f"[{self.__class__.__name__}] update scoreboard: %s" % repr(err)
            )

        self._updated = True

    def __init__(self):
        logging.debug(f"[{self.__class__.__name__}] plugin init")
        logging.info(f"[{self.__class__.__name__}] pwn the friendly skies!")

        self._updated = False
        self.airplanes = []
        self.ap_text = [1, 2, 3, 4, 5, 6, 7, 8, 9, 0, 11, 12, 13, 14, 15]
        self.SmallerFont = ImageFont.truetype("DejaVuSansMono", 10)

        self.scoreboard = "--"
        self.watch_planes = {
            "": "ACAB",
            "N626TS": "EM420",
            "DAL954": "ATL>",
            "DAL786": ">ATL",
            "SKW3682": "EUG>SEA",
            "UAL1979": ">EWR",
            "N": "ACAB",
            "DAL720": ">DTW",
            "JZA595": "SMF>YVR",
            "ACA554": "YVR>LAX",
        }
        # get default from options would be better
        self.coordinates = {"Latitude": 45.4568, "Longitude": -122.6486}

    def on_webhook(self, path, request):
        # link to skyaware page
        try:
            # list planes, have input to label or make notes, save to JSON file or database
            planes = self.check_airplanes()
            if request.method == "GET":
                if True or path == "/" or not path:
                    ret = '<html><head><title>Pwnaware</title><meta name="csrf_token" content="{{ csrf_token() }}"></head>'
                    ret += "<body><h1>Pwnaware</h1>"
                    logging.info(f"[{self.__class__.__name__}] webook called2")
                    ret += '<img src="/ui?%s">' % int(time.time())
                    logging.info(f"[{self.__class__.__name__}] webook called")
                    ret += '<form method=post action="pwnaware/update">'
                    ret += '<input id="csrf_token" name="csrf_token" type="hidden" value="{{ csrf_token() }}">'
                    ret += "<table><tr><th>hex id</th><th>Flight</th><th>Dist</th><th>Dir</th><th>Alt</th><th>Notes</th><th>Enter new note</th></tr>\n"

                    for p in planes:
                        ret += "<tr><td>%s</td>" % p["hex"]
                        ret += "<td><b>%s</b></td>" % p["flight"]
                        ret += "<td>%5.1fmi</td>" % p["calc_dist"].miles
                        ret += "<td>%3s\N{DEGREE SIGN}</td>" % int(p["calc_bearing"])
                        ret += "<td>%s</td>" % (
                            p["alt_baro"] if not "alt_geom" in p else p["alt_geom"]
                        )
                        flight = p["flight"].strip()
                        hex = p["hex"].strip()
                        if flight in self.watch_planes:
                            watch = self.watch_planes[flight]
                        elif ("*" + hex) in self.watch_planes:
                            watch = self.watch_planes["*" + hex]
                        else:
                            watch = ""
                        ret += "<td>%s</td>" % watch
                        ret += (
                            '<td><input type=text id="note_%s_%s" name="note_%s_%s" size="30"></td>'
                            % (flight, hex, flight, hex)
                        )

                        ret += "</tr>\n"
                    ret += "</table>"
                    ret += (
                        '<input type=submit name=submit value="update"></form></pre><p>'
                    )
                    ret += "</body></html>"
                    return render_template_string(ret)
            # else if POST, update new settings in a json file and apply them at runtime
            elif request.method == "POST":
                logging.info(f"[{self.__class__.__name__}] POST: %s" % path)
                ret = '<html><head><title>PWNAware. Update!</title><meta name="csrf_token" content="{{ csrf_token() }}"></head><body>'
                if path == "update":
                    ret += "<h1>PWNAware Update</h1>"
                    ret += '<img src="/ui?%s">' % int(time.time())
                    ret += "<h2>Path</h2><code>%s</code><p>" % repr(request.values)
                    updated = False
                    for k, val in request.form.items():
                        if k.startswith("note_"):
                            if val:
                                (dummy, planeID, planeHex) = k.split("_")
                                ret += "%s -> %s<p>" % (planeID, val)
                                if not planeID.startswith("*"):
                                    # don't store fake plane IDs
                                    self.watch_planes[planeID] = val
                                self.watch_planes["*%s" % planeHex] = val
                                updated = True
                    if updated:
                        with open("/etc/pwnagotchi/airplane.notes", "w") as f:
                            f.write(json.dumps(self.watch_planes, indent=4))
                            ret += "Saved changes<p>"

                ret += "</body></html>"

                return render_template_string(ret)

        except Exception as e:
            ret = "<html><head><title>Pwnaware Error</title></head>"
            ret += "<body><h1>%s</h1></body></html>" % repr(e)
            logging.error(f"[{self.__class__.__name__}] %s" % repr(r))
            return render_template_string(ret)
        pass

    # called when the plugin is loaded
    def on_loaded(self):
        logging.info(f"[{self.__class__.__name__}] plugin loaded")
        logging.warn(f"[{self.__class__.__name__}] options = " % self.options)
        if not "numPlanes" in self.options:
            self.options["numPlanes"] = 4

    # called before the plugin is unloaded
    def on_unload(self, ui):
        try:
            for i in range(self.options["numPlanes"]):
                ui.remove_element("airplane%i" % i)
                logging.info(f"[{self.__class__.__name__}] Removed airplane%i" % i)
            ui.remove_element("airplane_header")
            logging.info(f"[{self.__class__.__name__}] plugin unloaded")
        except Exception as err:
            logging.info(f"[{self.__class__.__name__}] unload err %s " % repr(err))

    # called hen there's internet connectivity
    def on_internet_available(self, agent):
        self.update_scoreboard(agent)
        pass

    # called to setup the ui elements
    def on_ui_setup(self, ui):
        # add custom UI elements
        try:
            self.SmallFont = ImageFont.truetype("DejaVuSansMono", 12)
            self.SmallerFont = ImageFont.truetype("DejaVuSansMono", 8)

            height = 22
            for i in range(self.options["numPlanes"]):
                height += 12
                ui.add_element(
                    "airplane%i" % (self.options["numPlanes"] - i - 1),
                    Text(
                        color=BLACK,
                        value="--",
                        position=(ui.width() / 2 - 69, ui.height() - height),
                        font=self.SmallFont,
                    ),
                )
                logging.info("Added airplane%i" % (self.options["numPlanes"] - i - 1))

            height += 11
            ui.add_element(
                "airplane_header",
                Text(
                    color="Yellow",
                    value="flight  dis dir   alt(ft)",
                    position=(ui.width() / 2 - 73, ui.height() - height),
                    font=self.SmallerFont,
                ),
            )
        except Exception as e:
            logging.error(f"[{self.__class__.__name__}] UI setup: %s" % repr(e))

    # called when the ui is updated
    def on_ui_update(self, ui):
        # update those elements
        for i in range(self.options["numPlanes"]):
            try:
                if i < len(self.airplanes):
                    ui.set("airplane%i" % i, "%s" % self.ap_text[i])
                else:
                    ui.set(
                        "airplane%i" % i,
                        "%8s%4s %4s %6s" % ("   --   ", " -- ", " -- ", "  --  "),
                    )
            except Exception as e:
                logging.warn(
                    f"[{self.__class__.__name__}] ui_update: i %s airplanes %s ap_text %s err %s"
                    % (i, len(self.airplanes), len(self.ap_text), repr(e))
                )

        ui.set(
            "airplane_header",
            "%2i PLANES DIS(mi) DIR   ALT[ft]......" % len(self.airplanes),
        )

    # called when the hardware display setup is done, display is an hardware specific object
    def on_display_setup(self, display):
        pass

    # called when everything is ready and the main loop is about to start
    def on_ready(self, agent):
        logging.info(f"[{self.__class__.__name__}] plugin ready")

        if os.path.isfile("/etc/pwnagotchi/airplane.notes"):
            with open("/etc/pwnagotchi/airplane.notes", "r") as f:
                self.watch_planes = json.load(f)

        self.update_scoreboard(agent)
        # you can run custom bettercap commands if you want
        #   agent.run('ble.recon on')
        # or set a custom state
        #   agent.set_bored()

    # called when the agent is waiting for t seconds
    def on_wait(self, agent, t):
        self.update_scoreboard(agent)

    # called when the agent is sleeping for t seconds
    def on_sleep(self, agent, t):
        self.update_scoreboard(agent)

    # called when an epoch is over (where an epoch is a single loop of the main algorithm)
    def on_epoch(self, agent, epoch, epoch_data):
        self.update_scoreboard(agent)
        pass

    def on_bcap_gps_new(self, agent, event):
        try:
            coords = event["data"]
            if coords and all([coords["Latitude"], coords["Longitude"]]):
                self.coordinates = coords

        except Exception as err:
            logging.warn(
                f"[{self.__class__.__name__}] gps.new err: %s, %s"
                % (repr(event), repr(err))
            )


if __name__ == "__main__":

    pa = PWNAware()

    watch_planes = {
        "N626TS  ": "*EM69420",
        "DAL954  ": "Atlanta inbound",
        "DAL786  ": "PDX to ATL",
        "AIC174  ": "woohoo",
        "SKW3682 ": "EUG to SEA",
        "UAL1979 ": "PDX to EWR",
        "N       ": "PDX Police",
        "DAL720  ": "PDX-DTW",
        "JZA595  ": "Jazz Sac-Vancouver",
        "ACA554  ": "YVR-LAX",
    }

    if os.path.isfile("/etc/pwnagotchi/airplane.notes"):
        with open("/etc/pwnagotchi/airplane.notes", "r") as f:
            watch_planes = json.load(f)

    planes = pa.check_airplanes()

    for p in planes:

        if p["flight"].strip() in watch_planes:
            print(
                "%8s %6.2fmi %6.2f\N{DEGREE SIGN} %6sft %s"
                % (
                    p["flight"],
                    p["calc_dist"].miles,
                    p["calc_bearing"],
                    "{:,}".format(
                        p["alt_baro"] if not "alt_geom" in p else p["alt_geom"]
                    ),
                    watch_planes[p["flight"].strip()],
                )
            )
        else:
            print(
                "%8s %6.2fmi %6.2f\N{DEGREE SIGN} %6sft"
                % (
                    p["flight"],
                    p["calc_dist"].miles,
                    p["calc_bearing"],
                    "{:,}".format(
                        p["alt_baro"] if not "alt_geom" in p else p["alt_geom"]
                    ),
                )
            )
