*** Pwnagotchi Build Guide ***
Description:
  * notes for building my pwnagotchi
  * Based on the guide from CyberSnek (https://pastebin.com/bTkXiZ52)
  * Last Updated: 2023 April
 
*** Hardware: ***
   * Raspberry Pi 3b
   * Pitft 2,8" resistive touch
   * PiSugar 3 Plus 5000 mAh UPS (pending)
   * Panda Wireless PAUN09 Wifi Adapter (pending)
   * DIYmall VK-172 USB GPS Dongle (U-blox 7)
   * Sandisk Ultra 32Gb micro SD
 
*** Kudos and Special Thanks: ***
  * Reddit User "u/panoptyk", for their "Guerrilla guide to Pwnagotchi [v1.5.5/2022]:
    Link: https://www.reddit.com/r/pwnagotchi/comments/sl2rv1/guerrilla_guide_to_pwnagotchi_v1552022/?utm_source=share&utm_medium=web2x&context=3
  * Junohea (Wark#8463) on the "Pwnagotchi Unofficial" Discord, for their guidance on configuring an external wifi adapter
  * Reddit User "u/Capt_Panic" on Reddit and Discord, for their contributions to this guide.
    Link: https://www.reddit.com/r/pwnagotchi/comments/ubnlde/comment/i6gg8sj/?utm_source=share&utm_medium=web2x&context=3
  * The Pwnagotchi Reddit Community:
    Link: https://www.reddit.com/r/pwnagotchi/
  * The "Pwnagotchi Unofficial" Discord Community:
    Link: https://discord.gg/8fV5Ka32
  * GaelicThunder on GitHub, for their Exp Plugin:
    Link: https://github.com/GaelicThunder/Experience-Plugin-Pwnagotchi
  * Hanna.Diamond on GitHub, for their Age Plugin and Waveshare 3.7" e-ink display Plugin:
    Link: https://github.com/hannadiamond/pwnagotchi-plugins
 
*** Build Instructions Below: ***
 
Step 1) Download Pwnagotchi image
  * Official repo from Evilsocket: https://github.com/evilsocket/pwnagotchi/releases
  * 1.5.5 with waveshare V3 patch: https://archive.org/details/pwnagotchi_1.5.5_WSV3Patched
  * 1.5.6 fork from Dr.Schottky:   https://github.com/DrSchottky/pwnagotchi/releases
  * 1.6.x fork from Aluminium-Ice: https://github.com/aluminum-ice/pwnagotchi/releases
  
       Note: version 1.5.5 is the latest version as of April 2022
             Many have recommended instead to flash version 1.5.3
             in order to avoid reported bugs regarding AI mode not starting.
             once installed, version 1.5.3 will automatically update to 1.5.5
             with an established internet connection (host connection sharing or bt-tether) 
             Download version 1.5.3 to avoid having to fix AI Mode. 
             Remediation guidance for v1.5.5 AI Mode bug is available from u/panoptyk on Reddit. See Link in Kudos section above.
 
Step 2) Flash pwnagotchi image to microSD.
       Note: Recommended to use "balenaEtcher" to flash the image.
             Several tutorials exist online (Google or YouTube) that
             provide instructions for flashing an image to a microSD.
 
Step 3) Build your initial config.toml
       Note: your initial config.toml will contain the baseline configuration
             for your pwnagotchi, such as the name of the device. It is recommended to avoid
             trying to configure all of your plugins at this stage, and only focus on the 
             essential plugins, such as 'bt-tether'.
 
######## start of config.toml ########
main.name = "pwnagotchi"
main.lang = "en"
main.whitelist = [
 "Your",
 "Network",
 "Here",
]
main.plugins.grid.enabled = true
main.plugins.grid.report = true
main.plugins.grid.exclude = [
 "Your",
 "Network",
 "Here",
]

main.plugins.bt-tether.enabled = true
main.plugins.bt-tether.devices.android-phone.enabled = true
main.plugins.bt-tether.devices.android-phone.search_order = 1
main.plugins.bt-tether.devices.android-phone.mac = "CH:AN:GE:XX:MM:EE" # Change this to your phones BT MAC
main.plugins.bt-tether.devices.android-phone.ip = "192.168.44.44" # If you have multiple pwnagotchi units, they will need different IPs 
main.plugins.bt-tether.devices.android-phone.netmask = 24
main.plugins.bt-tether.devices.android-phone.interval = 1
main.plugins.bt-tether.devices.android-phone.scantime = 10
main.plugins.bt-tether.devices.android-phone.max_tries = 0
main.plugins.bt-tether.devices.android-phone.share_internet = true
main.plugins.bt-tether.devices.android-phone.priority = 1

main.confd = "/etc/pwnagotchi/conf.d/"
main.custom_plugins = "/usr/local/share/pwnagotchi/installed-plugins/"  # Some plugins install say different, use only one folder for custom plugins
main.custom_plugin_repos = [
 "https://github.com/evilsocket/pwnagotchi-plugins-contrib/archive/master.zip",
 "https://github.com/Teraskull/pwnagotchi-community-plugins/archive/master.zip",
]
main.iface = "mon0"
main.mon_start_cmd = "/usr/bin/monstart"
main.mon_stop_cmd = "/usr/bin/monstop"
main.mon_max_blind_epochs = 50
main.no_restart = false
main.filter = ""
main.log.path = "/var/log/pwnagotchi.log"
main.log.rotation.enabled = true
main.log.rotation.size = "10M"

ui.display.enabled = true
ui.display.rotation = 180
ui.display.type = "spotpear24inch" # the spotpear24 inch display is using the same FB method as the pitft, you can change later
ui.display.color = "black"

# The web ui will be available from phone on the previously set IP, or if you connect to a router check the Pi-s IP address for web the web ui
ui.web.username = "changeme"
ui.web.password = "changeme"
ui.web.enabled = true
ui.web.address = "0.0.0.0"                  
ui.web.origin = ""
ui.web.port = 8080
ui.web.on_frame = ""

fs.memory.enabled = true
fs.memory.mounts.log.enabled = true
fs.memory.mounts.data.enabled = true

######## end of config.toml ########
 
Step 4) Copy config.toml to MicroSD (boot)
        Note: Insert the microSD card flashed in Step 3. Open the new drive titled "boot", and copy over your config.toml
 
Step 5) Boot pwnagotchi for the first time
        WARNING: BE PATIENT. The First boot will take longer than average due to key generation.
        NOTE: If you specified settings for bt-tether plugin, ensure your mobile device is nearby and listening for new bluetooth devices to pair. 
              Ensure Internet sharing via Personal Hotspot is enabled. Your mobile device will be prompted to pair with your pwnagotchi.

Step 6) Install pitft display drivers

For detailed instruction you can visit the adafruit website: https://learn.adafruit.com/adafruit-pitft-3-dot-5-touch-screen-for-raspberry-pi/overview
I have the 2,4" and 2,8" resistive touch displays, the resolution is 320x240 for both, and we will set it as a frame buffer display
SSH to the pi
In terminal we need the following commands:

cd ~
sudo apt-get update
sudo apt-get install -y git python3-pip
sudo pip3 install --upgrade adafruit-python-shell click
git clone https://github.com/adafruit/Raspberry-Pi-Installer-Scripts.git
cd Raspberry-Pi-Installer-Scripts
sudo python3 adafruit-pitft.py

When asked during the installation you should select:
1 - PiTFT 2,4", 2,8" or 3,2" resistive (240x320) (320x240)
1 - 90 degrees (landscape)
N - You would NOT like the console to appear on the display
N - You would NOT like the HDMI display to mirror on the display either

Reboot your pwnagotchi, and it should be smiling soon...

For backlight control you can use these commands to turn it off/on:
sudo sh -c 'echo "0" > /sys/class/backlight/soc\:backlight/brightness'
sudo sh -c 'echo "1" > /sys/class/backlight/soc\:backlight/brightness'


Step 7) Adding support for the pitft
 sudo nano /etc/pwnagotchi/config.toml
      #set: ui.display.enabled = true
      #set: ui.display.type = "pitft"
 
 sudo nano /usr/local/lib/python3.7/dist-packages/pwnagotchi/utils.py
 #Locate "def load_config" and add the following:
 elif config['ui']['display']['type'] in ('pitft', 'pitft28r', 'pitft24r'):
    config['ui']['display']['type'] = 'pitft'
 
 sudo nano /usr/local/lib/python3.7/dist-packages/pwnagotchi/ui/display.py
 #Add the following:
 def is_pitft(self):
   return self._implementation.name == 'pitft'
 
 sudo nano /usr/local/lib/python3.7/dist-packages/pwnagotchi/ui/hw/__init__.py
 #Add the following:
 from pwnagotchi.ui.hw.pitft import Pitft
 #Also, add the following into the elif block of the code:
 elif config['ui']['display']['type'] == 'pitft':
    return Pitft(config)
    
 sudo nano /usr/local/lib/python3.7/dist-packages/pwnagotchi/ui/hw/spotpear24inch.py
 #Modify the class as follows
 class Pitft(DisplayImpl):
    def __init__(self, config):
        super(Pitft, self).__init__(config, 'pitft')
        self._display = None
 #Save as pitft.py
 #If you need to modify the basic coordinates or font sizes you can do it in this file
    
 sudo systemctl restart pwnagotchi.service #to initialize new display. 
    # Troubleshooting: If the screen does not come on: 
    # Just SSH into your pwnagotchi via USB and check your work from the beginning of step 7.
    # I typically add the pitft code snippets at the end of the config files.
 
Step 8) Install & Configure Wireless adapter
 lsusb #ensure wifi adapter is plugged in and detected
 iw dev #ensure wlan1 is observed with mon0 under phy#1
 sudo nano /boot/config.txt
   # Find the following line:
     # Additional overlays and parameters are documented /boot/overlays/README
   # Add the following line under it:
     dtoverlay=disable-wifi #disables the onboard wifi, allowing our adapter to operate as wlan0
 
 sudo nano /usr/bin/pwnlib
 #locate and replace the contents of "start_monitor_interface with the following:
   #rename adapter and bring up as mon0 in monitor mode
   ip link set wlan0 down
   ip link set wlan0 name mon0
   iw dev mon0 set type monitor
   ip link set mon0 up
   #add a mon1 interface from the same adapter
   iw phy "$(iw phy | head -1 | cut -d" " -f2)" interface add mon1 type monitor
   
 sudo nano /etc/systemd/system/pwngrid-peer.service
  # update the service launch param. Replace "mon0" with "mon1"
  # Everything else continues to use mon0, bettercap accepts it and works fine. Pwngrid works fine on the mon1 interface.
 
 sudo reboot #allow all changes to take affect.
 
Step 9) Install custom plugins 
 #Consider this step OPTIONAL, unless you would like these custom plugins. Otherwise, proceed to Step 10.
 cd ~
 sudo mkdir /usr/local/share/pwnagotchi/installed-plugins/ 
      #make custom-plugins directory defined in config.toml, if not done so already.
 
 Step 9.1) aircrackonly plugin
  sudo pwnagotchi plugins install aircrackonly
  sudo nano /etc/pwnagotchi/config.toml
       # add the following lines to config.toml:
         main.plugins.aircrackonly.enabled = true
         main.plugins.aircrackonly.face = "( >.< )"
         
  # Aircrack-ng needed, to install:
  apt-get install aircrack-ng
        
 Step 9.2) Exp plugin #Generates an "experiance" level and progress bar for your pwnagotchi.
  #Copy exp.py from git: https://github.com/GaelicThunder/Experience-Plugin-Pwnagotchi
  sudo nano /usr/local/share/pwnagotchi/installed-plugins/exp.py #paste contents of exp.py from github to exp.py on your pwnagotchi.
  sudo nano /etc/pwnagotchi/config.toml
  #add the following to your config.toml. Please note that the positions have been adjusted to accomodate the waveshare 3.7 display.
    main.plugins.exp.enabled = true
    main.plugins.exp.lvl_x_coord = 0
    main.plugins.exp.lvl_y_coord = 210
    main.plugins.exp.exp_x_coord = 0
    main.plugins.exp.exp_y_coord = 228
 
 Step 9.3) Age plugin #Generates the pwnagotchi's "age" and "strength".
  #Copy exp.py from git: https://github.com/hannadiamond/pwnagotchi-plugins/blob/main/plugins/age.py
  sudo nano /usr/local/share/pwnagotchi/installed-plugins/age.py #paste contents of exp.py from github to exp.py on your pwnagotchi.
  sudo nano /etc/pwnagotchi/config.toml
  #add the following to your config.toml. Please note that the positions have been adjusted to accomodate the waveshare 3.7 display.
    main.plugins.age.enabled = true
    main.plugins.age.age_x_coord = 0
    main.plugins.age.age_y_coord = 56
    main.plugins.age.str_x_coord = 125
    main.plugins.age.str_y_coord = 56
    
 Step 9.4) GPS plugin #Uses the Ublox-7 USB GPS dongle to capture the GPS coordinates for a collected handshake. 
    #NOTE: Many people believe the GPS plugin should always communicate the current GPS coordinates. This is not true. the GPS coordinates will only update on the display when a handshake has been obtained. 
    #Troubleshooting: If the GPS dongle does not appear to be functioning, it is likely that the device is unable to capture a location (or has yet to capture a handshake. Try changing your physical location (i.e. go outside, walk around the house, down the street, etc). 
  lsusb #confirm the gps dongle is detected as plugged in.
  sudo pwnagotchi plugins install gps
  sudo nano /etc/pwnagotchi/config.toml
  #add the following to your config.toml. Please note that the positions have been adjusted to accomodate the waveshare 3.7 display.
    main.plugins.gps.enabled = true
    main.plugins.gps.speed = 19200
    main.plugins.gps.device = "/dev/ttyACM0" #gps dongle location
    main.plugins.gps.position = "225,194" #adjusted to support waveshare 3.7
    main.plugins.gps.linespacing = 18 #adjusted to support waveshare 3.7
    
 Step 9.5) PiSugar Plugin 
  #Ensure PiSugar Power Manager is installed:
  curl http://cdn.pisugar.com/release/pisugar-power-manager.sh | sudo bash
  cd /usr/local/share/pwnagotchi/installed-plugins/
  sudo nano pisugar2.py
  #locate and modify the following contents of 'def on_ui_setup':
        def on_ui_setup(self, ui):
        ui.add_element(
            "bat",
            LabeledValue(
                color=BLACK,
                label="BAT",
                value="0%",
                position=(ui.width() / 2 + 30, 0),
                label_font=fonts.Bold,
                text_font=fonts.Medium,
            ),
        )
  
 Step 9.6) memtemp Plugin
  sudo pwnagotchi plugins install memtemp
  sudo nano /etc/pwnagotchi/config.toml
  #add the following to your config.toml. Please note that the positions have been adjusted to accomodate the waveshare 3.7 display.
    main.plugins.memtemp.enabled = true
    main.plugins.memtemp.scale = "celsius"
    main.plugins.memtemp.orientation = "vertical" #adjusted for preference on waveshare 3.7
    main.plugins.memtemp.position = "382,194" #adjusted to support waveshare 3.7
    main.plugins.memtemp.linespacing = 18 #adjusted to support waveshare 3.7
    
 Step 9.7) customize bt-tether display position #to accomodate waveshare 3.7
  cd /usr/local/lib/python3.7/dist-packages/pwnagotchi/plugins/default 
  sudo nano bt-tether.py
  #locate and modify the following under 'def pn_ui_setup':
    def on_ui_setup(self, ui):
        with ui._lock:
            ui.add_element('bluetooth', LabeledValue(color=BLACK, label='BT', value='-', position=(ui.width() / 2 - 28$
                           label_font=fonts.Bold, text_font=fonts.Medium))
    
  sudo systemctl restart pwnagotchi.service #reload pwnagotchi with new plugins
 
Step 10) Update everything. #OPTIONAL. I'm just obsessive about updating everything...
 sudo pwnagotchi plugins update 
 sudo pwnagotchi plugins upgrade
 sudo apt-get update --allow-releaseinfo-change
      #Troubleshooting: Some repos for "re4son-kernel.com/re4son kali-pi" might present an error resembling the following: "The following signatures were invalid: EXPKEYSIG 11764EE8AC24832F Carsten Boeving <carsten.boeving@whitedome.com.au>"
      wget -O - https://re4son-kernel.com/keys/http/archive-key.asc | sudo apt-key add -
 
 sudo apt-get upgrade #This will take a while (~45 minutes). Be patient.
      #Troubleshooting: You might encounter an error that looks similar to:
      # Errors were encountered while processing:
      #  /var/cache/apt/archives/kalipi-kernel_5.4.83-20211204_armhf.deb
      # E: Sub-process /usr/bin/dpkg returned an error code (1)
         sudo mv /boot/overlays/ overlaysbackup #rename the existing overlays in /boot/. The renamed overlays can be safely deleted later
         sudo apt-get upgrade #attempt upgrade again.
 
 
Step 11) Change all the default passwords
 # Change "pi" password. Default "raspberry"
 psswd
 
 # Change "root" password:
 sudo su
 psswd
 
 # Change pwnagotchi Web UI password. Default "changeme"
 sudo nano /etc/pwnagotchi/config.toml
  # locate and update the values for:
    ui.web.username = "changeme"
    ui.web.password = "changeme"
 
 # Update bettercap password. Default "pwnagotchi"
 sudo nano /etc/pwnagotchi/config.toml
  # locate and update the values for:
    bettercap.username = "pwnagotchi"
    bettercap.password = "pwnagotchi"
  sudo nano /usr/local/share/bettercap/caplets/pwnagotchi-auto.cap 
    #modify the bettercap username & password to match config.toml
  sudo nano /usr/local/share/bettercap/caplets/pwnagotchi-manual.cap
    #modify the bettercap username & password to match config.toml
 
 sudo systemctl restart pwnagotchi.service #reload pwnagotchi for config changes to apply.
    
Step 12) Back up all your hard work!
 Download the Backup script from Github.
 # Link: https://github.com/evilsocket/pwnagotchi/blob/master/scripts/backup.sh
 
 Append the "FILES_TO_BACKUP" section of the backup script to include the following additional files that have been added or modified as a result of this guide:
 
  /usr/bin/pwnlib \
  /etc/systemd/system/pwngrid-peer.service \
  /usr/local/share/pwnagotchi/custom-plugins/ \
  /usr/local/lib/python3.7/dist-packages/pwnagotchi/ui/hw/libs/waveshare/v37inch/ \
  /usr/local/lib/python3.7/dist-packages/pwnagotchi/ui/hw/waveshare37inch.py \
  /usr/local/lib/python3.7/dist-packages/pwnagotchi/utils.py \
  /usr/local/lib/python3.7/dist-packages/pwnagotchi/ui/display.py \
  /usr/local/lib/python3.7/dist-packages/pwnagotchi/ui/components.py \
  /usr/local/lib/python3.7/dist-packages/pwnagotchi/ui/hw/__init__.py
 
     # Note: The last entry in the list must include an end quotation mark. Be sure to relocate this to the end of the list before saving.
  
  sudo chmod +x backup.sh # make backup.sh executable
  sudo ./backup.sh
 
#### Enjoy your new Pwnagotchi, and please support the Pwnagotchi community on Reddit and Discord! ####
 
Step 13) [OPTIONAL] Accessing your handshakes
#### Additional Optional step, curtosy of /u/Capt_Panic on Reddit and Discord #### 
    #Reference: https://www.reddit.com/r/pwnagotchi/comments/ubnlde/comment/i6gg8sj/?utm_source=share&utm_medium=web2x&context=3
    
#create file to access handshakes
 sudo nano cph.sh
 #insert these lines into the file
    \#/bin/bash
 
 cp -r /root/handshakes/\* /home/pi/handshakes/
 
 chown pi:pi /home/pi/handshakes
 
 chown pi:pi /home/pi/handshakes/\*
 sudo chmod +x cph.sh
    #To run file, execute 'sudo cph.sh'. This will copy your handshakes into the /home/pi/handshakes directory
 
Step 14) [OPTIONAL] May be required if you are having troubles with bluetooth
#### Additional Optional step, curtosy of /u/Capt_Panic on Reddit and Discord #### 
    #Reference: https://www.reddit.com/r/pwnagotchi/comments/ubnlde/comment/i6gg8sj/?utm_source=share&utm_medium=web2x&context=3
 
 # We need to add something into our profile which is in our root directory, hidden.
 sudo su
 cd /root
 sudo nano ~/.profile
 #add the following at the bottom of the file.
 \# attempt to restart bluetooth
 
 sudo systemctl restart bluetooth
 #save using crtl + x and then hit enter.
 #Comment out an if-else-statement.
 sudo nano /usr/bin/btuart
 #At the first if-else-statement you see, comment it out like you you see below.
 \#if grep -q "raspberrypi,4" /proc/device-tree/compatible; then
 
 BDADDR=
 
 \#else
 
 SERIAL='cat /proc/device-tree/serial-number | cut -c9-'
 
 B1='echo $SERIAL | cut -c3-4'
 
 B2='echo $SERIAL | cut -c5-6'
 
 B3='echo $SERIAL | cut -c7-8'
 
 BDADDR='printf b8:27:eb:%02x:%02x:%02x $((0x$B1 \^ 0xaa)) $((0x$B2 \^ 0xaa)) $((0x$B3 \^ 0xaa))'
 
 \#fi
 #save it using crtl + x and then hit enter.
 sudo reboot
