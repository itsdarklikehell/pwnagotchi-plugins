
# ! WIP the plugin is actually available for testing !
# Fancytools - Official Installer for Fancygotchi 

[Fancygotchi](https://github.com/Pwnagotchi-Unofficial/pwnagotchi-fancygotchi) is now an integral part of the Pwnagotchi, and Fancytools serves as its official installer. This plugin enhances the installation experience for Fancygotchi and introduces additional developer/debug tools along with a streamlined process to install various useful utilities.

## Installation  

### General  

- Download the code and paste the fancytools.py, fancyserver.py and the fancytools folder inside your custom plugins folder. (default folder path: `/usr/local/share/pwnagotchi/custom-plugins`)
- Restart the pwnagotchi.  
- Go to the web UI plugin page.
- Click on the enable button and refresh the page.
- The Fancytools web UI page is now available.

### Terminal  

- The first web UI table is the Terminal page.
- Internet is needed for the installation. The requirements will be installed, cmake is not always available on the base image.  
- Click on the install button.  
- Accept the confirmation pop-up and wait for the success pop-up. (the full install can take a while, be patient)  
- Wait for the page refresh.  

- Now you have a new button and the service status.  
- Click on the start button to start the ttyd service.  
- Wait for the success pop-up.  
- Wait for the page refresh.  
- The terminal is now available and you can stop the service to save ressources.  

### Fancygotchi  

- Go to the Fancygotchi tab.
- Click on the install button.
- Accept the confirmation pop-up and wait for the success pop-up.
- Wait for the pwnagotchi restart.
- The new face will appear on the screen.

### Dev  

The tool is now linked to the web UI for now, but it is accessible by the terminal.  

- Go to the terminal.
- The next command are availlable:
```
# To prompt the help manual:
fanncytools -h
# To prompt a system anonymized system report:
fancytools -d
# To enable a plugin:
fancytools -p plugin_name -e to enable
# To disable a plugin:
fancytools -p plugin_name
```
[11:45 AM]
this is my mod of his plugin, to add the command to the plugin:



- The options in the config.toml should look like this for Fancygotchi (I will add a code to integrate it on fancygotchi install):
```
fancygotchi.theme = "pwnachu"
fancygotchi.rotation = 0
```


## Features

### Fancygotchi Integration

Fancytools is the official installer for Fancygotchi, making it seamless for users to incorporate Fancygotchi into their Pwnagotchi environment.

### Developer/Debug Tools

- **Dev Menu:** Access a developer menu with diagnostic tools for troubleshooting and advanced configuration.

- **Terminal into Web UI:** Gain terminal access directly into the Fancygotchi web UI for real-time interaction and debugging.

### Auto Installation of Useful Tools

Fancytools includes an automated process to install additional useful tools, enhancing the capabilities of your Pwnagotchi environment.

## Usage

1. Navigate to the Pwnagotchi web UI.
2. Go to the plugins page.
3. Locate the Fancytools section in the menu and enable it.
4. Refresh the page and click Fancytools.
5. Explore the available options, including Fancygotchi installation, developer tools, and more.

## License

This project is licensed under the GNU General Public License v3.0.

## Acknowledgments

- Thanks to the Pwnagotchi community for their support and collaboration.

---

**Note:** Fancygotchi is now an integral part of Pwnagotchi, and Fancytools simplifies its installation process while offering additional developer/debug tools. Stay tuned for upcoming updates as Fancygotchi will be embedded directly into new Pwnagotchi images.

For more details, visit the [Fancygotchi GitHub repository](https://github.com/Pwnagotchi-Unofficial/pwnagotchi-fancygotchi).
