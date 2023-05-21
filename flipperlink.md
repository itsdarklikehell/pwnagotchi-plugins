# FlipperLink
Pwnagotchi plugin for interfacing with the Flipper Zero via bluetooth

# Active Development
Currently, the plugin will connect to the Flipper Zero as long as the user has previously used bluetoothctl to pair the pwnagotchi with the Flipper Zero. Once the plugin is turned on, it will begin trying to connect to the Flipper and update the pwnagotchi screen with a message that shows whether or not the connection is currently active.

# Current Features:
-   Provide interface to show whether or not the Flipper was able to be successfully connected to by the pwnagotchi device.
    + Need to add a variable that the user will provide the mac address of their Flipper to in the pwnagotchi config file

# Upcoming Features:
**Switching the bluetooth connection to a proper process instead of the janky proof of concept CLI command I started with through bluetoothctl. 

-   Once connection is established, Pwnagotchi will be able to communicate with the Flipper Zero to download yet to be defined files from the device in order to provide processing to discovered signals and turn them into usable/repeatable files for the Flipper Zero.
-   Display statistics from the Flipper Zero of some sort, number of captured signals? Number of IR Remotes? Have not made up my mind yet which direction to go with this yet and I am open to ideas. Will be dependent on what data is accessible via the Bluetooth connection with the flipper but it should be pretty open ended given how the app works on mobile devices.
