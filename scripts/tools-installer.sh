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

install_tools() {
    echo "Installing Tools..."
    #sudo apt update && sudo apt upgrade -y
    sudo apt install -y raspberrypi-ui-mods byobu aircrack-ng nmap expect speedtest-cli libttspico0 libttspico-utils macchanger espeak python3-pytzdata python3-googleapi python3-google-auth-oauthlib python3-speechd python3-buttonshim python3-nmea2 python3-qrcode python3-psutil python3-feedparser python3-netifaces python3-paramiko python3-plotly python3-serial python3-geopy python3-discord python3-dotenv
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

lcd_show() {
    sudo rm -rf LCD-show
    git clone https://github.com/goodtft/LCD-show.git
    chmod -R 755 LCD-show
    cd LCD-show/
    sudo ./LCD35-show # or sudo ./LCD35-show 90
}
hdmi_screen() {
    cd /tmp
    git clone https://github.com/solution-libre/pwnagotchi-hdmi-viewer.git
    cd pwnagotchi-hdmi-viewer
    sudo mv pwnagotchi-launcher-pre pwnagotchi-viewer pwnagotchi-viewer-next /usr/local/sbin

    sudo sed -i 's/ui.web.on_frame = \"\"/ui.web.on_frame = \"pwnagotchi-viewer-next\"/g' /etc/pwnagotchi/config.toml

    sudo systemctl daemon-reload
}
showerthoughts() {
    sudo curl --silent https://www.reddit.com/r/showerthoughts/.rss --user-agent 'Mozilla' --output /root/showerthoughts.rss
    sudo wget -P /usr/local/bin https://raw.githubusercontent.com/NoxiousKarn/Showerthoughts/main/remove_long_titles.py
    sudo python /usr/local/bin/remove_long_titles.py
    sudo wget -P /usr/local/lib/python3.11/dist-packages/pwnagotchi/ https://raw.githubusercontent.com/NoxiousKarn/Showerthoughts/main/voice.py
    sudo mv /usr/local/lib/python3.11/dist-packages/pwnagotchi/voice.py /usr/local/lib/python3.11/dist-packages/pwnagotchi/voice.py.old
    sudo mv /usr/local/lib/python3.11/dist-packages/pwnagotchi/voice.py.1 /usr/local/lib/python3.11/dist-packages/pwnagotchi/voice.py
    (
        echo "0 */4 * * * curl --silent https://www.reddit.com/r/showerthoughts.rss --user-agent 'Mozilla' --output showerthoughts.rss"
        echo "0 */4 * * * curl --silent https://www.reddit.com/r/worldnews.rss --user-agent 'Mozilla' --output worldnews.rss"
        echo "0 */4 * * * /usr/bin/python3 /usr/local/bin/remove_long_titles.py >/dev/null 2>&1"
    ) | sudo crontab -
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
    cd ~/bin
    ln -s /usr/local/share/pwnagotchi/custom-plugins/scripts/* .
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

    sudo dd if=/dev/sdc of=Paimon-$(date +"%Y%m%d").img bs=4M conv=fsync status=progress
    sync
    md5sum Paimon-$(date +"%Y%m%d").img >Paimon-$(date +"%Y%m%d").img.md5

    echo "Shrinking Backup..."
    echo "Cecking md5 sum..."
    if md5sum -c Paimon-$(date +"%Y%m%d").img.md5; then
        sudo pishrink.sh -Za Paimon-$(date +"%Y%m%d").img
        md5sum Paimon-$(date +"%Y%m%d").img >Paimon-$(date +"%Y%m%d").img.md5
        echo "Backup done!"
        sudo chown $USER Paimon-$(date +"%Y%m%d").img
        sudo chown $USER Paimon-$(date +"%Y%m%d").img.xz
        md5sum Paimon-$(date +"%Y%m%d").img.xz >Paimon-$(date +"%Y%m%d").img.xz.md5
    else
        echo "MD5 sum does not match!"
        exit
    fi
}
restore_backup() {
    cd ~
    lsblk
    echo "Cecking md5 sum..."
    if md5sum -c Paimon-$(date +"%Y%m%d").img.md5; then
        sudo dd if=Paimon-$(date +"%Y%m%d").img of=/dev/sdc bs=4M conv=fsync status=progress
        sync
        echo "Restore done!"
    else
        echo "MD5 sum does not match!"
        exit
    fi
}

bt_tether() {
    export PWNTETHER=94:45:60:5D:84:11
    git clone https://github.com/bablokb/pi-btnap.git
    sudo pi-btnap/tools/install-btnap client

    sudo sed -i "s@REMOTE_DEV=\"\"@REMOTE_DEV=\"$PWNTETHER\"@g" /etc/btnap.conf

    cat <<-EOFF >/home/pi/bluetooth-pair.sh
#!/usr/bin/expect -f

set prompt "#"
set address [lindex \$argv 0]

spawn bluetoothctl
expect -re \$prompt
send "remove \$address\r"
sleep 1
expect -re \$prompt
send "scan on\r"
send_user "\nSleeping\r"
sleep 10
send_user "\nDone sleeping\r"
send "scan off\r"
expect "Controller"
send "trust \$address\r"
sleep 2
send "pair \$address\r"
sleep 2
expect "Confirm passkey"
send "yes\r"
sleep 3
send_user "\nShould be paired now.\r"
send "quit\r"
expect eof
EOFF
    chmod +x /home/pi/bluetooth-pair.sh

    cat <<-EOFF >/home/pi/tether-restart.sh
#!/bin/sh

SCRIPT=\$(readlink -f \$0)
SCRIPTPATH=\`dirname \$SCRIPT\`

/sbin/ifconfig bnep0 > /dev/null 2>&1
status=\$?
if [ \$status -ne 0 ]; then
	echo "Connecting to bluetooth"
	sudo systemctl restart btnap
fi
sleep 10
	sudo ifconfig bnep0 192.168.44.100 netmask 255.255.255.0
	sudo sed -i "s@127.0.0.1@8.8.8.8@g" /etc/resolv.conf
	sudo route del -net 0.0.0.0 netmask 0.0.0.0 gw 10.0.0.1
	sudo route add -net 0.0.0.0 netmask 0.0.0.0 gw 192.168.44.1
EOFF
    chmod +x /home/pi/tether-restart.sh

    sudo /home/pi/bluetooth-pair.sh $PWNTETHER
    sudo systemctl restart btnap
    sleep 10
    sudo ifconfig bnep0 192.168.44.100 netmask 255.255.255.0
    sudo sed -i "s@127.0.0.1@8.8.8.8@g" /etc/resolv.conf
    sudo route del -net 0.0.0.0 netmask 0.0.0.0 gw 10.0.0.1
    sudo route add -net 0.0.0.0 netmask 0.0.0.0 gw 192.168.44.1
}

plugins() {
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
    enable_default_plugins() {
        echo "Enable default Plugins..."
        cd /usr/local/lib/python3.11/dist-packages/pwnagotchi/plugins/default
        for i in *.py; do
            echo "[ENABLE]: ${i%%.*}"
            sudo pwnagotchi plugins enable ${i%%.*}
            sudo pwnagotchi plugins enable bt-tether
            sudo pwnagotchi plugins enable telegram
            sudo pwnagotchi plugins disable example
        done
    }
    enable_custom_plugins() {
        echo "Enable custom Plugins..."
        cd /usr/local/share/pwnagotchi/available-plugins
        for i in *.py; do
            echo "[ENABLING]: ${i%%.*}"
            sudo pwnagotchi plugins enable ${i%%.*}
            sudo pwnagotchi plugins disable example_ng
        done
    }
    install_all_plugins() {
        echo "Install all Plugins..."
        cd /usr/local/lib/python3.11/dist-packages/pwnagotchi/plugins/default
        for i in *.py; do
            echo "[INSTALLING]: ${i%%.*}"
            sudo pwnagotchi plugins install ${i%%.*}
        done
        cd /usr/local/share/pwnagotchi/available-plugins
        for i in *.py; do
            echo "[INSTALLING]: ${i%%.*}"
            sudo pwnagotchi plugins install ${i%%.*}
        done
    }
    uninstall_all_plugins() {
        echo "Uninstall all Plugins..."
        cd /usr/local/lib/python3.11/dist-packages/pwnagotchi/plugins/default
        for i in *.py; do
            echo "[UNINSTALLING]: ${i%%.*}"
            sudo pwnagotchi plugins uninstall ${i%%.*}
        done
        cd /usr/local/share/pwnagotchi/available-plugins
        for i in *.py; do
            echo "[UNINSTALLING]: ${i%%.*}"
            sudo pwnagotchi plugins disable ${i%%.*}
            sudo pwnagotchi plugins uninstall ${i%%.*}
            sudo rm -f /usr/local/share/pwnagotchi/available-plugins/${i%%.*}.py
            sudo rm -f /usr/local/share/pwnagotchi/custom-plugins/${i%%.*}.py
        done
    }

    # install_all_plugins
    # uninstall_all_plugins
    # disable_all_plugins
    enable_default_plugins
    # enable_custom_plugins

}
plugins

# dns_fix
update_apt
update_pwnagotchi
# bettercaplets
# edit_pwnlib
# lcd_show
# edit_interfaces
# install_sounds
# plugins
# copy_tomls
enable_scripts
enable_lcd
