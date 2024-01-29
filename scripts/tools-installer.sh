#!/bin/bash
#set -e
if [ "$HOSNAME" != "Paimon" ]; then
    GOTCHI_ADDR=pi@Paimon
else
    GOTCHI_ADDR=localhost
fi

bettercaplets() {
    echo "Setting up caplets..."
    sudo bettercap -eval 'caplets.update; ui.update; quit'
    sudo nano /usr/local/share/bettercap/caplets/pwnagotchi-auto.cap /usr/local/share/bettercap/caplets/pwnagotchi-manual.cap /usr/local/share/bettercap/caplets/http-ui.cap /usr/local/share/bettercap/caplets/https-ui.cap
}

update_apt() {
    echo "Updating apt..."
    sudo apt update -y
    sudo apt upgrade -y
    sudo apt full-upgrade -y
    sudo apt install --fix-missing
    sudo apt install --fix-broken
}

update_pwnagotchi() {
    echo "Updating pwnagotchi..."
    sudo pwnagotchi --version
    sudo pwnagotchi --check-update
}

edit_pwnlib() {
    echo "editting pwnlib..."
    sudo nano /usr/bin/pwnlib
}

edit_interfaces() {
    echo "editting interfaces..."
    sudo nano /etc/network/interfaces.d/*
}

install_sounds() {
    echo "installing sounds/picotts..."
    ssh "$GOTCHI_ADDR" "wget http://archive.raspberrypi.org/debian/pool/main/s/svox/libttspico-utils_1.0+git20130326-3+rpi1_armhf.deb"
    ssh "$GOTCHI_ADDR" "wget http://archive.raspberrypi.org/debian/pool/main/s/svox/libttspico0_1.0+git20130326-3+rpi1_armhf.deb"
    ssh "$GOTCHI_ADDR" "sudo apt install -y ./libttspico0_1.0+git20130326-3+rpi1_armhf.deb ./libttspico-utils_1.0+git20130326-3+rpi1_armhf.deb"
    ssh "$GOTCHI_ADDR" "pico2wave -w lookdave.wav 'Look Dave, I can see youre really upset about this.' && aplay lookdave.wav"
}

install_tools() {
    echo "Installing Tools..."
    sudo apt install -y aircrack-ng nmap macchanger espeak python3-pytzdata python3-googleapi python3-google-auth-oauthlib python3-speechd
}

install_seclists() {
    echo "Installing SecLists..."
    cd ~
    ssh "$GOTCHI_ADDR" "git clone https://github.com/danielmiessler/SecLists"
    ssh "$GOTCHI_ADDR" "ln -s /etc/pwnagotchi/wordlists"
}

dns_fix() {
    ssh "$GOTCHI_ADDR" "echo nameserver 1.1.1.1 | sudo tee -a /etc/resolv.conf"
}

update_plugins() {
    echo "Updating Plugins..."
    cd ~
    sudo pwnagotchi plugins update
    sudo pwnagotchi plugins upgrade
}

disable_all_plugins() {
    echo "Disable all Plugins..."
    cd /usr/local/share/pwnagotchi/available-plugins
    for i in *.py; do
        echo "[DISABLE]: ${i%%.*}"
        sudo pwnagotchi plugins disable ${i%%.*}
    done
}

enable_all_plugins() {
    echo "Enable all Plugins..."
    cd /usr/local/share/pwnagotchi/available-plugins
    for i in *.py; do
        echo "[ENABLING]: ${i%%.*}"
        sudo pwnagotchi plugins enable ${i%%.*}
    done
}

install_all_plugins() {
    echo "Enable all Plugins..."
    cd /usr/local/share/pwnagotchi/available-plugins
    for i in *.py; do
        echo "[INSTALLING]: ${i%%.*}"
        sudo pwnagotchi plugins install ${i%%.*}
    done
}

uninstall_all_plugins() {
    echo "uninstall all Plugins..."
    cd /usr/local/share/pwnagotchi/available-plugins
    for i in *.py; do
        echo "[UNINSTALLING]: ${i%%.*}"
        sudo pwnagotchi plugins uninstall ${i%%.*}
    done
}

# dns_fix
update_apt
update_pwnagotchi
# bettercaplets
# edit_pwnlib
# edit_interfaces
# install_sounds
install_tools
update_plugins
install_all_plugins
disable_all_plugins
enable_all_plugins
# uninstall_all_plugins
