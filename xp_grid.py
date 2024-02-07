import logging
import pwnagotchi.grid as grid
import pwnagotchi.plugins as plugins
import pwnagotchi.ui.fonts as fonts
from pwnagotchi.ui.components import Text
from pwnagotchi.ui.view import BLACK


class XPGrid(plugins.Plugin):
    __author__ = "SgtStroopwafel, sliim@mailoo.org"
    __version__ = "1.0.0"
    __license__ = "GPL3"
    __description__ = (
        "Level sharing between peers for xp plugin. xp plugin must be enabled."
    )

    def __init__(self):
        self.known_peers = {}

    def on_loaded(self):
        try:
            if (
                "name_position" not in self.options
                or not self.options["name_position"]
                or len(self.options["name_position"].split(",")) != 2
            ):
                self.options["name_position"] = "63,95"
            if (
                "position" not in self.options
                or not self.options["position"]
                or len(self.options["position"].split(",")) != 2
            ):
                self.options["position"] = "36,95"
            logging.info(f"[{self.__class__.__name__}] plugin loaded")
        except Exception as e:
            logging.error("xp_grid.on_loaded: %s" % e)

    def on_level_update(self, level):
        try:
            grid.call("/mesh/data", {"level": level})
        except Exception as e:
            logging.error("xp_grid.on_level_update: %s" % e)

    def on_rank_update(self, rank):
        try:
            grid.call("/mesh/data", {"rank": rank})
        except Exception as e:
            logging.error("xp_grid.on_rank_update: %s" % e)

    def on_peer_detected(self, agent, peer):
        try:
            self.known_peers[peer.identity()] = peer
        except Exception as e:
            logging.error("xp_grid.on_peer_detected: %s" % e)

    def on_ui_setup(self, ui):
        try:
            pos = self.options["position"].split(",")
            name_pos = self.options["name_position"].split(",")
            ui.remove_element("friend_name")
            ui.add_element(
                "friend_name",
                Text(
                    color=BLACK,
                    value=None,
                    position=(int(name_pos[0]), int(name_pos[1])),
                    font=fonts.BoldSmall,
                ),
            )
            ui.add_element(
                "friend_level",
                Text(
                    color=BLACK,
                    value=None,
                    position=(int(pos[0]), int(pos[1])),
                    font=fonts.BoldSmall,
                ),
            )
        except Exception as e:
            logging.error("xp_grid.on_ui_setup: %s" % e)

    def on_ui_update(self, ui):
        try:
            friend = ui.get("friend_name")
            if not friend:
                ui.set("friend_level", None)
                return False

            peer = friend.split(" ")
            for i, p in self.known_peers.items():
                if (
                    p.name() == peer[1]
                    and str(p.pwnd_run()) == peer[2]
                    and "(%d)" % p.pwnd_total() == peer[3]
                ):
                    level = ""
                    rank = ""

                    if p.adv.get("level"):
                        level = p.adv.get("level")
                    if p.adv.get("rank"):
                        rank = p.adv.get("rank")

                    ui.set("friend_level", "[%d]" % level)
                    return True
        except Exception as e:
            logging.error("xp_grid.on_ui_update: %s" % e)

    def on_unload(self, ui):
        try:
            with ui._lock:
                ui.remove_element("friend_level")
        except Exception as e:
            logging.error("xp_grid.on_unload: %s" % e)
