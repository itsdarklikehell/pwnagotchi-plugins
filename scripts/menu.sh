#!/bin/bash

update_plugins() {
    if [[ $LOCAL == true ]]; then
        cd pwnagotchi-plugins
        git pull origin master
        mkdir -p ~/scripts
        cp pwnmenu.txt ~/scripts/
    fi
    if [[ $EXTERNAL == true ]]; then
        ssh pi@Paimon.local -- "sudo pwnagotchi plugins update && sudo pwnagotchi plugins upgrade"
        ssh pi@Paimon.local -- "mkdir -p ~/scripts"
        ssh pi@Paimon.local -- "cp pwnmenu.txt ~/scripts"
        ssh pi@Paimon.local -- "sudo cp /usr/local/share/pwnagotchi/custom-plugins/tweak-view.json /etc/pwnagotchi/"
    fi
}

install_tools() {
    if [[ $LOCAL == true ]]; then
        cd ~
        sudo apt install -y raspberrypi-ui-mods aircrack-ng nmap macchanger espeak python3-pytzdata python3-googleapi python3-google-auth-oauthlib python3-speechd python3-buttonshim python3-nmea2 python3-qrcode python3-psutil python3-feedparser python3-netifaces python3-paramiko python3-plotly python3-serial python3-geopy python3-discord python3-dotenv
        sudo rm -rf LCD-show
        git clone https://github.com/goodtft/LCD-show.git
        chmod -R 755 LCD-show
        cd LCD-show/ && sudo ./LCD35-show
    fi
    if [[ $EXTERNAL == true ]]; then
        ssh pi@Paimon.local -- "sudo apt install -y raspberrypi-ui-mods aircrack-ng nmap macchanger espeak python3-pytzdata python3-googleapi python3-google-auth-oauthlib python3-speechd python3-buttonshim python3-nmea2 python3-qrcode python3-psutil python3-feedparser python3-netifaces python3-paramiko python3-plotly python3-serial python3-geopy python3-discord python3-dotenv"
        ssh pi@Paimon.local -- "sudo rm -rf LCD-show"
        ssh pi@Paimon.local -- "git clone https://github.com/goodtft/LCD-show.git"
        ssh pi@Paimon.local -- "chmod -R 755 LCD-show"
        ssh pi@Paimon.local -- "cd LCD-show/ && sudo ./LCD35-show"
    fi
}

where() {
    echo "Are you running this on a pwnagotchi (Local) or do you want to ssh into one (External)?"
    select LE in "Local" "External"; do
        case $yn in
        Local)
            LOCAL=true
            break
            ;;
        External)
            LOCAL=true
            break
            ;;
        esac
    done
}

echo "Update plugins?"
select yn in "Yes" "No"; do
    case $yn in
    Yes)
        where
        update_plugins
        break
        ;;
    No) exit ;;
    esac
done

echo "Install tools?"
select yn in "Yes" "No"; do
    case $yn in
    Yes)
        where
        install_tools
        break
        ;;
    No) exit ;;
    esac
done
