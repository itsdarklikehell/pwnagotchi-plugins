import pwnagotchi
import pwnagotchi.plugins as plugins
import logging
import traceback
import os
from os import fdopen, remove
import shutil
from shutil import move, copymode
from tempfile import mkstemp
from PIL import Image
import json
import toml
import csv
import _thread
from pwnagotchi import restart
from pwnagotchi.utils import save_config
from flask import abort, render_template_string
import requests
import subprocess
import re
import html

import pwnagotchi.plugins as plugins
import pwnagotchi.plugins.cmd
from pwnagotchi.plugins import toggle_plugin
import inspect

pwny_path = pwnagotchi.__file__
pwny_path = os.path.dirname(pwny_path)
pwnagotchi.root_path = pwny_path

ROOT_PATH = pwny_path

ONLINE_PATH = "https://raw.githubusercontent.com/V0r-T3x/Fancytools/main/fancytools.py"

# ROOT_PATH = '/usr/local/lib/python3.11/dist-packages/pwnagotchi'
FANCY_ROOT = os.path.dirname(os.path.realpath(__file__))
setattr(pwnagotchi, "fancy_root", FANCY_ROOT)

with open("%s/fancytools/sys/index.html" % (FANCY_ROOT), "r") as file:
    html_contents = file.read()
INDEX = html_contents


def www_check():
    try:
        # Use the ping command to check internet connectivity
        subprocess.run(["ping", "-c", "1", "8.8.8.8"], check=True)
        print("Pwnagotchi is connected to the internet.")
        return True
    except subprocess.CalledProcessError:
        print("Pwnagotchi is not connected to the internet.")
        return False


def load_config(file_path):
    try:
        with open(file_path, "r") as file:
            config_data = toml.load(file)
        return config_data
    except FileNotFoundError:
        print(f"Error: File not found - {file_path}")
        return None
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return None


def scan_folder(root_folder):
    folder_dict = {}

    for folder_name in os.listdir(root_folder):
        folder_path = os.path.join(root_folder, folder_name)

        if os.path.isdir(folder_path):
            config_path = os.path.join(folder_path, "config.toml")

            if os.path.exists(config_path):
                config_data = load_config(config_path)

                if config_data:
                    folder_dict[folder_name] = config_data
                    # folder_dict[folder_name]['info']['']

    return folder_dict


def serializer(obj):
    if isinstance(obj, set):
        return list(obj)
    raise TypeError


def copy_with_backup(src_path, dest_path):
    # Check if the source file exists
    if not os.path.exists(src_path):
        raise FileNotFoundError(f"The source file '{src_path}' does not exist.")

    # Check if the destination directory exists, create it if not
    dest_dir = os.path.dirname(dest_path)
    os.makedirs(dest_dir, exist_ok=True)

    # Check if the destination file already exists
    if os.path.exists(dest_path):
        # Check if a backup file with .original extension exists
        backup_path = dest_path + ".original"
        index = 1
        while os.path.exists(backup_path):
            backup_path = f"{dest_path}.original_{index}"
            index += 1
            logging.debug(backup_path)
        logging.debug(backup_path)
        # If no .original file found, create a backup with .original extension
        shutil.copy(dest_path, backup_path)

    # Copy the source file to the destination
    shutil.copy(src_path, dest_path)


def delete_restore(dest_path):
    # Check if the destination file exists
    if not os.path.exists(dest_path):
        raise FileNotFoundError(f"The destination file '{dest_path}' does not exist.")

    # Check if a backup file with .original extension exists
    backup_path = dest_path + ".original"

    # If a backup file exists, copy it back to the destination
    if os.path.exists(backup_path):
        shutil.copy(backup_path, dest_path)
        logging.debug(f"Restored '{dest_path}' from backup.")

        # Optionally, you can remove the backup file after restoring
        os.remove(backup_path)
        logging.debug(f"Removed backup file '{backup_path}'.")
    else:
        os.remove(dest_path)
        # Recursively check and delete empty parent folders
        folder_path = os.path.dirname(dest_path)
        while not os.listdir(folder_path):
            os.rmdir(folder_path)
            logging.debug(f"Removed empty folder '{folder_path}'.")
            folder_path = os.path.dirname(folder_path)


# function to backup all actual modified files to make a new install update
def dev_backup(config, dest_fold):
    if not config.get("pwnagotchi") and not config.get("system"):
        logging.debug("empty config files for dev backup")
    else:
        if config.get("pwnagotchi"):
            for path in config["pwnagotchi"]:
                target_path = ROOT_PATH + "/" + path
                back_path = "%s/%s" % (dest_fold, path)
                logging.debug(target_path + " >> " + back_path)
                copy_with_backup(target_path, back_path)

        if config.get("system"):
            for path in config["system"]:
                target_path = path
                back_path = "%s%s" % (dest_fold, path)
                logging.debug(target_path + " >> " + back_path)
                copy_with_backup(target_path, back_path)


def install(config):
    logging.debug("hello worlds")
    if config["info"]["default"]:
        tooltype = "default"
    else:
        tooltype = "custom"
    name = config["info"]["name"]

    logging.info("[FANCYTOOLS] starting " + config["info"]["name"] + " install")
    if not config["files"].get("pwnagotchi") and not config["files"].get("system"):
        logging.debug("No install files")
    else:
        if config["files"].get("pwnagotchi"):
            for path in config["files"]["pwnagotchi"]:
                target_path = "%s/fancytools/tools/%s/%s/files/%s" % (
                    FANCY_ROOT,
                    tooltype,
                    name,
                    path,
                )
                sys_path = "%s/%s" % (ROOT_PATH, path)
                logging.debug(target_path + " >> " + sys_path)
                copy_with_backup(target_path, sys_path)

        if config["files"].get("system"):
            for path in config["files"]["system"]:
                target_path = "%s/fancytools/tools/%s/%s/files%s" % (
                    FANCY_ROOT,
                    tooltype,
                    name,
                    path,
                )
                sys_path = path
                logging.debug(target_path + " >> " + sys_path)
                copy_with_backup(target_path, sys_path)

    if not config["commands"].get("install"):
        logging.debug("no install commands")
    else:
        for cmd in config["commands"]["install"]:
            logging.debug(cmd)
            formatted_cmd = eval(cmd)
            logging.debug(formatted_cmd)
            response = os.system(formatted_cmd)
            logging.debug(response)


def uninstall(config):
    if config["info"]["default"]:
        tooltype = "default"
    else:
        tooltype = "custom"
    name = config["info"]["name"]
    if name == "fancygotchi":
        logging.debug("rm %s/%s" % (ROOT_PATH, "ui/web/static/img"))
        os.system("rm %s/%s" % (ROOT_PATH, "ui/web/static/img"))
        logging.debug("load config: %s/%s" % (ROOT_PATH, "ui/theme/config.toml"))
        config = load_config("%s/%s" % (ROOT_PATH, "ui/themes/config.toml"))

    logging.info("[FANCYTOOLS] starting " + config["info"]["name"] + " install")

    logging.info("uninstall function start")
    if not config["commands"].get("uninstall"):
        logging.debug("no uninstall commands")
    else:
        for cmd in config["commands"]["uninstall"]:
            logging.debug(cmd)
            formatted_cmd = eval(cmd)
            logging.debug(formatted_cmd)
            response = os.system(formatted_cmd)
            logging.debug(response)

    if not config["files"].get("pwnagotchi") and not config["files"].get("system"):
        logging.debug("No install files")
    else:
        if config["files"].get("pwnagotchi"):
            for path in config["files"]["pwnagotchi"]:
                sys_path = "%s/%s" % (ROOT_PATH, path)
                logging.debug("delete: " + sys_path)
                delete_restore(sys_path)

        if config["files"].get("system"):
            for path in config["files"]["system"]:
                sys_path = path
                logging.debug("Delete: " + sys_path)
                delete_restore(sys_path)
    # if name == 'fancygotchi':
    #    os.system(f'rm -R {ROOT_PATH}/ui/themes')


def check_update(vers, path, online):
    nofile = False
    upd = None
    cversion = ""
    compared_version = ""
    if online:
        logging.debug("online check update")
        response = requests.get(path)
        if response.status_code == 200:
            lines = str(response.content)
        else:
            logging.debug(
                f"Failed to retrieve the file. Status code: {response.status_code}"
            )
            nofile = True
    else:
        logging.debug("local check update")
        if os.path.exists(path):
            with open(path, "r") as file:
                lines = file.read()
        else:
            nofile = True
    if not nofile:
        compared_version = re.search(r"(\d+\.\d+\.\d+)", lines)
        logging.debug("starting version comparaison")
        cversion = compared_version.groups(1)[0]
        com_v = cversion.split(".")
        local_v = vers.split(".")
        logging.debug(str(local_v) + " >> " + str(com_v))
        upd = False
        if local_v == com_v:
            logging.debug("same version")
        elif local_v < com_v:
            logging.debug("compared version is newer")
            upd = True
        elif local_v > com_v:
            logging.debug("local version is newer")

    return [upd, cversion]


def update(online):
    logging.info("[FANCYGOTCHI] The updater is starting, is online: %s" % (online))
    path_upd = "%s/fancygotchi/update" % (FANCY_ROOT)
    if online:  # <-- Download from the Git & define the update path
        URL = "https://github.com/V0r-T3x/fancygotchi/archive/refs/heads/main.zip"
        response = requests.get(URL)
        filename = "%s/%s" % (path_upd, URL.split("/")[-1])
        os.system("mkdir %s" % (path_upd))
        with open(filename, "wb") as output_file:
            output_file.write(response.content)
        shutil.unpack_archive(filename, path_upd)
    path_upd += "/fancygotchi-main"

    logging.info(
        "[FANCYGOTCHI] %s/fancygotchi.py ====> %s/fancygotchi.py"
        % (path_upd, FANCY_ROOT)
    )
    shutil.copyfile(
        "%s/fancygotchi.py" % (path_upd), "%s/fancygotchi.py" % (FANCY_ROOT)
    )

    uninstall(True)
    mod_path = "%s/fancytools/mod" % (FANCY_ROOT)
    logging.info("[FANCYGOTCHI] removing mod folder: %s" % (mod_path))
    os.system("rm -R %s" % (mod_path))
    deftheme_path = "%s/fancygotchi/theme/.default" % (FANCY_ROOT)
    logging.info("[FANCYGOTCHI] removing theme folder: %s" % (deftheme_path))
    os.system("rm -R %s" % (deftheme_path))
    sys_path = "%s/fancytools/sys" % (FANCY_ROOT)
    logging.info("[FANCYGOTCHI] removing sys folder: %s" % (sys_path))
    os.system("rm -R %s" % (sys_path))

    path_upd += "/fancygotchi"
    for root, dirs, files in os.walk(path_upd):
        for name in files:
            if not name in ["README.md", "readme.md"]:
                src_file = os.path.join(root, name)
                dst_path = "%s/%s" % (FANCY_ROOT, root.split("fancygotchi-main/")[-1])
                dst_file = "%s/%s" % (dst_path, name)
                logging.info("[FANCYGOTCHI] %s ~~~~> %s" % (src_file, dst_file))

                if not os.path.exists(dst_path):
                    os.makedirs(dst_path)
                shutil.copyfile(src_file, dst_file)

                # Check if the destination path exists and create it if it doesn't
                if not os.path.exists(dst_path):
                    os.makedirs(dst_path)

                # Copy the file to the destination path
                shutil.copyfile(src_file, dst_file)
    if online:
        path_upd = "%s/fancytools/update" % (FANCY_ROOT)
        logging.info(
            "[FANCYGOTCHI] removing the update temporary folder: %s" % (path_upd)
        )
        os.system("rm -R %s" % (path_upd))


def verify_config_files(config, ext=""):
    missing = []
    total_files = 0

    if not config.get("pwnagotchi") and not config.get("system"):
        # Skip verification if both sections are empty
        return missing, total_files

    if config.get("pwnagotchi"):
        for path in config["pwnagotchi"]:
            total_files += 1
            target_path = ROOT_PATH + "/" + path + ext
            if not os.path.exists(target_path):
                missing.append(target_path)

    if config.get("system"):
        for path in config["system"]:
            total_files += 1
            target_path = path + ext
            if not os.path.exists(target_path):
                missing.append(target_path)

    return missing, total_files


def verify_subprocess(subp):
    missing = []
    is_installed = 0

    for command in subp:
        try:
            subprocess.check_output(["which", command])
        except subprocess.CalledProcessError:
            logging.debug("[FANCYTOOLS] " + command + " is not installed")
            missing.append(command)
    if missing:
        is_installed = 0
    else:
        is_installed = 1

    return is_installed, missing


def verify_services(services_dict):
    missing_services = []
    is_installed = 1  # Assume all services are installed by default

    for services_list in services_dict:
        services = services_dict[services_list]
        for service in services:
            logging.debug(str(service["name"]))
            name = str(service["name"])

            # Search for service files recursively in /etc/systemd/system
            # service_files = find_service_files('/etc/systemd/system')
            service_files = []
            for root, dirs, files in os.walk("/etc/systemd/system"):
                for file in files:
                    if file.endswith(".service"):
                        service_files.append(os.path.join(root, file))

            # Check if the service file exists
            if not any(name in service_file for service_file in service_files):
                is_installed = 0

            if not is_installed:
                is_installed = 1
                initd_service_file = f"/etc/init.d/{name}"
                if not os.path.exists(initd_service_file):
                    is_installed = 0
            if not is_installed:
                logging.debug(
                    f"Service file for {name} not found in /etc/init.d or /etc/systemd/system."
                )
                missing_services.append(name)
    logging.debug(is_installed)
    return is_installed, missing_services


def is_service_running(services):
    logging.debug(services)

    # Check if services is empty
    if not services:
        logging.debug("No services provided")
        return None

    for service, details in services.items():
        for service_info in details:
            service_name = service_info["name"]
            try:
                # Check if the service is running using subprocess
                subprocess.check_output(
                    ["pgrep", service_name], stderr=subprocess.STDOUT
                )
            except subprocess.CalledProcessError:
                # If an error occurs (process not found), return False
                logging.debug("False")
                return False
    # If all services are running, return True
    logging.debug("True")
    return True


def srv_start(services):
    for service, details in services.items():
        for service_info in details:
            service_name = service_info["name"]
            try:
                # Start the service using subprocess
                subprocess.run(["service", service_name, "start"], check=True)
                logging.debug(f"Service {service_name} started successfully.")
            except subprocess.CalledProcessError as e:
                logging.debug(f"Error starting service {service_name}: {e}")
                # You can choose to handle the error as needed


def srv_stop(services):
    for service, details in services.items():
        for service_info in details:
            service_name = service_info["name"]
            try:
                # Start the service using subprocess
                subprocess.run(["service", service_name, "stop"], check=True)
                logging.debug(f"Service {service_name} started successfully.")
            except subprocess.CalledProcessError as e:
                logging.debug(f"Error starting service {service_name}: {e}")
                # You can choose to handle the error as needed


def verify_fancygotchi_status(config):
    logging.debug(config["fancygotchi"]["info"]["__version__"])
    missing_files, total_files = verify_config_files(config["fancygotchi"]["files"])
    logging.debug("missing files: " + str(len(missing_files)) + "/" + str(total_files))
    missing_backup, total_files = verify_config_files(
        config["fancygotchi"]["files"], ".original"
    )
    logging.debug(
        "missing backup: " + str(len(missing_backup)) + "/" + str(total_files)
    )

    fancy_status = 0

    if len(missing_files) == total_files:
        logging.info("[FANCYTOOLS] Fancygotchi is not installed")
        fancy_status = 0
    elif len(missing_files) == 0 and len(missing_backup) == total_files:
        logging.info("[FANCYTOOLS] Fancygotchi is installed and is embedded")
        fancy_status = 1
    elif len(missing_files) == 0 and len(missing_backup) != total_files:
        logging.info("[FANCYTOOLS] Fancygotchi is installed manually")
        fancy_status = 2
    # logging.debug(str(fancy_status))
    return fancy_status


def verify_tool_status(config):
    files = config["files"]
    subp = config["info"]["subprocess"]
    services = config["services"]
    is_installed = 1
    is_embed = False
    missing_subp = []
    missing_serv = []
    missing_files = []

    missing_files, total = verify_config_files(files)
    logging.debug(
        "[FANCYTOOLS] missing files: " + str(len(missing_files)) + "/" + str(total)
    )

    if subp:
        # logging.debug('verify if '+subp+' subprocess is installed')
        subp_status, missing_subp = verify_subprocess(subp)
    else:
        logging.debug("no subprocess")
        subp_status = 2

    if services:
        serv_status, missing_serv = verify_services(services)
    else:
        logging.debug("no services")
        serv_status = 2

    if total == 0 and subp_status == 2 and serv_status == 2:
        logging.debug("This tool doesn't need to be installed")
        is_embed = True
    else:
        if missing_files:
            logging.debug("Missing files:")
            for mfile in missing_files:
                logging.debug(mfile)
            is_installed = 0

        if missing_subp:
            logging.debug("Missing subprocesses:")
            for subpr in missing_subp:
                logging.debug(subpr)
            is_installed = 0

        if missing_serv:
            logging.debug("Missing services:")
            for serv in missing_serv:
                logging.debug(serv)
            is_installed = 0

    return is_installed, is_embed


class Fancytools(plugins.Plugin):
    __name__ = "FancyTools"
    __author__ = "@V0rT3x https://github.com/V0r-T3x"
    __version__ = "2023.12.2"
    __license__ = "GPL3"
    __description__ = "Fancygotchi and additional debug/dev tools"

    def __init__(self):
        self.ready = False
        self.mode = "MANU"

    def toggle_plugin(name, enable=True):
        logging.debug(toggle_plugin(name, enable))

    def tooltype(self, name):
        tooltype = ""
        if name in self.deftools:
            logging.debug("default tool")
            tooltype = "default"
        if name in self.custools:
            logging.debug("custom tool")
            tooltype = "custom"
        return tooltype

    def on_config_changed(self, config):
        self.config = config
        self.ready = True

    def on_ready(self, agent):
        self.mode = "MANU" if agent.mode == "manual" else "AUTO"

    def on_internet_available(self, agent):
        self.mode = "MANU" if agent.mode == "manual" else "AUTO"

    def on_loaded(self):
        logging.info("")
        logging.info("[FANCYTOOLS] Beginning Fancytools load")
        logging.info("[FANCYTOOLS]" + "=" * 20)
        # Fancytools cmd
        os.system("chmod +x %s/fancytools/sys/fancytools.py" % (FANCY_ROOT))
        os.system(
            "sudo ln -s %s/fancytools/sys/fancytools.py /usr/local/bin/fancytools"
            % (FANCY_ROOT)
        )

        # Each tool folders should be scanned
        # Each sub-folder become the tool name ID
        # Each tool dict have a place for the mod files (this can be use to verify if this is already installed) this is including special install/uninstall commands

        deftool_path = "%s/fancytools/tools/default/" % (FANCY_ROOT)
        custool_path = "%s/fancytools/tools/custom/" % (FANCY_ROOT)

        self.deftools = scan_folder(deftool_path)
        self.custools = scan_folder(custool_path)
        logging.info("[FANCYTOOLS] Default tools")
        logging.info("[FANCYTOOLS]" + "=" * 20)
        for tool in self.deftools:
            logging.info("[FANCYTOOLS] " + tool + " tool")
            self.deftools[tool]["info"]["is_embedded"] = False
            # logging.debug(f'{deftool_path}{tool}/frontend.html')
            file_path = os.path.join(
                FANCY_ROOT, "fancytools", "tools", "default", tool, "frontend.html"
            )
            self.deftools[tool]["info"]["html"] = ""
            if os.path.exists(file_path):
                with open(file_path, "r") as file:
                    html_contents = file.read()
                self.deftools[tool]["info"]["html"] = html_contents
            else:
                # Handle the case when the file does not exist
                print(f"Error: File '{file_path}' does not exist.")

            is_installed = 0
            self.deftools[tool]["info"]["default"] = True
            if tool == "fancygotchi":
                status = verify_fancygotchi_status(self.deftools)
                if status == 1:
                    self.deftools[tool]["info"]["is_embedded"] = True
                if status == 1 or status == 2:
                    is_installed = 1
                    self.deftools[tool]["info"]["is_installed"] = True
                else:
                    is_installed = 0
            else:
                is_installed, is_embed = verify_tool_status(self.deftools[tool])
                self.deftools[tool]["info"]["is_embedded"] = is_embed

            # adding the is_installed to the deftools[tool]['info']['installed']
            if is_installed == 0:
                logging.info("[FANCYTOOLS] tool need install")
            else:
                logging.info("[FANCYTOOLS] tool don't need install")
            self.deftools[tool]["info"]["is_installed"] = is_installed
            logging.debug(tool + " : " + str(self.deftools[tool]["services"]))
            logging.info("[FANCYTOOLS]" + "=" * 20)

        logging.info("[FANCYTOOLS] Custom tools")
        logging.info("[FANCYTOOLS]" + "=" * 20)
        for tool in self.custools:
            with open(
                "%s/fancytools/tools/default/%s/frontend.html" % (FANCY_ROOT, tool), "r"
            ) as file:
                html_contents = file.read()
            self.deftools[tool]["info"]["html"] = html_contents
            logging.info("[FANCYTOOLS] " + tool + " tool")
            is_installed, is_embed = verify_tool_status(self.custools[tool])
            self.deftools[tool]["info"]["is_embedded"] = is_embed
            self.deftools[tool]["info"]["default"] = False
            logging.debug(is_installed)
            # adding the is_installed to the deftools[tool]['info']['installed']
            if is_installed == 0:
                logging.info("[FANCYTOOLS] tool need install")
            else:
                logging.info("[FANCYTOOLS] tool don't need install")
            self.deftools[tool]["info"]["is_installed"] = is_installed
            logging.debug(
                tool + " : " + str(self.custools[tool]["info"]["is_installed"])
            )
            logging.info("[FANCYTOOLS]" + "=" * 20)

            # linking the local path deftools[tool]['info']['local_path']

        logging.info("[FANCYTOOLS] Ending Fancytools load")

    def on_unload(self, ui):
        os.system("rm /usr/local/bin/fancytools")
        # logging.debug('rm /usr/local/bin/fancytools')
        logging.info("[FANCYTOOLS] Fancytools unloaded")

    def on_webhook(self, path, request):
        # logging.info(request.remote_addr)
        if not self.ready:
            return "Plugin not ready"

        deftoold = self.deftools
        is_run = {}
        for tool in deftoold:
            content = deftoold[tool]["info"]["html"]

            content_result = render_template_string(
                content, deftools=self.deftools[tool]
            )
            logging.debug(content_result)
            deftoold[tool]["info"]["html"] = content_result
            srvs = deftoold[tool]["services"]
            logging.debug(srvs)
            is_run = is_service_running(srvs)
            logging.debug(is_run)
            deftoold[tool]["info"]["is_run"] = is_run

        if request.method == "GET":
            if path == "/" or not path:
                # pwnagotchi.fancy_change = True
                "
)
                tools info and process needed:
                -----------------------------
                is it installed?
                if installed
                    uninstall button
                    check_update button
                if installed and embedded
                    no button
                if not installed
                    install button

                if services
                    on or off service button


                "
)
                title = os.path.basename(__file__)[:-3]
                logging.debug(title)

                logging.debug(self.deftools)
                return render_template_string(INDEX, title=title, deftools=deftoold)

        elif request.method == "POST":
            logging.debug("WebUI subpath: " + path)
            if path == "devbackup":
                try:
                    jreq = request.get_json()
                    folder = json.loads(json.dumps(jreq))
                    fancybu = "%s/fancybackup/" % (FANCY_ROOT)
                    dest = "%s%s" % (fancybu, str(folder["response"]))
                    if not os.path.exists(fancybu):
                        os.system("mkdir %s" % (dest))
                    if not os.path.exists(dest):
                        os.system("mkdir %s" % (dest))
                    dev_backup(self.deftools["fancygotchi"]["files"], dest)
                    return "success"
                except Exception as ex:
                    logging.error(ex)
                    logging.error(traceback.format_exc())
                    return "dev backup error", 500

            elif path == "install":
                try:
                    jreq = request.get_json()
                    data = json.loads(json.dumps(jreq))
                    name = data["name"]
                    logging.debug(name)
                    alltools = {**self.deftools, **self.custools}
                    logging.debug(alltools[name])
                    install_dict = alltools[name]
                    install(install_dict)
                    _thread.start_new_thread(restart, (self.mode,))
                    # logging.info(str(request.get_json()))
                    return "success"
                except Exception as ex:
                    logging.error(ex)
                    return "install error", 500

            elif path == "srv_start":
                try:
                    jreq = request.get_json()
                    data = json.loads(json.dumps(jreq))
                    name = data["name"]
                    logging.debug(name)
                    alltools = {**self.deftools, **self.custools}
                    logging.debug(alltools[name])
                    srv_dict = alltools[name]["services"]
                    srv_start(srv_dict)
                    # _thread.start_new_thread(restart, (self.mode,))
                    # logging.info(str(request.get_json()))
                    return "success"
                except Exception as ex:
                    logging.error(ex)
                    return "install error", 500

            elif path == "srv_stop":
                try:
                    jreq = request.get_json()
                    data = json.loads(json.dumps(jreq))
                    name = data["name"]
                    logging.debug(name)
                    alltools = {**self.deftools, **self.custools}
                    logging.debug(alltools[name])
                    srv_dict = alltools[name]["services"]
                    srv_stop(srv_dict)
                    # _thread.start_new_thread(restart, (self.mode,))
                    # logging.info(str(request.get_json()))
                    return "success"
                except Exception as ex:
                    logging.error(ex)
                    return "install error", 500

            elif path == "uninstall":
                try:
                    jreq = request.get_json()
                    data = json.loads(json.dumps(jreq))
                    name = data["name"]
                    logging.debug(name)
                    alltools = {**self.deftools, **self.custools}
                    logging.debug("before uninstall")
                    uninstall(alltools[name])
                    _thread.start_new_thread(restart, (self.mode,))
                    # logging.info(str(request.get_json()))
                    return "success"
                except Exception as ex:
                    logging.error(ex)
                    return "install error", 500

            elif path == "check_update":
                try:
                    jreq = request.get_json()
                    data = json.loads(json.dumps(jreq))
                    name = data["name"]
                    online = data["online"]
                    alltools = {**self.deftools, **self.custools}
                    installed_version = alltools[name]["info"]["__version__"]
                    if online:
                        ckpath = alltools[name]["info"]["online_path"]
                    else:
                        ckpath = "%s/fancytools/tools/update/%s/config.toml" % (
                            FANCY_ROOT,
                            name,
                        )
                    if not ckpath:
                        logging.debug("no tool with this name")
                        return
                    else:
                        logging.debug(ckpath)
                    is_update = check_update(installed_version, ckpath, data["online"])
                    upd = "%s,%s" % (is_update[0], is_update[1])
                    return upd
                except Exception as ex:
                    logging.error(ex)
                    return "update check error, check internet connection", 500

            elif path == "online_update":
                try:
                    update(True)
                    _thread.start_new_thread(restart, (self.mode,))
                    logging.info(str(request.get_json()))
                    return "success"
                except Exception as ex:
                    logging.error(ex)
                    return "update error", 500

            elif path == "local_update":
                try:
                    update(False)
                    _thread.start_new_thread(restart, (self.mode,))
                    logging.info(str(request.get_json()))
                    return "success"
                except Exception as ex:
                    logging.error(ex)
                    return "update error", 500
        abort(404)
