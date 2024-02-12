import logging
import subprocess
import time
import pwnagotchi.plugins as plugins
import RPi.GPIO as GPIO


class lcdhatcontrols(plugins.Plugin):
    __GitHub__ = ""
    __author__ = "(edited by: itsdarklikehell bauke.molenaar@gmail.com), NeonLightning"
    __version__ = "0.0.2"
    __license__ = "GPL3"
    __description__ = "lcdhat controls"
    __name__ = "lcdhatcontrols"
    __help__ = "lcdhat controls"
    __dependencies__ = {
        "apt": ["none"],
        "pip": ["scapy"],
    }
    __defaults__ = {
        "enabled": False,
    }

    KEY_PRESS_PIN = 13
    KEY_DOWN_PIN = 19
    KEY1_PIN = 21
    KEY2_PIN = 20
    KEY3_PIN = 16
    DEBOUNCE_DELAY = 0.05
    pluginloc = "/home/pi/custom_plugins/fix_brcmf_plugin.py"

    def __init__(self):
        self.ready = False
        logging.debug(f"[{self.__class__.__name__}] plugin init")
        self.title = ""
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.KEY_PRESS_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(self.KEY_DOWN_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(self.KEY1_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(self.KEY2_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(self.KEY3_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

    @staticmethod
    def get_input(pin):
        return not GPIO.input(pin)

    def on_loaded(self):
        logging.info("[controls] loaded")
        self.loaded = True
        button_states = [False, False, False, False, False]
        last_press_times = [0.0, 0.0, 0.0, 0.0, 0.0]
        logging.info(f"[{self.__class__.__name__}] plugin loaded")
        while self.loaded:
            time.sleep(0.2)
            button_states[0] = self.get_input(self.KEY_PRESS_PIN)
            button_states[1] = self.get_input(self.KEY1_PIN)
            button_states[2] = self.get_input(self.KEY2_PIN)
            button_states[3] = self.get_input(self.KEY3_PIN)
            button_states[4] = self.get_input(self.KEY_DOWN_PIN)
            current_time = time.monotonic()

            if button_states[0]:
                if ((current_time - last_press_times[4]) >= self.DEBOUNCE_DELAY) and (
                    (current_time - last_press_times[0]) >= self.DEBOUNCE_DELAY
                ):
                    last_press_times[0] = current_time
                    if button_states[1]:
                        logging.info("Rebooting (auto)")
                        subprocess.run(["sudo", "touch", "/root/.pwnagotchi-auto"])
                        subprocess.run(["sudo", "reboot"])
                    elif button_states[2]:
                        logging.info("Shutting down")
                        subprocess.run(["sudo", "shutdown", "-h", "now"])
                    elif button_states[3]:
                        logging.info("Resetting service (auto)")
                        subprocess.run(["sudo", "touch", "/root/.pwnagotchi-auto"])
                        subprocess.run(
                            ["sudo", "systemctl", "restart", "pwnagotchi.service"]
                        )
                    else:
                        logging.info("Resending telegram QR codes")
                        subprocess.run(["sudo", "rm", "/root/.qrlist"])
            elif button_states[4]:
                if ((current_time - last_press_times[4]) >= self.DEBOUNCE_DELAY) and (
                    (current_time - last_press_times[0]) >= self.DEBOUNCE_DELAY
                ):
                    last_press_times[4] = current_time
                    if button_states[3]:
                        logging.info("Showing the light.")
                        subprocess.run(["sudo", "python3", self.pluginloc])
                    else:
                        pass
            else:
                last_press_times[0] = 0.0
                last_press_times[4] = 0.0

    def on_unloaded(self, ui):
        with ui._lock:
            logging.info(f"[{self.__class__.__name__}] plugin unloaded")
            self

    def on_webhook(self, path, request):
        logging.info(f"[{self.__class__.__name__}] webhook pressed")
