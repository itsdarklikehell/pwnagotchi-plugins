#!/bin/bash

bettercaplets() {
    echo "Setting up caplets..."
    sudo bettercap -eval 'caplets.update; ui.update; quit'
    sudo nano /usr/local/share/bettercap/caplets/pwnagotchi-auto.cap /usr/local/share/bettercap/caplets/pwnagotchi-manual.cap /usr/local/share/bettercap/caplets/http-ui.cap /usr/local/share/bettercap/caplets/https-ui.cap
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
    wget http://archive.raspberrypi.org/debian/pool/main/s/svox/libttspico-utils_1.0+git20130326-3+rpi1_armhf.deb
    wget http://archive.raspberrypi.org/debian/pool/main/s/svox/libttspico0_1.0+git20130326-3+rpi1_armhf.deb
    sudo apt install -y ./libttspico0_1.0+git20130326-3+rpi1_armhf.deb ./libttspico-utils_1.0+git20130326-3+rpi1_armhf.deb
    pico2wave -w lookdave.wav 'Look Dave, I can see youre really upset about this.' && aplay lookdave.wav
}

install_tools() {
    echo "Installing Tools..."
    #sudo apt update && sudo apt upgrade -y
    sudo apt install -y byobu aircrack-ng nmap macchanger espeak python3-pytzdata python3-googleapi python3-google-auth-oauthlib python3-speechd python3-buttonshim python3-nmea2 python3-qrcode python3-psutil python3-feedparser python3-netifaces python3-paramiko python3-plotly python3-serial python3-geopy python3-discord python3-dotenv
    wget https://raw.githubusercontent.com/Drewsif/PiShrink/master/pishrink.sh
    chmod +x pishrink.sh
    sudo mv pishrink.sh /usr/local/bin

}

install_seclists() {
    echo "Installing SecLists..."
    cd ~
    git clone https://github.com/danielmiessler/SecLists
    ln -s /etc/pwnagotchi/wordlists
}

dns_fix() {
    echo nameserver 1.1.1.1 | sudo tee -a /etc/resolv.conf
}

update_plugins() {
    echo "Updating Plugins..."
    cd ~
    sudo pwnagotchi plugins update
    sudo pwnagotchi plugins upgrade
}

disable_all_plugins() {
    echo "Disable all Plugins..."
    cd /usr/local/share/pwnagotchi/custom-plugins
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
    echo "Install all Plugins..."
    cd /usr/local/share/pwnagotchi/available-plugins
    for i in *.py; do
        echo "[INSTALLING]: ${i%%.*}"
        sudo pwnagotchi plugins install ${i%%.*}
    done
}

uninstall_all_plugins() {
    echo "Uninstall all Plugins..."
    cd /usr/local/share/pwnagotchi/available-plugins
    for i in *.py; do
        echo "[UNINSTALLING]: ${i%%.*}"
        sudo pwnagotchi plugins disable ${i%%.*}
        sudo pwnagotchi plugins uninstall ${i%%.*}
        sudo rm -f /usr/local/share/pwnagotchi/available-plugins/${i%%.*}.py
        sudo rm -f /usr/local/share/pwnagotchi/custom-plugins/${i%%.*}.py
    done
}

copy_tomls() {
    echo "Copy all configs to conf.d..."
    cd /usr/local/share/pwnagotchi/available-plugins/configs
    for i in *.toml; do
        echo "[COPYING CONFIG]: ${i%%.*}.toml"
        sudo cp ${i%%.*}.toml /etc/pwnagotchi/conf.d/
    done
}

enable_scripts() {
    cd ~
    ln -s /usr/local/share/pwnagotchi/custom-plugins/scripts .
    mkdir bin
    cd /usr/local/share/pwnagotchi/custom-plugins/scripts
    ln -s * ~/bin
}

enable_lcd() {
    cd ~
    sudo rm -rf LCD-show
    git clone https://github.com/goodtft/LCD-show.git
    chmod -R 755 LCD-show
    cd LCD-show/
    sudo ./LCD35-show
}

create_backup() {
    cd ~
    lsblk

    sudo dd if=/dev/sdc of=Paimon.img bs=4M conv=fsync status=progress
    sync
    md5sum Paimon.img >md5sum.txt

    echo "Shrinking Backup..."
    echo "Cecking md5 sum..."
    if md5sum -c md5sum.txt; then
        sudo pishrink.sh -Za Paimon.img
        md5sum Paimon.img >md5sum.txt
        echo "Backup done!"
    else
        echo "MD5 sum does not match!"
        exit
    fi
}

restore_backup() {
    cd ~
    lsblk

    echo "Cecking md5 sum..."
    if md5sum -c md5sum.txt; then
        sudo dd if=Paimon.img of=/dev/sdc bs=4M conv=fsync status=progress
        sync
        echo "Restore done!"
    else
        echo "MD5 sum does not match!"
        exit
    fi

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
# disable_all_plugins
# enable_all_plugins
# uninstall_all_plugins
# copy_tomls
enable_scripts
enable_lcd
