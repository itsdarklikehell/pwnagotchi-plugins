#!/bin/bash
#set -e
if [ "$HOSNAME" != "WifiKirby" ]; then
    GOTCHI_ADDR=pi@WifiKirby
else
    GOTCHI_ADDR=localhost
fi

raspi-config() {
    ssh "$GOTCHI_ADDR" "sudo raspi-config"
}

bettercaplets() {
    echo "Setting up caplets..."
    ssh "$GOTCHI_ADDR" "sudo bettercap -eval 'caplets.update; ui.update; quit'"
    ssh "$GOTCHI_ADDR" "sudo nano /usr/local/share/bettercap/caplets/pwnagotchi-auto.cap /usr/local/share/bettercap/caplets/pwnagotchi-manual.cap /usr/local/share/bettercap/caplets/http-ui.cap /usr/local/share/bettercap/caplets/https-ui.cap"
}

update_apt() {
    echo "Updating apt..."
    ssh "$GOTCHI_ADDR" "sudo nano /etc/apt/preferences.d/kali.pref"
    ssh "$GOTCHI_ADDR" "wget -O - https://re4son-kernel.com/keys/http/archive-key.asc | sudo apt-key add -"
    ssh "$GOTCHI_ADDR" "sudo apt-key adv --keyserver hkp://pgp.mit.edu --recv-keys 11764EE8AC24832F"
    ssh "$GOTCHI_ADDR" "sudo apt update --allow-releaseinfo-change-suite"
    ssh "$GOTCHI_ADDR" "sudo apt upgrade -y"
    ssh "$GOTCHI_ADDR" "sudo apt full-upgrade -y"
    ssh "$GOTCHI_ADDR" "sudo apt install --fix-missing"
    ssh "$GOTCHI_ADDR" "sudo apt install --fix-broken"
}
update_pwnagotchi() {
    echo "Updating pwnagotchi..."
    ssh "$GOTCHI_ADDR" "cd /usr/local/src/pwnagotchi/ && sudo git pull && sudo pip3 install ."
}

edit_pwnlib() {
    echo "editting pwnlib..."
    ssh "$GOTCHI_ADDR" "sudo nano /usr/bin/pwnlib"
}

edit_interfaces() {
    echo "editting interfaces..."
    ssh "$GOTCHI_ADDR" "sudo nano /etc/network/interfaces.d/*"
}

install_sounds() {
    echo "installing sounds/picotts..."
    ssh "$GOTCHI_ADDR" "wget http://archive.raspberrypi.org/debian/pool/main/s/svox/libttspico-utils_1.0+git20130326-3+rpi1_armhf.deb"
    ssh "$GOTCHI_ADDR" "wget http://archive.raspberrypi.org/debian/pool/main/s/svox/libttspico0_1.0+git20130326-3+rpi1_armhf.deb"
    ssh "$GOTCHI_ADDR" "sudo apt install -y ./libttspico0_1.0+git20130326-3+rpi1_armhf.deb ./libttspico-utils_1.0+git20130326-3+rpi1_armhf.deb"
    ssh "$GOTCHI_ADDR" "pico2wave -w lookdave.wav 'Look Dave, I can see youre really upset about this.' && aplay lookdave.wav"
}

install_aircrack() {
    echo "Installing Aircrack..."
    ssh "$GOTCHI_ADDR" "sudo apt install -y aircrack-ng nmap macchanger espeak"
    ssh "$GOTCHI_ADDR" "sudo pip3 install pytz google-api-python-client google-auth-oauthlib SpeechRecognition pyttsx3 python-telegram-bot"
}

install_seclists() {
    echo "Installing SecLists..."
    cd ~
    ssh "$GOTCHI_ADDR" "git clone https://github.com/danielmiessler/SecLists"
    ssh "$GOTCHI_ADDR" "ln -s /home/pi/SecLists wordlists"
}

dns_fix() {
    ssh "$GOTCHI_ADDR" "echo nameserver 1.1.1.1 | sudo tee -a /etc/resolv.conf"
}

reboot() {
    echo "Rebooting..."
    ssh "$GOTCHI_ADDR" "sudo reboot now"
}

dns_fix
raspi-config

# update_apt
# update_pwnagotchi
# bettercaplets
# edit_pwnlib
# edit_interfaces
# install_sounds
# install_aircrack
# reboot
