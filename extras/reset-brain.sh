#!/bin/bash
echo "[=] Stopping pwnagtochi service"
sudo systemctl stop pwnagotchi.service
echo "[-] Erasing past life"
sudo rm -rf /root/handshakes/*.pcap /root/peers/ /root/brain.nn /root/brain.json
#sudo rm -rf /root/.shakes /root/.qrlist /root/qrcodes /home/pi/.qrlist /home/pi/qrcodes /root/handshakes/ /root/peers/ /var/log/pwnagotchi.log /root/brain.nn /root/brain.json
echo "[=] Setting auto flag"
sudo touch /root/.pwnagotchi-auto
echo "[=] Starting pwnagtochi service"
# echo "now start pwnagotchi service manually"
sudo systemctl start pwnagotchi
#sudo reboot
#sudo shutdown -h now
echo "[=] Pwnagotchi reset complete"
