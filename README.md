# pwnagotchi-plugins

Collectie van Pwnagotchi-plugins voor Wi-Fi auditing en pentesting op Raspberry Pi.

De Pwnagotchi is een AI-geoptimaliseerde Wi-Fi analyse tool die bettercap gebruikt voor
handshake capture, monitor mode, en automatische aanvallen. Deze plugin-collectie breidt
de standaard functionaliteit uit met extra features voor GPS-tracking, handshake upload,
weergaves, en systeembeheer.

## Installatie

Zie de [Pwnagotchi-documentatie](https://pwnagotchi.org/) voor de basisinstallatie.
Plugins worden geladen vanuit `/usr/local/share/pwnagotchi/available-plugins/`.

### Snelle setup

```bash
git clone https://github.com/itsdarklikehell/pwnagotchi-plugins.git
cd pwnagotchi-plugins

# Kopieer plugins naar de Pwnagotchi plugin directory
sudo cp *.py /usr/local/share/pwnagotchi/available-plugins/

# Activeer gewenste plugins
sudo pwnagotchi plugins enable <plugin-naam>
```

### Installer script

```bash
sudo ./scripts/install-plugins.sh list
sudo ./scripts/install-plugins.sh gps
sudo ./scripts/install-plugins.sh all
```

## Ontwikkeltijdlijn

<video src="https://raw.githubusercontent.com/itsdarklikehell/pwnagotchi-plugins/master/gource.mp4" controls width="100%"></video>

## Plugins

Zie de [plugin-tabel](PLUGIN_TABLE.md) voor een overzicht van beschikbare plugins.

## Bijdragen

Zie [CONTRIBUTING.md](CONTRIBUTING.md) voor richtlijnen.

## Licentie

Zie [LICENSE](LICENSE) voor details.

## Credits

Special thanks go to:

- [Pwnagotchi Unofficial](https://github.com/Pwnagotchi-Unofficial)
- [pwnagotchi.org](https://pwnagotchi.org/)
- [evilsocket](https://github.com/evilsocket)
- [NeonLightning](https://github.com/NeonLightning)
- [V0rT3x](https://github.com/V0r-T3x)
- [Jayofellony](https://github.com/jayofelony)
- [Alumium-Ice](https://github.com/aluminum-ice)
- [Talking Sasquach](https://github.com/skizzophrenic/Talking-Sasquach)
- [NurseJackass / Sniffleupagus](https://github.com/Sniffleupagus)
- [WPA2](https://github.com/wpa-2)
- [S4ntr3ri4](https://github.com/s4ntr3ri4)
- [DylanJava](https://github.com/DylanJava)
- [Aleda](https://www.twitch.tv/aleda2112)
- [Dal](https://github.com/dal)
- [Rai](https://github.com/rai68)
- [Dj1ch](https://github.com/dj1ch)

and many others.
