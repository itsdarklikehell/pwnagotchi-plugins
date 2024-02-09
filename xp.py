import copy
import glob
import json
import logging
import os
import time

import pwnagotchi.plugins as plugins
import pwnagotchi.ui.fonts as fonts
import pwnagotchi.ui.faces as faces
import pwnagotchi.utils as utils
from pwnagotchi.ui.components import LabeledValue, Text, Rect, FilledRect
from pwnagotchi.ui.view import BLACK

from flask import render_template_string
from flask import abort
from flask import Response

# TODO: jquery mobile notifications ?

TEMPLATE = """
{% extends "base.html" %}
{% set active_page = "plugins" %}
{% block title %}
  {{ name }} XP
{% endblock %}

{% block styles %}
  {{ super() }}
  <style>
    h1 {
      text-align: center;
    }
    #infos {
      margin: 10px;
    }
    #face {
      font-family: monospace;
    }
    #progressbar {
      font-size: 25px;
      width: 80%;
      margin: auto;
      border: 3px solid black;
      filter: opacity(100%);
      text-shadow: none;
    }
    #progress {
      background: lime;
      color: black;
      position: fixed;
      z-index: 1;
    }
    #level {
        position: fixed;
        z-index: 2;
    }
    #percents {
        position: fixed;
        z-index: 2;
        right: 0;
    }
    #messages {
      width: 90%;
      margin: auto;
      font-size: 80%;
      font-family: monospace;
      border: 1px solid black;
    }
    #buttons {
      right: 5%;
      position: absolute;
    }
    .error {
      color: red;
    }
    .message {
      color: black;
    }
  </style>
{% endblock %}

{% block script %}
  var level = document.getElementById('level');
  var percents = document.getElementById('percents');
  var xp = document.getElementById('xp');
  var next_level = document.getElementById('next_level');
  var progress = document.getElementById('progress');
  var rank = document.getElementById('rank');
  var face = document.getElementById('face');
  var messages = document.getElementById('messages');
  var xhr = new XMLHttpRequest();

  function toggledebug() {
    var toggle = new XMLHttpRequest();
    toggle.open('GET', '{{ url_for('plugins') }}/xp/toggledebug');
    toggle.send();
  }

  function clearMessages() {
    messages.innerHTML = "";
  }

  function error(msg) {
    var tr = document.createElement("tr");
    var td = document.createElement("td");
    td.textContent = msg;
    tr.appendChild(td);
    tr.className = "error";
    messages.prepend(tr);
  }

  xhr.onload = function() {
    if (xhr.status != 200) {
      error("> " + xhr.status + ": " + xhr.response);
      return false;
    }

    var data = JSON.parse(xhr.response);
    level.textContent = "LVL " + data.level;
    xp.textContent = data.xp;
    next_level.textContent = data.next_level;
    rank.textContent = data.rank;
    face.textContent = data.face;
    progress.setAttribute("style", "width:" + data.percents + "%;");
    percents.textContent = data.percents.toFixed(2) + "%";

    data.messages.forEach((msg) => {
      var tr = document.createElement("tr");
      var td = document.createElement("td");
      td.textContent = "> " + msg;
      tr.appendChild(td);
      tr.className = "message";
      messages.prepend(tr);
    });

    data.errors.forEach((err) => {
      error("> " + err);
    });
  }

  xhr.onerror = function() {
    error("> Cannot fetch data. Request failed..");
  }

  setInterval(function() {
    xhr.open('GET', '{{ url_for('plugins') }}/xp/data');
    xhr.send();
  }, 3000);
{% endblock %}

{% block content %}
  <h1>{{ name }} XP</h1>
  <div id="progressbar">
  <div id="level">-</div>
  <div id="percents">-</div>
  <div id="progress"><wbr></div>
  <wbr>
  </div>
  <div id="infos">
  <div>XP: <span id="xp">-</span>/<span id="next_level">-</span>
  <span id="buttons">
  <button data-role="none" onclick="clearMessages()">Clear</button>
  <button data-role="none" onclick="toggledebug()">Debug</button>
  </span>
  </div>
  <div>Rank: <span id="rank">-</span>&nbsp;<span id="face"></span></div>
  </div>
  <table id="messages"></table>
{% endblock %}
"""


EVENTS_XP = {
    "ai_ready": 5,
    "ai_best_reward": 20,
    "ai_training_step": 5,
    "ai_training_end": 15,
    "ai_worst_reward": -20,
    "association": 5,
    "bored": -2,
    "deauthentication": 10,
    "epoch_rewarded": 1,
    "epoch": 0.1,
    "excited": 5,
    "handshake": 20,
    "handshake_new": 100,
    "handshakes_100": 500,
    "peer_detected": 5,
    "good_friend_detected": 10,
    "sad": -2,
}

RANKS = {
    "newbie": {"level": 1, "head": "()", "face": "look_l"},
    "rookie": {"level": 5, "head": "❪❫", "face": "look_r"},
    "kiddie": {"level": 10, "head": "❨❩", "face": "look_l_happy"},
    "student": {"level": 15, "head": "◖◗", "face": "look_r_happy"},
    "insider": {"level": 20, "head": "⎛⎞", "face": "motivated"},
    "infiltrator": {"level": 25, "head": "⎝⎠", "face": "sleep2"},
    "pineap-fan": {"level": 30, "head": "⟪⟫", "face": "friend"},
    "parasit": {"level": 35, "head": "❰❱", "face": "intense"},
    "wardriver": {"level": 40, "head": "⎞⎞", "face": "cool"},
    "profiler": {"level": 45, "head": "⎠⎝", "face": "happy"},
    "hunter": {"level": 50, "head": "[]", "face": "grateful"},
    "tracker": {"level": 55, "head": "⁅⁆", "face": "excited"},
    "pwner": {"level": 60, "head": "⟦⟧", "face": "smart"},
    "hacker": {"level": 65, "head": "{}", "face": "awake"},
    "hAIx0r": {"level": 70, "head": "❴❵", "face": "motivated"},
    "dumper": {"level": 75, "head": "/\\", "face": "grateful"},
    "elite": {"level": 80, "head": "⎠⎞", "face": "debug"},
    "pwnbot": {"level": 85, "head": "⎛⎛", "face": "broken"},
    "sentinel": {"level": 90, "head": "╔╗", "face": "sleep"},
    "terminator": {"level": 95, "head": "❲❳", "face": "cool"},
    "legend": {"level": 100, "head": "⦗⦘", "face": "cool"},
}


MULTIPLIER = 1.05
BASE = 750


class XP(plugins.Plugin):
    __author__ = "SgtStroopwafel, sliim@mailoo.org"
    __version__ = "1.0.0"
    __license__ = "GPL3"
    __description__ = "XP / Leveling implementation. Just for fun!"
    __name__ = "XP"
    __help__ = "XP / Leveling implementation. Just for fun!"
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
        self.xp_file = "/var/local/pwnagotchi/xp.txt"
        self.xp = 0
        self.level = 0
        self.next_level = 0
        self.percents = 0
        self.rank = list(RANKS.keys())[0]
        self.agent = None
        self.handshakes = 0
        self.ai_ready = False

        # WEBUI
        self.messages = []
        self.errors = []
        self.debug = False

        # UI positions
        self.level_position = False
        self.rank_position = False
        self.progressbar_position = False

    def _error(self, msg):
        logging.error(f"[{self.__class__.__name__}] %s" % msg)
        self.errors.append(msg)

    def _save_xp(self):
        try:
            with open(self.xp_file, "w") as f:
                f.write(str(self._get_xp()))
        except Exception as e:
            self._error("Cannot write to %s: %s" % (self.xp_file, str(e)))

    def _update_xp(self, event, multiplier=1):
        if event in EVENTS_XP:
            if not self.ready:
                logging.warn(f"[{self.__class__.__name__}] Plugin not ready yet!")
                return False

            xp = EVENTS_XP[event] * multiplier
            if not self.ai_ready:
                xp /= 4
            logging.info(
                f"[{self.__class__.__name__}] Update %.3f xp from event %s"
                % (xp, event)
            )
            self.xp += float("%.3f" % xp)
            self._save_xp()
            self._update_level()

    def _get_xp(self):
        return float("%.3f" % self.xp)

    def _update_level(self):
        level = 1
        next_level = BASE
        old = 0

        while self.xp >= next_level:
            old = next_level
            next_level = int(next_level * MULTIPLIER + (BASE * 3))
            level += 1

        self.percents = (100 * (self.xp - old)) / (next_level - old)

        if level > self.level:
            if self.level != 0:
                plugins.on("level_up", level)
            self._update_agent(level)

        self.level = level
        self.next_level = next_level
        plugins.on("level_update", level)

    def _update_agent(self, level):
        current_rank = self.rank
        update = None

        for name, rank in RANKS.items():
            if level >= rank["level"]:
                self.rank = name

        if self.rank != current_rank:
            if self.level != 0:
                self.messages.append("New rank: %s :]" % self.rank)

            head = RANKS[self.rank]["head"]
            update = copy.copy(self.agent.config()["ui"]["faces"])
            for key, value in update.items():
                update[key] = value.replace("(", head[0]).replace(")", head[1])
            faces.load_from_config(update)
        plugins.on("rank_update", self.rank)

    def _progress(self, p):
        return [
            (p[0] + 1, p[1]),
            ((self.percents * (p[2] - p[0]) / 100) + p[0] - 2, p[3]),
        ]

    def on_loaded(self):
        try:
            if not os.path.exists(os.path.dirname(self.xp_file)):
                os.makedirs(os.path.dirname(self.xp_file), exist_ok=True)

            opts = self.options

            if opts["level_position"] and len(opts["level_position"].split(",")) == 2:
                self.level_position = [
                    int(i) for i in opts["level_position"].split(",")
                ]
            if opts["rank_position"] and len(opts["rank_position"].split(",")) == 2:
                self.rank_position = [int(i) for i in opts["rank_position"].split(",")]
            if (
                opts["progressbar_position"]
                and len(opts["progressbar_position"].split(",")) == 4
            ):
                self.progressbar_position = [
                    int(i) for i in opts["progressbar_position"].split(",")
                ]

            logging.info(f"[{self.__class__.__name__}] plugin loaded")
        except Exception as e:
            self._error("on_loaded error: %s" % str(e))
            return False

    def on_ready(self, agent):
        try:
            self.agent = agent
            self.handshakes = utils.total_unique_handshakes(
                agent.config()["bettercap"]["handshakes"]
            )

            if os.path.exists(self.xp_file):
                with open(self.xp_file, "r") as f:
                    self.xp = float(f.read())
            elif self.options["load_initial_xp"]:
                logging.info(
                    f"[{self.__class__.__name__}] Loading initial XP from last activities.."
                )
                xp = 0

                if os.path.exists("/root/brain.json"):
                    with open("/root/brain.json", "r") as f:
                        xp = json.load(f)["epochs_lived"] * EVENTS_XP["epoch"]
                        logging.info(
                            f"[{self.__class__.__name__}] Loaded %d XP from lived epoch"
                            % xp
                        )
                        self.xp += xp

                xp = self.handshakes * EVENTS_XP["handshake"]
                logging.info(
                    f"[{self.__class__.__name__}] Loaded %d XP from pwned hanshakes"
                    % xp
                )
                self.xp += xp

                if os.path.exists("/root/peers"):
                    xp = (
                        len(glob.glob("/root/peers/*.json"))
                        * EVENTS_XP["peer_detected"]
                    )
                    logging.info(
                        f"[{self.__class__.__name__}] Loaded %d XP from detected peers"
                        % xp
                    )
                    self.xp += xp

            self._save_xp()

            logging.info(
                f"[{self.__class__.__name__}] plugin initialized: current xp: %f"
                % self._get_xp()
            )
            self.ready = True
            self._update_level()
        except Exception as e:
            self._error("on_ready error: %s" % str(e))

    def on_level_up(self, level):
        logging.info(f"[{self.__class__.__name__}] LEVEL UP! (%d)" % level)
        self.messages.append("LEVEL UP! %s" % faces.COOL)

        try:
            self.agent.view().set("status", "LEVEL UP!")
            self.agent.view().set("face", faces.COOL)
            self.agent.view().update(force=True)
        except Exception as e:
            self._error("Error LVL UP status: %s" % str(e))

    def on_ui_setup(self, ui):
        try:
            if self.level_position:
                ui.add_element(
                    "level",
                    LabeledValue(
                        color=BLACK,
                        label="lvl",
                        value=str(self.level),
                        position=(self.level_position[0], self.level_position[1]),
                        label_font=fonts.BoldSmall,
                        text_font=fonts.Small,
                    ),
                )
            if self.rank_position:
                ui.add_element(
                    "rank",
                    Text(
                        color=BLACK,
                        value=str(self.rank),
                        position=(self.rank_position[0], self.rank_position[1]),
                        font=fonts.Small,
                    ),
                )
            if self.progressbar_position:
                ui.add_element(
                    "progressbar",
                    Rect(
                        color=BLACK,
                        xy=[
                            (
                                self.progressbar_position[0],
                                self.progressbar_position[1],
                            ),
                            (
                                self.progressbar_position[2],
                                self.progressbar_position[3],
                            ),
                        ],
                    ),
                )
                ui.add_element(
                    "progress",
                    FilledRect(
                        color=BLACK, xy=self._progress(self.progressbar_position)
                    ),
                )
        except Exception as e:
            self._error("on_ui_setup error: %s" % str(e))

    def on_ui_update(self, ui):
        try:
            if self.level_position:
                ui.set("level", str(self.level))
            if self.rank_position:
                ui.set("rank", str(self.rank))
            if self.progressbar_position:
                with ui._lock:
                    old = ui._state._state["progress"].xy
                    new = self._progress(self.progressbar_position)
                    if old != new:
                        ui._state._state["progress"].xy = new
                        ui._state._changes["progress"] = True
        except Exception as e:
            self._error("on_ui_update error: %s" % str(e))

    def on_unload(self, ui):
        try:
            self._save_xp()
            with ui._lock:
                if self.level_position:
                    ui.remove_element("level")
                if self.rank_position:
                    ui.remove_element("rank")
                if self.progressbar_position:
                    ui.remove_element("progressbar")
                    ui.remove_element("progress")
        except Exception as e:
            self._error("on_unload error: %s" % str(e))

    def on_webhook(self, path, request):
        try:
            if not path or path == "/":
                return render_template_string(
                    TEMPLATE, name=self.agent.config()["main"]["name"]
                )

            if path == "data":
                jsonResponse = json.dumps(
                    {
                        "level": self.level,
                        "xp": self._get_xp(),
                        "next_level": self.next_level,
                        "percents": self.percents,
                        "rank": self.rank,
                        "face": getattr(faces, RANKS[self.rank]["face"].upper()),
                        "messages": self.messages,
                        "errors": self.errors,
                    }
                )

                self.messages = []
                self.errors = []
                return Response(jsonResponse, mimetype="application/json")

            if path == "toggledebug":
                if self.debug:
                    self.debug = False
                    self.messages.append("Debug mode disabled.")
                else:
                    self.debug = True
                    self.messages.append("Debug mode enabled.")

                return Response(
                    json.dumps({"debug": self.debug}), mimetype="application/json"
                )

            abort(404)
        except Exception as e:
            self._error("on_webhook error: %s" % str(e))

    def on_ai_ready(self, agent):
        try:
            self._update_xp("ai_ready")
            self.ai_ready = True

            if self.debug:
                self.messages.append("AGENT: %s" % agent)
            self.messages.append("AI ready!")
        except Exception as e:
            self._error("on_ai_ready error: %s" % str(e))

    def on_ai_best_reward(self, agent, reward):
        try:
            self._update_xp("ai_best_reward")

            if self.debug:
                self.messages.append("REWARD: %s" % reward)
            self.messages.append("Best reward %s" % faces.MOTIVATED)
        except Exception as e:
            self._error("on_ai_best_reward error: %s" % str(e))

    def on_ai_worst_reward(self, agent, reward):
        try:
            self._update_xp("ai_worst_reward")

            if self.debug:
                self.messages.append("REWARD: %s" % reward)
            self.messages.append("Worst reward %s" % faces.DEMOTIVATED)
        except Exception as e:
            self._error("on_ai_worst_reward error: %s" % str(e))

    def on_ai_training_step(self, agent):
        try:
            self._update_xp("ai_training_step")

            if self.debug:
                self.messages.append("AGENT: %s" % agent)
            self.messages.append("End of training step %s" % faces.GRATEFUL)
        except Exception as e:
            self._error("on_ai_training_step error: %s" % str(e))

    def on_ai_training_end(self, agent):
        try:
            self._update_xp("ai_training_end")

            if self.debug:
                self.messages.append("AGENT: %s" % agent)
            self.messages.append("End of training %s" % faces.EXCITED)
        except Exception as e:
            self._error("on_ai_training_end error: %s" % str(e))

    def on_association(self, agent, ap):
        try:
            self._update_xp("association")

            if self.debug:
                self.messages.append("AP: %s" % ap)
            self.messages.append(
                "Associated with %s (%s) %s"
                % (ap["hostname"], ap["mac"], faces.LOOK_L_HAPPY)
            )
        except Exception as e:
            self._error("on_association error: %s" % str(e))

    def on_bored(self, agent):
        try:
            self._update_xp("bored")

            if self.debug:
                self.messages.append("AGENT: %s" % agent)
            self.messages.append("I'm bored %s" % faces.BORED)
        except Exception as e:
            self._error("on_bored error: %s" % str(e))

    def on_deauthentication(self, agent, ap, client):
        try:
            self._update_xp("deauthentication")

            if self.debug:
                self.messages.append("AP: %s" % ap)
                self.messages.append("CLIENT: %s" % client)
            self.messages.append(
                "Deauthenticated %s from %s (%s) %s"
                % (client["mac"], ap["hostname"], ap["mac"], faces.COOL)
            )
        except Exception as e:
            self._error("on_deauthentication error: %s" % str(e))

    def on_epoch(self, agent, epoch, data):
        try:
            if data["reward"] > 0:
                self._update_xp("epoch_rewarded")
            else:
                self._update_xp("epoch")

            if self.debug:
                self.messages.append("DATA: %s" % data)
            self.messages.append("Epoch #%s finished!" % epoch)
        except Exception as e:
            self._error("on_epoch error: %s" % str(e))

    def on_excited(self, agent):
        try:
            self._update_xp("excited")

            if self.debug:
                self.messages.append("AGENT: %s" % agent)
            self.messages.append("I'm so excited %s" % faces.EXCITED)
        except Exception as e:
            self._error("on_excited error: %s" % str(e))

    def on_handshake(self, agent, filename, ap, client):
        try:
            while not os.path.exists(filename):
                logging.warn(
                    f"[{self.__class__.__name__}] on_handshake: Waiting for %s to be created."
                    % filename
                )
                time.sleep(1)

            handshakes = utils.total_unique_handshakes(
                agent.config()["bettercap"]["handshakes"]
            )

            if handshakes > self.handshakes:
                if handshakes % 100 == 0:
                    self._update_xp("handshakes_100", handshakes / 100)
                else:
                    self._update_xp("handshake_new")
            else:
                self._update_xp("handshake")

            self.handshakes = handshakes

            if self.debug:
                self.messages.append("AP: %s" % ap)
                self.messages.append("CLIENT: %s" % client)
            self.messages.append(
                "New handshake by %s for %s (%s) %s"
                % (client["mac"], ap["hostname"], ap["mac"], faces.COOL)
            )
        except Exception as e:
            self._error("on_handshake error: %s" % str(e))

    def on_peer_detected(self, agent, peer):
        try:
            self._update_xp("peer_detected")

            if peer.is_good_friend(agent.config()):
                self._update_xp("good_friend_detected")

            if self.debug:
                self.messages.append("PEER: %s" % peer)
            self.messages.append(
                "Hey AIx0r %s is in the place %s" % (peer.name(), faces.FRIEND)
            )
        except Exception as e:
            self._error("on_peer_detected error: %s" % str(e))

    def on_sad(self, agent):
        try:
            self._update_xp("sad")

            if self.debug:
                self.messages.append("AGENT: %s" % agent)
            self.messages.append("I'm sad %s" % faces.SAD)
        except Exception as e:
            self._error("on_sad error: %s" % str(e))
