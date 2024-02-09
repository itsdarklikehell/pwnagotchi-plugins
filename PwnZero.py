import serial
from enum import Enum

import pwnagotchi.plugins as plugins
import pwnagotchi.ui.faces as faces


class PwnZeroParam(Enum):

    FACE = 4
    NAME = 5
    CHANNEL = 6
    APS = 7
    UPTIME = 8
    FRIEND = 9
    MODE = 10
    HANDSHAKES = 11
    MESSAGE = 12


class PwnMode(Enum):

    MANU = 4
    AUTO = 5
    AI = 6


class PwnFace(Enum):

    NO_FACE = 4
    DEFAULT_FACE = 5
    LOOK_R = 6
    LOOK_L = 7
    LOOK_R_HAPPY = 8
    LOOK_L_HAPPY = 9
    SLEEP = 10
    SLEEP2 = 11
    AWAKE = 12
    BORED = 13
    INTENSE = 14
    COOL = 15
    HAPPY = 16
    GRATEFUL = 17
    EXCITED = 18
    MOTIVATED = 19
    DEMOTIVATED = 20
    SMART = 21
    LONELY = 22
    SAD = 23
    ANGRY = 24
    FRIEND = 25
    BROKEN = 26
    DEBUG = 27
    UPLOAD = 28
    UPLOAD1 = 29
    UPLOAD2 = 30


class PwnZero(plugins.Plugin):
    __GitHub__ = ""
    __author__ = "(edited by: itsdarklikehell bauke.molenaar@gmail.com), github.com/Matt-London"
    __version__ = "1.0.0"
    __license__ = "MIT"
    __description__ = "Plugin to display the Pwnagotchi on the Flipper Zero"
    __name__ = "PwnZero"
    __help__ = "Plugin to display the Pwnagotchi on the Flipper Zero"
    __dependencies__ = {
        "apt": ["none"],
        "pip": ["scapy"],
    }
    __defaults__ = {
        "enabled": False,
    }
    PROTOCOL_START = 0x02
    PROTOCOL_END = 0x03

    def __init__(self, port: str = "/dev/serial0", baud: int = 115200):
        self.ready = False
        logging.debug(f"[{self.__class__.__name__}] plugin init")
        self.title = ""
        self._port = port
        self._baud = baud

        try:
            self._serialConn = serial.Serial(port, baud)
        except:
            raise "Cannot bind to port ({}) with baud ({})".format(port, baud)

    def on_loaded(self):
        logging.info(f"[{self.__class__.__name__}] plugin loaded")

    def close(self):
        self._serialConn.close()

    def _is_byte(self, i: int) -> bool:
        return 0 <= i < 256

    def _str_to_bytes(self, s: str):
        retVal = []
        for c in s:
            retVal.append(ord(c))

        return retVal

    def _send_data(self, param: int, args) -> bool:
        # Make sure everything is a valid byte
        if not self._is_byte(param):
            return False
        for i in args:
            if not self._is_byte(i):
                return False

        # Now we know everything is a valid byte

        # Build the sending data
        data = [self.PROTOCOL_START]
        data.append(param)
        for arg in args:
            data.append(arg)

        data.append(self.PROTOCOL_END)

        # Send data to flipper
        return self._serialConn.write(data) == len(data)

    # Public method commands
    def set_face(self, face: PwnFace) -> bool:
        return self._send_data(PwnZeroParam.FACE.value, [face.value])

    def set_name(self, name: str) -> bool:
        data = self._str_to_bytes(name)
        return self._send_data(PwnZeroParam.NAME.value, data)

    def set_channel(self, channel: int) -> bool:
        # Make sure channel is valid
        if not (0 <= channel <= 255):
            return False

        channelStr = "*"

        if channel != 0:
            channelStr = str(channel)

        data = self._str_to_bytes(channelStr)
        return self._send_data(PwnZeroParam.CHANNEL.value, data)

    def set_aps(self, apsCurrent: int, apsTotal) -> bool:
        data = self._str_to_bytes("{} ({})".format(apsCurrent, apsTotal))
        return self._send_data(PwnZeroParam.APS.value, data)

    def set_uptime(self, hh: int, mm: int, ss: int) -> bool:
        # Make sure all values are less than 100 and greater than 0
        if not (0 <= hh < 100 and 0 <= mm < 100 and 0 <= ss < 100):
            return False

        # A stands for adjusted
        hhA = str(hh).zfill(2)
        mmA = str(mm).zfill(2)
        ssA = str(ss).zfill(2)

        data = self._str_to_bytes("{}:{}:{}".format(hhA, mmA, ssA))
        return self._send_data(PwnZeroParam.UPTIME.value, data)

    def set_friend(self) -> bool:
        return False

    def set_mode(self, mode: PwnMode) -> bool:
        return self._send_data(PwnZeroParam.MODE.value, [mode.value])

    def set_handshakes(self, handshakesCurrent: int, handshakesTotal: int) -> bool:
        data = self._str_to_bytes("{} ({})".format(
            handshakesCurrent, handshakesTotal))
        return self._send_data(PwnZeroParam.HANDSHAKES.value, data)

    def set_message(self, message: str) -> bool:
        data = self._str_to_bytes(message)
        return self._send_data(PwnZeroParam.MESSAGE.value, data)

    def on_ui_setup(self, ui):
        pass

    def on_ui_update(self, ui):
        # Message
        self.set_message(ui.get("status"))

        # Mode
        modeEnum = None
        if ui.get("mode") == "AI":
            modeEnum = PwnMode.AI
        elif ui.get("mode") == "MANU":
            modeEnum = PwnMode.MANU
        elif ui.get("mode") == "AUTO":
            modeEnum = PwnMode.AUTO
        self.set_mode(modeEnum)

        # Channel
        channelInt = 0
        channel = ui.get("channel")
        if channel == "*":
            channelInt = 0
        else:
            channelInt = int(channel)
        self.set_channel(channelInt)

        # Uptime
        uptime = ui.get("uptime")
        uptimeSplit = uptime.split(":")
        self.set_uptime(int(uptimeSplit[0]), int(
            uptimeSplit[1]), int(uptimeSplit[2]))

        # APS
        aps = ui.get("aps")

        # name
        self.set_name(ui.get("name").replace(">", ""))

        # Face
        face = ui.get("face")

        faceEnum = None
        if face == faces.LOOK_R:
            faceEnum = PwnFace.LOOK_R
        elif face == faces.LOOK_L:
            faceEnum = PwnFace.LOOK_L
        elif face == faces.LOOK_R_HAPPY:
            faceEnum = PwnFace.LOOK_R_HAPPY
        elif face == faces.LOOK_L_HAPPY:
            faceEnum = PwnFace.LOOK_L_HAPPY
        elif face == faces.SLEEP:
            faceEnum = PwnFace.SLEEP
        elif face == faces.SLEEP2:
            faceEnum = PwnFace.SLEEP2
        elif face == faces.AWAKE:
            faceEnum = PwnFace.AWAKE
        elif face == faces.BORED:
            faceEnum = PwnFace.BORED
        elif face == faces.INTENSE:
            faceEnum = PwnFace.INTENSE
        elif face == faces.COOL:
            faceEnum = PwnFace.COOL
        elif face == faces.HAPPY:
            faceEnum = PwnFace.HAPPY
        elif face == faces.GRATEFUL:
            faceEnum = PwnFace.GRATEFUL
        elif face == faces.EXCITED:
            faceEnum = PwnFace.EXCITED
        elif face == faces.MOTIVATED:
            faceEnum = PwnFace.MOTIVATED
        elif face == faces.DEMOTIVATED:
            faceEnum = PwnFace.DEMOTIVATED
        elif face == faces.SMART:
            faceEnum = PwnFace.SMART
        elif face == faces.LONELY:
            faceEnum = PwnFace.LONELY
        elif face == faces.SAD:
            faceEnum = PwnFace.SAD
        elif face == faces.ANGRY:
            faceEnum = PwnFace.ANGRY
        elif face == faces.FRIEND:
            faceEnum = PwnFace.FRIEND
        elif face == faces.BROKEN:
            faceEnum = PwnFace.BROKEN
        elif face == faces.DEBUG:
            faceEnum = PwnFace.DEBUG
        elif face == faces.UPLOAD:
            faceEnum = PwnFace.UPLOAD
        elif face == faces.UPLOAD1:
            faceEnum = PwnFace.UPLOAD1
        elif face == faces.UPLOAD2:
            faceEnum = PwnFace.UPLOAD2

        self.set_face(faceEnum)

        # Handshakes
        handshakes = ui.get("shakes")

        shakesCurr = handshakes.split(" ")[0]
        shakesTotal = handshakes.split(
            " ")[1].replace(")", "").replace("(", "")

    def on_unload(self, ui):
        with ui._lock:
            logging.info(f"[{self.__class__.__name__}] plugin unloaded")

    def on_webhook(self, path, request):
        logging.info(f"[{self.__class__.__name__}] webhook pressed")
