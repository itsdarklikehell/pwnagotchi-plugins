#!/usr/bin/env bash
# Edited by Doctor X - @xNigredo -- t.me/pwnagotchiitalia
set -e
GOTCHI_ADDR=pi@10.0.0.2
YOUR_DNS=8.8.8.8
USB_IFACE="$(ip -br l | awk '$1 !~ "ham|lo|vir|tun|wl|enp" { print $1 }')"
USB_IFACE_IP=10.0.0.1
USB_IFACE_NET=10.0.0.0/24
UPSTREAM_IFACE="$(ip route get $YOUR_DNS | awk -- '{printf $5}')"

echo "Flushing $USB_IFACE"
sudo ip addr flush "$USB_IFACE"
echo "Adding $USB_IFACE_IP/24 to dev $USB_IFACE"
sudo ip addr add "$USB_IFACE_IP/24" dev "$USB_IFACE"
echo "setting link to $USB_IFACE up"
sudo ip link set "$USB_IFACE" up
echo "setting up iptables forwarding from $UPSTREAM_IFACE to $USB_IFACE with $USB_IFACE_NET"
sudo iptables -A FORWARD -o "$UPSTREAM_IFACE" -i "$USB_IFACE" -s "$USB_IFACE_NET" -m conntrack --ctstate NEW -j ACCEPT
sudo iptables -A FORWARD -m conntrack --ctstate ESTABLISHED,RELATED -j ACCEPT
sudo iptables -t nat -F POSTROUTING
sudo iptables -t nat -A POSTROUTING -o "$UPSTREAM_IFACE" -j MASQUERADE

if [ -f /proc/sys/net/ipv4/ip_forward ]; then
  echo "setting /proc/sys/net/ipv4/ip_forward to:"
  sudo echo "1" | sudo tee /proc/sys/net/ipv4/ip_forward
else
  echo "WARNING:"
  echo "file /proc/sys/net/ipv4/ip_forward does not exist!"
fi

echo "Copying ssh keys from/to $GOTCHI_ADDR prior to logging in."
ssh-copy-id -f "$GOTCHI_ADDR"
echo "Logging in to $GOTCHI_ADDR and setting namesever to $YOUR_DNS"
ssh "$GOTCHI_ADDR" "echo 'nameserver $YOUR_DNS' | sudo tee -a /etc/resolv.conf"
ssh "$GOTCHI_ADDR" "ping $YOUR_DNS -c 4"
ssh "$GOTCHI_ADDR"
