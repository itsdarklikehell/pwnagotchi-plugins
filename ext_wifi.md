# Pwnagotchi External Wifi Adapter Plugin for Raspberry Pi Zero

## NOTE: This is still a work in progress

Add the following to your config.toml:
```
main.plugins.ext_wifi.enabled = true
main.plugins.ext_wifi.interface = "wlan0"
main.plugins.ext_wifi.mode = "external"
```
Change main.plugins.ext_wifi.mode to "internal" to swap back to the internal WiFi.

At the moment you must reboot your Pwnagotchi after enabling the plugin in order to restart the services. Will fix this later. 

Todo:
-Add setting for internal interface name
-Reset services after enabling the plugin if necessary

