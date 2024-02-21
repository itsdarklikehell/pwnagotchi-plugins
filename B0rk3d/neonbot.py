# Setup
###########################################################################
# right now depends on the output of wpa-sec or onlinehashcrack until i can
# find a better solution.
# add these three lines to config and fill in bot_token and chat_id
# main.plugins.neonbot.enabled = false
# main.plugins.neonbot.bot_token = ""
# main.plugins.neonbot.chat_id = ""
# sudo pip3 install python-telegram-bot==13.15 qrcode tomli_w
# bot token add @BotFather and setup your bot. it will give you your token
# chat id add @RawDataBot and find chat id
import pwnagotchi, logging, os, qrcode, csv, html, subprocess, random, hashlib, time, re, urllib.request, glob, shutil, json, telegram.error
import pwnagotchi.plugins as plugins
from itertools import islice
from PIL import Image, ImageDraw, ImageFont
from telegram.ext import CommandHandler, Updater, CallbackContext, MessageHandler, Filters
from pwnagotchi import config

class neonbot(plugins.Plugin):
    __author__ = 'NeonLightning'
    __version__ = '0.8.0'
    __license__ = 'GPL3'
    __description__ = 'Telegram QR and control bot.'

    def __init__(self):
        self.qrlist_path = "/root/.qrlist"
        self.qrcode_dir = '/root/qrcodes/'
        self.locdata_path = '/root/handshakes/'
        self.possibleExt = ['.2500', '.16800', '.22000', '.pcap']
        self.file_paths = {
            'config.toml': '/etc/pwnagotchi/config.toml',
            'fingerprint': '/etc/pwnagotchi/fingerprint',
            'id_rsa': '/etc/pwnagotchi/id_rsa',
            'id_rsa.pub': '/etc/pwnagotchi/id_rsa.pub',
            'tweak_view.json': '/etc/pwnagotchi/tweak_view.json',
            'testfile': '/etc/pwnagotchi/testfile'
        }
        self.bot_token = None
        self.chat_id = None
        self.updater = None
        self.bot_running = False
        self.all_bssid = []
        self.all_ssid = []
        self.all_passwd = []
        self.file_list = []

    def _startstopbot(self):
        try:
            if self._is_internet_available():
                if not self.bot_running:
                    logging.info("[neonbot] Bot started.")
                    self.bot_running = True
                    self.updater.start_polling()
                    self.updater.bot.send_message(chat_id=self.chat_id, text="Bot started due to internet availability.")
            else:
                if self.bot_running:
                    try:
                        self.updater.stop()
                        while self.updater.is_alive():
                            time.sleep(0.1)
                    except telegram.error.Conflict as conflict_error:
                        logging.warning(f"[neonbot] Conflict error when stopping the bot: {conflict_error}")
                    logging.info("[neonbot] Bot stopped due to no internet connectivity.")
                    self.bot_running = False
        except ConnectionResetError as e:
            logging.error(f"[neonbot] Connection reset error: {e}")
        except telegram.error.Conflict as conflict_error:
            logging.warning(f"[neonbot] Conflict error: {conflict_error}")
            if self.bot_running:
                try:
                    self.updater.stop()
                    while self.updater.is_alive():
                        time.sleep(0.1)
                except Exception as stop_error:
                    logging.error(f"[neonbot] Error stopping the previous instance: {stop_error}")
            logging.info("[neonbot] Bot stopped due to conflict error.")
            self.bot_running = False
        except Exception as e:
            logging.error(f"[neonbot] An error occurred: {e}")

    def _qr_generation(self, update, context):
        try:
            self._read_wpa_sec_file()
        except FileNotFoundError:
            return
        try:
            self._read_onlinehashcrack_file()
        except FileNotFoundError:
            return
        for bssid, ssid, password in zip(self.all_bssid, self.all_ssid, self.all_passwd):
            if not os.path.exists(self.qrcode_dir):
                os.makedirs(self.qrcode_dir)
            png_filepath = os.path.join(f"{self.qrcode_dir}{ssid}-{password}-{bssid.lower().replace(':', '')}.png")
            filename = f"{ssid}-{password}-{bssid.lower().replace(':', '')}.png"
            if os.path.exists(png_filepath):
                continue
            if os.path.exists(self.qrlist_path):
                with open(self.qrlist_path, 'r') as qrlist_file:
                    qrlist = qrlist_file.read().splitlines()
                    if filename in qrlist:
                        continue
            qr_data = f"WIFI:T:WPA;S:{html.escape(ssid)};P:{html.escape(password)};;"
            qr_code = qrcode.QRCode(
                version=None,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            qr_code.add_data(qr_data)
            qr_code.make(fit=True)
            try:
                if os.path.exists(self.qrlist_path):
                    with open(self.qrlist_path, 'r') as qrlist_file:
                        qrlist = qrlist_file.read().splitlines()
                        if png_filepath in qrlist:
                            continue
                else:
                    open(self.qrlist_path, 'w+').close()
                img = qr_code.make_image(fill_color="yellow", back_color="black")
                img.save(png_filepath)
            except Exception as e:
                logging.error(f"[neonbot] something went wrong generating QR code for {ssid}-{password}-{bssid.lower().replace(':', '')}: {e}")

    def _is_internet_available(self):
        try:
            urllib.request.urlopen('https://www.google.com', timeout=1)
            return True
        except urllib.request.URLError:
            return False
        
    def _read_wpa_sec_file(self):
        wpa_sec_filepath = '/root/handshakes/wpa-sec.cracked.potfile'
        try:
            with open(wpa_sec_filepath, 'r+', encoding='utf-8') as f:
                for line_f in f:
                    pwd_f = line_f.split(':')
                    self.all_passwd.append(str(pwd_f[-1].rstrip('\n')))
                    self.all_bssid.append(str(pwd_f[0]))
                    self.all_ssid.append(str(pwd_f[-2]))
        except:
            pass

    def _read_onlinehashcrack_file(self):
        onlinehashcrack_filepath = '/root/handshakes/onlinehashcrack.cracked'
        try:
            with open(onlinehashcrack_filepath, 'r+', encoding='utf-8') as h:
                reader = csv.DictReader(h)
                for line_h in reader:
                    try:
                        pwd_h = str(line_h['password'])
                        bssid_h = str(line_h['BSSID'])
                        ssid_h = str(line_h['ESSID'])
                        if pwd_h and bssid_h and ssid_h:
                            self.all_passwd.append(pwd_h)
                            self.all_bssid.append(bssid_h)
                            self.all_ssid.append(ssid_h)
                    except csv.Error as e:
                        continue
                h.close()
        except Exception as e:
            logging.error(f"[neonbot] Encountered a problem in onlinehashcrack.cracked: {str(e)}")

    def _get_cpu_usage(self):
        try:
            cpu_output = subprocess.check_output("grep 'cpu ' /proc/stat", shell=True, universal_newlines=True)
            cpu_fields = cpu_output.split()
            total_time = sum(map(int, cpu_fields[1:]))
            idle_time = int(cpu_fields[4])
            usage = (1 - idle_time / total_time) * 100
            return int(usage)
        except Exception as e:
            return -1

    def _get_memory_usage(self):
        try:
            mem_output = subprocess.check_output("free -m", shell=True, universal_newlines=True)
            lines = mem_output.split('\n')
            mem_info = lines[1].split()
            total_mem = int(mem_info[1])
            used_mem = int(mem_info[2])
            mem_usage = (used_mem / total_mem) * 100
            return int(mem_usage)
        except Exception as e:
            return -1

    def _get_cpu_temperature(self):
        try:
            temp_output = subprocess.check_output("cat /sys/class/thermal/thermal_zone0/temp", shell=True, universal_newlines=True)
            temperature = int(temp_output) / 1000
            return temperature
        except Exception as e:
            return -1

    def _get_ipv4_address(self, interface):
        try:
            ip_output = subprocess.check_output(f"ifconfig {interface}", shell=True, universal_newlines=True)
            ip_address = re.search(r'inet\s+(\d+\.\d+\.\d+\.\d+)', ip_output)
            if ip_address:
                return ip_address.group(1)
            return "N/A"
        except Exception as e:
            return "N/A"

    def _composite_text_on_background(self, output_text, output_image_path):
        default_background = "/home/pi/custom_plugins/default_background.png"
        if not os.path.exists(default_background):
            with Image.new('RGB', (250, 122), (128, 0, 128)) as img:
                img.save(default_background)
        with Image.open(default_background) as img:
            draw = ImageDraw.Draw(img)
            font_path = '/home/pi/custom_plugins/DejaVuSansMono.ttf'
            font_size = 14
            font = ImageFont.truetype(font_path, font_size)
            text_x = 10
            text_y = 20
            draw.text((text_x, text_y), output_text, font=font, fill=(0,0,0))
            img.save(output_image_path)
            img.close()
    
    def _send_output(self, update, context, output_lines, max_lines):
        if len(output_lines) <= 50:
            output_text = "".join(output_lines)
            context.bot.send_message(chat_id=self.chat_id, text=f"Command Output:\n{output_text}")
        else:
            context.bot.send_message(chat_id=self.chat_id, text="Output longer than 50 lines.")
            if len(output_lines) <= max_lines:
                output_text = "".join(output_lines)
            else:
                output_text = "".join(output_lines[:max_lines])
                with open('/home/pi/output.txt', 'w') as output_file:
                    output_file.write("\n".join(line.rstrip() for line in output_lines[:max_lines]))
                context.bot.send_document(chat_id=self.chat_id, document=open('/root/output.txt', 'rb'))
                os.remove('/home/pi/output.txt')

    def _display_files(self, update, context):
        file_list = sorted([f for f in os.listdir(self.locdata_path) if f.endswith(tuple(self.possibleExt))])
        if file_list:
            chunk_size = 30
            num_files = len(file_list)
            num_chunks = -(-num_files // chunk_size)
            for i in range(num_chunks):
                start = i * chunk_size
                end = (i + 1) * chunk_size
                files_chunk = file_list[start:end]
                file_list_text = "\n".join([f"{start + j + 1}. {file_name}" for j, file_name in enumerate(files_chunk)])
                message = f"Files available ({start + 1}-{min(start + chunk_size, num_files)} of {num_files}):\n{file_list_text}"
                context.bot.send_message(chat_id=update.effective_chat.id, text=message)
        else:
            update.message.reply_text("No files found.")

    def _send_file(self, update: Updater, file_number: int) -> None:
        file_list = sorted([f for f in os.listdir(self.locdata_path) if f.endswith(tuple(self.possibleExt))])
        if file_list and 0 < file_number <= len(file_list):
            file_to_send = os.path.join(self.locdata_path, file_list[file_number - 1])
            with open(file_to_send, 'rb') as file:
                update.message.reply_document(document=file)
        else:
            update.message.reply_text("Invalid file number. Please choose a valid file number.")
            

    def handle_handshake(self, update, context):
        args = context.args
        if args:
            try:
                file_number = int(args[0])
                self._send_file(update, file_number)
            except (ValueError, IndexError):
                self._display_files(update, context)
        else:
            self._display_files(update, context)

    def screencap_command(self, update, context):
        photo_path = '/var/tmp/pwnagotchi/pwnagotchi.png'
        with Image.open(photo_path) as img:
            img = img.resize((img.width * 2, img.height * 2), Image.ANTIALIAS)
            temp_path = '/var/tmp/pwnagotchi/resized_pwnagotchi.png'
            img.save(temp_path)
        with open(temp_path, 'rb') as photo_file:
            context.bot.send_photo(chat_id=update.message.chat_id, photo=photo_file)
        os.remove(temp_path)

    def stats_command(self, update, context):
        args = context.args
        output_image_path = "/root/stats.png"
        cpu = self._get_cpu_usage()
        memory = self._get_memory_usage()
        temperature = self._get_cpu_temperature()
        wlan0_ip = self._get_ipv4_address("wlan0")
        usb0_ip = self._get_ipv4_address("usb0")
        eth0_ip = self._get_ipv4_address("eth0")
        bnep0_ip = self._get_ipv4_address("bnep0")
        handshake_dir = "/root/handshakes/"
        count = len([name for name in os.listdir(handshake_dir) if os.path.isfile(os.path.join(handshake_dir, name))])
        with open('/proc/uptime', 'r') as f:
            uptime_seconds = float(f.readline().split()[0])
            uptime_minutes = uptime_seconds / 60
            uptime_hours = int(uptime_minutes // 60)
            uptime_remaining_minutes = int(uptime_minutes % 60)
        composite_output_text = f"Handshakes: {count}\nUptime: {uptime_hours}hr and {uptime_remaining_minutes}min\nCPU:{cpu}%  Mem:{memory}%\nCPU:{temperature:.0f}°\nETH0:{eth0_ip}\nUSB0:{usb0_ip}\nWLN0:{wlan0_ip}\nBT :{bnep0_ip}"
        if 'image' in args:
            result = self._composite_text_on_background(composite_output_text, output_image_path)
            if result == -1:
                context.bot.send_message(chat_id=self.chat_id, text="Error generating the stats image.")
            else:
                with open(output_image_path, 'rb') as image_file:
                    context.bot.send_photo(chat_id=self.chat_id, photo=image_file)
        else:
            context.bot.send_message(chat_id=self.chat_id, text=composite_output_text)

    def genqrcodes_command(self, update, context):
        self._qr_generation(update, context)
        context.bot.send_message(chat_id=self.chat_id, text="QR codes generated successfully!")

    def important_command(self, update, context):
        super_secret_seed = int(time.time()) * 42 % 1001
        random_number = random.randint(super_secret_seed, super_secret_seed + 1000)
        hash_object = hashlib.sha256(str(random_number).encode())
        hex_dig = hash_object.hexdigest()
        reversed_hex = hex_dig[::-1]
        shuffled_hex = ''.join(random.sample(reversed_hex, len(reversed_hex)))
        for _ in range(len(shuffled_hex)):
            shuffled_hex = shuffled_hex[1:] + shuffled_hex[0]
        for i in range(len(shuffled_hex)):
            if i % 2 == 0:
                shuffled_hex = shuffled_hex[:i] + shuffled_hex[i].upper() + shuffled_hex[i+1:]
        result = sum(int(digit, 16) for digit in shuffled_hex)
        if result % 2 == 0:
            response = "It Does Something."
        else:
            response = "It Does Nothing."
        context.bot.send_message(chat_id=self.chat_id, text=response)

    def run_command(self, update, context):
        if update.message is None:
            context.bot.send_message(chat_id=self.chat_id, text="This command must be invoked with a message.")
            return
        args = context.args
        if args:
            command = " ".join(args)
            context.bot.send_message(chat_id=self.chat_id, text=f"Running command: {command}")
            try:
                os.chdir('/home/pi')
                result = subprocess.Popen(
                    f"sudo -u pi {command}",
                    shell=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    bufsize=1,
                    universal_newlines=True,
                )
                output_lines = []
                max_lines = 1000
                line_count = 0
                for line in iter(result.stdout.readline, ''):
                    if line_count < max_lines:
                        output_lines.append(line)
                    line_count += 1
                    if line_count > max_lines:
                        break
                result.stdout.close()
                self._send_output(update, context, output_lines, max_lines)
            except subprocess.TimeoutExpired:
                self._send_output(update, context, output_lines, max_lines)
                context.bot.send_message(chat_id=self.chat_id, text="Command execution timed out.")
            except Exception as e:
                context.bot.send_message(chat_id=self.chat_id, text=f"Error executing command: {str(e)}")
            finally:
                os.chdir('/tmp')
        else:
            context.bot.send_message(chat_id=self.chat_id, text="Usage: /command <command> [arguments]")

    def restart_command(self, update, context):
        args = context.args
        logging.info("[neonbot] restarting pwny")
        context.bot.send_message(chat_id=self.chat_id, text="[neonbot] restarting pwny")
        if args and "M" in args:
            subprocess.run(["sudo", "systemctl", "restart", "pwnagotchi"])
        else:
            subprocess.run(["sudo", "touch", "/root/.pwnagotchi-auto"])
            subprocess.run(["sudo", "systemctl", "restart", "pwnagotchi"])

    def reboot_command(self, update, context):
        args = context.args
        logging.info("[neonbot] rebooting")
        context.bot.send_message(chat_id=self.chat_id, text="[neonbot] rebooting")
        if args and "M" in args:
            subprocess.run(["sudo", "reboot"])
        else:
            subprocess.run(["sudo", "touch", "/root/.pwnagotchi-auto"])
            subprocess.run(["sudo", "shutdown", "-r", "now"])

    def shutdown_command(self, update, context):
        args = context.args
        logging.info("[neonbot] shutting down")
        context.bot.send_message(chat_id=self.chat_id, text="[neonbot] shutting down")
        if args and "M" in args:
            subprocess.run(["sudo", "shutdown", "-h", "now"])
        else:
            subprocess.run(["sudo", "touch", "/root/.pwnagotchi-auto"])
            subprocess.run(["sudo", "shutdown", "-h", "now"])
            
    def send_files_command(self, update, context):
        if len(context.args) > 0:
            file_name_requested = context.args[0]
        else:
            context.bot.send_message(chat_id=update.effective_chat.id, text="Please specify a file name.")
            return
        if file_name_requested in self.file_paths:
            file_path = self.file_paths[file_name_requested]
            if os.path.exists(file_path):
                context.bot.send_document(chat_id=update.effective_chat.id, document=open(file_path, 'rb'))
            else:
                context.bot.send_message(chat_id=update.effective_chat.id, text=f"Sorry, {file_name_requested} is not available.")
        else:
            context.bot.send_message(chat_id=update.effective_chat.id, text=f"Sorry, {file_name_requested} is not allowed.")
            
    def receive_files_command(self, update, context):
        if update.message.document:
            file_id = update.message.document.file_id
            file_name = update.message.document.file_name

            # Check if the received file name is allowed
            if file_name in self.file_paths:
                file_path = self.file_paths[file_name]
                file_obj = context.bot.get_file(file_id)
                file_obj.download(file_path)
                context.bot.send_message(chat_id=self.chat_id, text=f"Received and saved {file_name} to {file_path}")
            else:
                filenames = list(self.file_paths.keys())
                context.bot.send_message(chat_id=self.chat_id, text=f"Only {filenames} Are accepted.")

    def qr_files(self, update, context):
        args = context.args
        idx_start = 1
        data = None
        if args and args[0].strip():
            try:
                selected_number = int(args[0])
                if 1 <= selected_number <= len(os.listdir(self.qrcode_dir)):
                    selected_file = os.listdir(self.qrcode_dir)[selected_number - 1]
                    ssid_n_pass = selected_file.rsplit('-', 1)[-2]
                    bssid = selected_file.rsplit('-', 1)[-1].rsplit('.', 1)[0].lower().replace(':', '')
                    with open(f"{self.qrcode_dir}{selected_file}", 'rb') as f:
                        caption = f"^^^ {ssid_n_pass}"
                        geojson_files = glob.glob(f"/root/handshakes/*_{bssid}.gps.json")
                        geojson_files += glob.glob(f"/root/handshakes/*_{bssid}.geo.json")
                        if geojson_files:
                            geojson_file = geojson_files[0]
                            data = json.load(open(geojson_file, 'r'))
                            if data is not None:
                                if 'Latitude' in data and 'Longitude' in data:
                                    lat = data['Latitude']
                                    lng = data['Longitude']
                                else:
                                    lat = data.get('location', {}).get('lat')
                                    lng = data.get('location', {}).get('lng')
                                if lat is not None and lng is not None:
                                    google_maps_link = f"https://www.google.com/maps?q={lat},{lng}"
                                    caption += f"\n[Location Long: {lng} Lat:{lat}]({google_maps_link})"
                                    context.bot.send_photo(self.chat_id, f, caption, parse_mode="Markdown")
                        else:
                            context.bot.send_photo(self.chat_id, f, caption)
                else:
                    context.bot.send_message(chat_id=self.chat_id, text="Invalid file number.")
            except ValueError:
                context.bot.send_message(chat_id=self.chat_id, text="Please enter a valid number.")
        else:
            self.file_list.clear()
            for idx, filename in enumerate(os.listdir(self.qrcode_dir), start=1):
                if filename.lower().endswith('.png'):
                    file_name = filename.split('.')[0]
                    bssid = file_name.split('-')[-1]
                    geojson_files = glob.glob(f"/root/handshakes/*_{bssid}.gps.json")
                    geojson_files += glob.glob(f"/root/handshakes/*_{bssid}.geo.json")
                    if geojson_files:
                        filename += " *geodata*"
                    self.file_list.append(filename)
                if idx % 30 == 0 or idx == len(os.listdir(self.qrcode_dir)):
                    file_list_text = "\n".join([f"{i}. {fn}" for i, fn in enumerate(self.file_list, start=idx_start)])
                    context.bot.send_message(chat_id=self.chat_id, text=file_list_text)
                    self.file_list.clear()
                    idx_start = idx + 1

    def help_command(self, update, context):
        command_list = [
            'Try One Of These',
            '/genqrcodes - Initialize or update qr codes',
            '/screencap - Send capture of current pwnagotchi face',
            '/stats - Send brief system info',
            '/handshake - List all handshakes ',
            '/handshake # - Handshake file sent for selection',
            '/qr_files - List all available qr codes',
            '/qr_files # - QR and login displayed for selection',
            '/run (command) - Run cmd and provide stdout',
            '/sendfile (file) - Send config.toml, id_rsa or id_rsa.pub',
            '                 - And if you send one of those to the bot',
            '                 - it will save it to /etc/pwnagotchi/',
            '                 - do so with caution',
            '/restart - Restart Pwnagotchi',
            '/reboot - Reboot the system',
            '/shutdown - Shutdown the system',
            '/help - Show this help message'
        ]
        help_message = "\n".join(command_list)
        context.bot.send_message(chat_id=self.chat_id, text=help_message)

    def on_loaded(self):
        logging.info("[neonbot] Loading...")
        self.bot_token = config['main']['plugins']['neonbot']['bot_token']
        self.chat_id = config['main']['plugins']['neonbot']['chat_id']
        logging.info("[neonbot] Configured...")
        self.bot_running = False
        logging.info("[neonbot] Loading updater...")
        self.updater = Updater(token=self.bot_token, use_context=True)
        logging.info("[neonbot] Updater Loaded...")
        self.updater.dispatcher.add_handler(CommandHandler('xyzzy', self.important_command))
        self.updater.dispatcher.add_handler(CommandHandler('genqrcodes', self.genqrcodes_command))
        self.updater.dispatcher.add_handler(CommandHandler('restart', self.restart_command))
        self.updater.dispatcher.add_handler(CommandHandler('reboot', self.reboot_command))
        self.updater.dispatcher.add_handler(CommandHandler('shutdown', self.shutdown_command))
        self.updater.dispatcher.add_handler(CommandHandler('run', self.run_command))
        self.updater.dispatcher.add_handler(CommandHandler('qr_files', self.qr_files))
        self.updater.dispatcher.add_handler(CommandHandler('stats', self.stats_command))
        self.updater.dispatcher.add_handler(CommandHandler('sendfile', self.send_files_command))
        self.updater.dispatcher.add_handler(CommandHandler('screencap', self.screencap_command))
        self.updater.dispatcher.add_handler(CommandHandler('help', self.help_command))
        self.updater.dispatcher.add_handler(CommandHandler("handshake", self.handle_handshake))
        self.updater.dispatcher.add_handler(MessageHandler(Filters.document, self.receive_files_command))
        self.updater.dispatcher.add_handler(MessageHandler(Filters.command, self.help_command))
        logging.info("[neonbot] Loaded.")
        self._startstopbot()

    def on_unload(self, agent):
        if self.updater is not None:
            logging.info("[neonbot] Unloaded.")
            self.updater.stop()

    def on_internet_available(self, agent):
        self._startstopbot()