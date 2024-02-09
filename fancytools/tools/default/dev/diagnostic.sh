#!/bin/bash

# Get the script's directory
script_dir=$(dirname "$(readlink -f "$0")")

# Output file in the script's directory
output_file="$script_dir/system_info.txt"

# Pwnagotchi version
echo "Pwnagotchi version:" > "$output_file"
pip list | grep pwnagotchi >> "$output_file"
echo >> "$output_file"

# Kernel info
echo "Kernel info:" >> "$output_file"
uname -a >> "$output_file"
echo >> "$output_file"

# Boot config
echo "Boot config:" >> "$output_file"
cat /boot/cmdline.txt >> "$output_file"
echo >> "$output_file"
cat /boot/config.txt >> "$output_file"
echo >> "$output_file"

# Service status
echo "Service status:" >> "$output_file"
service pwnagotchi status >> "$output_file"
echo >> "$output_file"

# Network driver interface load
echo "Network driver interface load:" >> "$output_file"
sudo dmesg | grep brcm >> "$output_file"
echo >> "$output_file"

# List all IP active host names
echo "List all IP active host names:" >> "$output_file"
hostname -I >> "$output_file"
echo >> "$output_file"

echo "List all active ports:" >> "$output_file"
lsof -nP -iTCP -sTCP:LISTEN >> "$output_file"
echo >> "$output_file"

# List available plugins
echo "List available plugins:" >> "$output_file"
cat /etc/pwnagotchi/config.toml | grep plugin | grep enabled >> "$output_file"
echo >> "$output_file"

# List enabled plugins
echo "List enabled plugins:" >> "$output_file"
cat /etc/pwnagotchi/config.toml | grep plugin | grep enabled | grep true >> "$output_file"
echo >> "$output_file"

# Log file
log_file="/var/log/pwnagotchi.log"

# Config file
config_file="/etc/pwnagotchi/config.toml"

# Output files in the script's directory
log_output_file="$script_dir/anonymized_log.txt"
config_output_file="$script_dir/anonymized_config.toml"



# Anonymize and export the last 100 lines of the log file to a file
echo "Anonymized log (last 100 lines):"
tail -n 100 "$log_file" | sed -E -e 's/([0-9]{1,3}\.){3}[0-9]{1,3}/XX.XX.XX.XX/g' -e 's/([0-9A-Fa-f]{2}:){5}[0-9A-Fa-f]{2}/XX:XX:XX:XX:XX:XX/g' -e '/api_key/ s/=.*$/= "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"/' -e '/whitelist/ {s/=.*/= \[\]/; :loop n; /\]/! {s/^[[:space:]]*["'"'"'].*["'"'"'],?//; s/^[[:space:]]*\][[:space:]]*$//; b loop}}' -e '/password/ s/=.*$/= "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"/' -e 's/@[^()]*()/@XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX/' > "$log_output_file"

# Anonymize and export the config file to a file
echo -e "\nAnonymized config file:"
sed -E -e 's/([0-9]{1,3}\.){3}[0-9]{1,3}/XX.XX.XX.XX/g' -e 's/([0-9A-Fa-f]{2}:){5}[0-9A-Fa-f]{2}/XX:XX:XX:XX:XX:XX/g' -e '/api_key/ s/=.*$/= "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"/' -e '/whitelist/ {s/=.*/= \[\]/; :loop n; /\]/! {s/^[[:space:]]*["'"'"'].*["'"'"'],?//; s/^[[:space:]]*\][[:space:]]*$//; b loop}}' -e '/password/ s/=.*$/= "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"/' "$config_file" > "$config_output_file"
cat $output_file
cat $log_output_file
cat $config_output_file

echo "Basic system info saved to $output_file"
echo "Anonymized log saved to $log_output_file"
echo "Anonymized config saved to $config_output_file"
