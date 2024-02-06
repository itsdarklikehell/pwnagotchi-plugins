import os
import subprocess
import logging
from pwnagotchi import plugins
from flask import render_template_string
from pwnagotchi.ui.components import LabeledValue
from pwnagotchi.ui.view import BLACK

WEBSSH2_SERV = """
[Unit]
Description=Access Webssh2
After=default.target

[Service]
ExecStart=/bin/bash WebSSH2
Restart=always
User=pi
Group=pi

[Install]
WantedBy=default.target
"""

SERV_PATH = "/etc/systemd/system/webssh2.service"

TEMPLATE = """
{% extends "base.html" %}
{% block styles %}
{{ super() }}
<style>
#term-container {
    margin: 0;
    padding: 0;
    border: none;
}
</style>
{% endblock %}

{% block content %} 
    <div id="term-container">
        {% if request.remote_addr.startswith('10.0.0.') %}
            <iframe style="width:calc(100vw - 10px); height:calc(100vh - 47px);" id="term-iframe" src="http://10.0.0.2:2222/ssh/host/127.0.0.1?port=22&header=Pwnagotchir&headerBackground=red&tabStopWidth=100&fontSize=16" scrolling="no"></iframe>
        {% elif request.remote_addr.startswith('192.168.') %}
            <iframe style="width:calc(100vw - 10px); height:calc(100vh - 47px);" id="term-iframe" src="http://192.168.44.44:2222/ssh/host/127.0.0.1?port=22&header=Pwnagotchir&headerBackground=red&tabStopWidth=100&fontSize=16" scrolling="no"></iframe>
        {% endif %}
    </div>
{% endblock %}
"""


class WebSSH2Plugin(plugins.Plugin):
    __author__ = "NeonLightning"
    __version__ = "1.0.0"
    __license__ = "GPL3"
    __description__ = "WebSSH2 Access"

    def __init__(self):
        self.ready = False

    def on_loaded(self):
        logging.info("[Webssh2] plugin loading")
        if not os.path.exists(SERV_PATH):
            logging.info("[Webssh2] creating systemd unit file")
            file = open(SERV_PATH, "w")
            file.write(WEBSSH2_SERV)
            file.close()
            os.system("sudo systemctl enable webssh2.service")
            os.system("sudo systemctl start webssh2.service")

            # check if webssh2.service is running and listening on an IP address
            for i in range(12):
                output = subprocess.check_output(
                    ["systemctl", "status", "webssh2.service"]
                ).decode("utf-8")
                if "Active: active" in output and "listening on" in output:
                    ip_address = self.extract_ip_address(output)
                    if ip_address is not None:
                        self.ready = True
                        logging.info(
                            f"[Webssh2] service started successfully on {ip_address}"
                        )
                        return
                time.sleep(5)

            logging.error("[Webssh2] failed to start service")
        else:
            logging.info(
                "[Webssh2] systemd unit file already exists, skipping creation"
            )
            output = subprocess.check_output(
                ["systemctl", "is-active", "webssh2.service"]
            ).decode("utf-8")
            if not output.strip() == "active":
                os.system("sudo systemctl disable webssh2.service")
                file = open(SERV_PATH, "w")
                file.write(WEBSSH2_SERV)
                file.close()
                os.system("sudo systemctl enable webssh2.service")
                os.system("sudo systemctl start webssh2.service")

    def extract_ip_address(self, output):
        match = re.search(r"listening on (\S+)", output)
        if match:
            return match.group(1)
        return None

    def on_unload(self, ui):
        logging.info("[Webssh2] plugin unloading")
        os.system("sudo systemctl stop webssh2.service")
        os.system("sudo systemctl disable webssh2.service")
        os.system("sudo rm -f {}".format(SERV_PATH))
        logging.info("[Webssh2] plugin stopped")
        self.ready = False

    def on_webhook(self, path, request):
        return render_template_string(TEMPLATE)
