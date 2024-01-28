# Plugin to use with Pwnagotchi and the PiSugar2.

## This plugin DOES require using the official [pisugar-power-manager-rs](https://github.com/PiSugar/pisugar-power-manager-rs) install. 

## Install guide:

```bash
# Go to the home directory
cd ~

# Install PiSugar Power Manager 
curl http://cdn.pisugar.com/release/Pisugar-power-manager.sh | sudo bash

# Download the plugin and support library
git clone https://github.com/PiSugar/pisugar2py.git
git clone https://github.com/PiSugar/pwnagotchi-pisugar2-plugin.git

#Make the installed-plugins directory if it doesn't already exist
sudo mkdir -p /usr/local/share/pwnagotchi/installed-plugins/

# This installs the pisugar2 package into your python library
sudo ln -s ~/pisugar2py/ /usr/local/lib/python3.11/dist-packages/pisugar2

# Installs the user-plugin
sudo ln -s ~/pwnagotchi-pisugar2-plugin/pisugar2.py /usr/local/share/pwnagotchi/installed-plugins/pisugar2.py


```


In /etc/pwnagotchi/config.toml add:
```toml
main.custom_plugins = "/usr/local/share/pwnagotchi/installed-plugins/"
main.plugins.pisugar2.enabled = true
main.plugins.pisugar2.shutdown = 5
main.plugins.pisugar2.sync_rtc_on_boot = true
```



PiSugar2 web settings are accessible at http://10.0.0.2:8421/#/

The support library exposes all of the available commands from the pi-sugar in a python library for developers
