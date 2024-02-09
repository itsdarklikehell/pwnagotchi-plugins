# educational-purposes-exclusively.py

import os
from pwnagotchi.plugins import Plugin
import logging
import subprocess
import requests
import time
from reportlab.pdfgen import canvas
import datetime

READY = 0
STATUS = ""
NETWORK = ""
CHANNEL = 0


class EducationalPurposesOnly(Plugin):
    __author__ = "SgtStroopwafel, @nagy_craig , MaliosDark"
    __version__ = "1.0.15.2"
    __license__ = "GPL3"
    __description__ = "A plugin to automatically authenticate to known networks and perform internal network recon"
    __name__ = "EducationalPurposesOnly"
    __help__ = "A plugin to automatically authenticate to known networks and perform internal network recon"
    __dependencies__ = {
        "apt": ["none"],
        "pip": ["requests"],
    }
    __defaults__ = {
        "enabled": False,
    }

    def __init__(self):
        self.ready = False
        logging.debug(f"[{self.__class__.__name__}] plugin init")
        self.title = ""

    def on_loaded(self):
        global READY
        logging.info(f"[{self.__class__.__name__}] plugin loaded")
        READY = 1

    def display_text(self, text):
        global STATUS
        STATUS = text

    def on_ui_update(self, ui):
        global STATUS
        status_messages = []

        if STATUS == "rssi_low":
            ui.set("face", "(⊙_☉)")
            status_messages.append(
                "Signal strength of %s is currently too low to connect ..." % NETWORK
            )
            status_messages.append(
                f'Interface Status: {"Up" if "UP" in os.popen("ifconfig wlan0mon").read() else "Down"}'
            )
        elif STATUS == "home_detected":
            ui.set("face", "(╯°□°）╯︵ ┻━┻")
            ui.set("face", "(⚆_⚆)")
            status_messages.append("Found home network at %s ..." % NETWORK)
        elif STATUS == "switching_mon_off":
            ui.set("face", "(◔_◔)")
            ui.set("face", "(¬_¬)")
            status_messages.append("We're home! Pausing monitor mode ...")
        elif STATUS == "scrambling_mac":
            ui.set("face", "(¬‿¬)")
            status_messages.append(
                "Scrambling MAC address before connecting to %s ..." % NETWORK
            )
        elif STATUS == "associating":
            status_messages.append("Greeting the AP and asking for an IP via DHCP ...")
            ui.set("face", "(¬◡¬ )")
            ui.set("face", "( ¬◡¬)")
        elif STATUS == "associated":
            ui.set("face", "(¬‿¬)")
            status_messages.append("Home at last!")
            status_messages.append(f"Connected to {NETWORK} on channel {CHANNEL}.")
            current_mac = (
                os.popen("ifconfig wlan0mon | grep -o -E '([0-9a-fA-F]:?){2,6}'")
                .read()
                .strip()
            )
            status_messages.append(f"Current MAC Address: {current_mac}")
            status_messages.append("Performing network reconnaissance...")

        # Única llamada para actualizar el estado
        ui.set("status", "\n".join(status_messages))

    def _connect_to_target_network(self, network_name, channel, interface="wlan0mon"):
        global READY
        global STATUS
        global NETWORK
        global CHANNEL

        NETWORK = network_name
        logging.info(
            f"sending command to Bettercap to stop using wlan0mon on {interface}..."
        )
        STATUS = "switching_mon_off"
        requests.post(
            "http://127.0.0.1:8081/api/session",
            data='{"cmd":"wifi.recon off"}',
            auth=("pwnagotchi", "pwnagotchi"),
        )
        logging.info("ensuring all wpa_supplicant processes are terminated...")
        subprocess.Popen(
            f"systemctl stop wpa_supplicant; killall wpa_supplicant",
            shell=True,
            stdin=None,
            stdout=open("/dev/null", "w"),
            stderr=None,
            executable="/bin/bash",
        )
        time.sleep(10)
        logging.info(f"disabling monitor mode on {interface}...")
        subprocess.Popen(
            f"modprobe --remove brcmfmac; modprobe brcmfmac",
            shell=True,
            stdin=None,
            stdout=open("/dev/null", "w"),
            stderr=None,
            executable="/bin/bash",
        )
        time.sleep(10)
        # Runs this driver reload command again because sometimes it gets stuck the first time:
        subprocess.Popen(
            f"modprobe --remove brcmfmac; modprobe brcmfmac",
            shell=True,
            stdin=None,
            stdout=open("/dev/null", "w"),
            stderr=None,
            executable="/bin/bash",
        )
        time.sleep(10)
        logging.info(f"randomizing {interface} MAC address prior to connecting...")
        STATUS = "scrambling_mac"
        subprocess.Popen(
            f"macchanger -A {interface}",
            shell=True,
            stdin=None,
            stdout=open("/dev/null", "w"),
            stderr=None,
            executable="/bin/bash",
        )
        time.sleep(10)
        logging.info(
            f"setting hostname to a ^work dictionary word prior to connecting (for added stealth since their DHCP server will see this name)..."
        )
        subprocess.Popen(
            f'hostnamectl set-hostname $(grep "^work" /usr/share/dict/words | grep -v "s$" | sort -u | shuf -n 1))',
            shell=True,
            stdin=None,
            stdout=open("/dev/null", "w"),
            stderr=None,
            executable="/bin/bash",
        )
        time.sleep(5)
        logging.info(f"starting up {interface} again...")
        subprocess.Popen(
            f"ifconfig {interface} up",
            shell=True,
            stdin=None,
            stdout=open("/dev/null", "w"),
            stderr=None,
            executable="/bin/bash",
        )
        time.sleep(3)
        # This command runs multiple times because it sometimes doesn't work the first time:
        subprocess.Popen(
            f"ifconfig {interface} up",
            shell=True,
            stdin=None,
            stdout=open("/dev/null", "w"),
            stderr=None,
            executable="/bin/bash",
        )
        time.sleep(10)
        logging.info(f"setting {interface} channel to match the target...")
        STATUS = "associating"
        subprocess.Popen(
            f"iwconfig {interface} channel {channel}",
            shell=True,
            stdin=None,
            stdout=open("/dev/null", "w"),
            stderr=None,
            executable="/bin/bash",
        )
        subprocess.Popen(
            f"ifconfig {interface} up",
            shell=True,
            stdin=None,
            stdout=open("/dev/null", "w"),
            stderr=None,
            executable="/bin/bash",
        )
        time.sleep(10)
        logging.info(f"writing to wpa_supplicant.conf file...")
        with open("/tmp/wpa_supplicant.conf", "w") as wpa_supplicant_conf:
            wpa_supplicant_conf.write(
                f'ctrl_interface=DIR=/var/run/wpa_supplicant\nupdate_config=1\ncountry=GB\n\nnetwork={{\n\tssid="%s"\n\tpsk="%s"\n}}\n'
                % (network_name, self.options["home-password"])
            )
        logging.info(f"starting wpa_supplicant background process on {interface}...")
        subprocess.Popen(
            f"ifconfig {interface} up",
            shell=True,
            stdin=None,
            stdout=open("/dev/null", "w"),
            stderr=None,
            executable="/bin/bash",
        )
        subprocess.Popen(
            f"wpa_supplicant -u -s -c /tmp/wpa_supplicant.conf -i {interface} &",
            shell=True,
            stdin=None,
            stdout=open("/dev/null", "w"),
            stderr=None,
            executable="/bin/bash",
        )
        time.sleep(10)
        logging.info(f"connecting to wifi on {interface}...")
        subprocess.Popen(
            f"ifconfig {interface} up",
            shell=True,
            stdin=None,
            stdout=open("/dev/null", "w"),
            stderr=None,
            executable="/bin/bash",
        )
        subprocess.Popen(
            f"wpa_cli -i {interface} reconfigure",
            shell=True,
            stdin=None,
            stdout=open("/dev/null", "w"),
            stderr=None,
            executable="/bin/bash",
        )
        time.sleep(10)
        logging.info(
            f"trying to get an IP address on the network via DHCP on {interface}..."
        )
        subprocess.Popen(
            f"dhclient {interface}",
            shell=True,
            stdin=None,
            stdout=open("/dev/null", "w"),
            stderr=None,
            executable="/bin/bash",
        )
        time.sleep(10)

        # Nueva mejora: Registrar la conexión exitosa
        self._log_successful_connection(network_name)
        STATUS = "associated"
        READY = 1
        CHANNEL = channel  # Esta línea ya está presente al principio de la función
        NETWORK = network_name
        logging.info(
            f"sending command to Bettercap to stop using wlan0mon on {interface}..."
        )

    def _restart_monitor_mode(self):
        logging.info("Resuming wifi recon and monitor mode...")

        # Detener wpa_supplicant
        subprocess.run(["systemctl", "stop", "wpa_supplicant"])
        subprocess.run(["killall", "wpa_supplicant"])

        logging.info("Waiting for wpa_supplicant to stop...")
        time.sleep(10)

        # Recargar el controlador brcmfmac
        subprocess.run(["modprobe", "--remove", "brcmfmac"])
        subprocess.run(["modprobe", "brcmfmac"])
        logging.info("Reloading brcmfmac driver...")
        time.sleep(10)

        # Randomizar la dirección MAC de wlan0mon
        subprocess.run(["macchanger", "-A", "wlan0mon"])
        logging.info("Randomizing MAC address...")
        time.sleep(10)

        # Activar wlan0mon
        subprocess.run(["ifconfig", "wlan0mon", "up"])
        logging.info("Activating wlan0mon...")

        # Crear la interfaz wlan0mon
        subprocess.run(
            [
                "iw",
                "phy",
                '$(iw phy | head -1 | cut -d" " -f2)',
                "interface",
                "add",
                "wlan0mon",
                "type",
                "monitor",
            ]
        )
        subprocess.run(["ifconfig", "wlan0mon", "up"])
        logging.info("Creating and activating wlan0mon...")

        # Resumir wifi recon en Bettercap
        requests.post(
            "http://127.0.0.1:8081/api/session",
            data='{"cmd":"wifi.recon on"}',
            auth=("pwnagotchi", "pwnagotchi"),
        )
        logging.info("Resuming wifi recon in Bettercap...")

        logging.info("Wifi recon and monitor mode resumed.")

    def on_epoch(self, ui, agent, epoch, total_epochs):
        global READY
        global STATUS

        blinds = epoch["blind"]

        # If there are blinds, perform reconnection
        if blinds > 0:
            logging.info(f"Detected {blinds} blinds. Reconnecting to wlan0monmon...")
            self._restart_monitor_mode()

    def on_wifi_update(self, agent, access_points):
        global STATUS
        home_network = self.options["home-network"]

        for network in access_points:
            if network["hostname"] == home_network:
                signal_strength = network["rssi"]
                channel = network["channel"]
                logging.info(
                    "FOUND home network nearby on channel %d (rssi: %d)"
                    % (channel, signal_strength)
                )
                if signal_strength >= self.options["minimum-signal-strength"]:
                    logging.info("Starting association...")
                    self._connect_to_target_network(network["hostname"], channel)
                else:
                    logging.info(
                        "The signal strength is too low (%d) to connect."
                        % (signal_strength)
                    )
                    STATUS = "rssi_low"

    def _port_scan(self, target_ip):
        open_ports = []
        for port in range(1, 1025):  # Rango común de puertos
            command = f"timeout 1 bash -c 'echo >/dev/tcp/{target_ip}/{port}'"
            try:
                subprocess.run(command, shell=True, check=True)
                open_ports.append(port)
            except subprocess.CalledProcessError:
                pass
        logging.info(f"Open ports on {target_ip}: {open_ports}")

    # Función para generar un informe en PDF
    def _generate_report(self, file_path, content):
        with open(file_path, "w") as pdf_file:
            pdf = canvas.Canvas(pdf_file)
            pdf.drawString(72, 800, "Informe de Actividades")
            pdf.drawString(72, 780, content)
            pdf.save()

    # Notificaciones avanzadas
    def _send_notification(self, message, urgency="normal"):
        # Implementa notificaciones avanzadas aquí (por ejemplo, Pushbullet API).
        logging.info(f"Sending {urgency} notification: {message}")

    # Seguimiento de conexiones exitosas
    def _log_successful_connection(self, target_ip):
        logging.info(
            f"Successfully connected to {target_ip} at {datetime.datetime.now()}"
        )

    def on_unload(self, ui):
        with ui._lock:
            logging.info(f"[{self.__class__.__name__}] plugin unloaded")

    def on_webhook(self, path, request):
        logging.info(f"[{self.__class__.__name__}] webhook pressed")
