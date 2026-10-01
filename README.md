# pwnagotchi-plugins

<img src="https://img.shields.io/github/stars/itsdarklikehell/pwnagotchi-plugins?style=flat-square&color=blue" alt="Stars">
<img src="https://img.shields.io/github/forks/itsdarklikehell/pwnagotchi-plugins?style=flat-square&color=green" alt="Forks">
<img src="https://img.shields.io/github/license/itsdarklikehell/pwnagotchi-plugins?style=flat-square" alt="License">
<img src="https://img.shields.io/github/actions/workflow/status/itsdarklikehell/pwnagotchi-plugins/ci.yml?branch=main&label=CI&style=flat-square" alt="CI Status">

Collectie van Pwnagotchi-plugins voor Wi-Fi auditing en pentesting op Raspberry Pi.

De Pwnagotchi is een AI-geoptimaliseerde Wi-Fi analyse tool die bettercap gebruikt voor handshake capture, monitor mode, en automatische aanvallen. Deze plugin-collectie breidt de standaard functionaliteit uit met extra features voor GPS-tracking, handshake upload, weergaves, en systeembeheer.

## Installatie

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

## Gebruik

Na installatie kunnen plugins geactiveerd worden via:

```bash
sudo pwnagotchi plugins enable <plugin-naam>
sudo pwnagotchi plugins disable <plugin-naam>
sudo pwnagotchi plugins list
```

Zie de [plugin-tabel](PLUGIN_TABLE.md) voor een overzicht van beschikbare plugins.

## Testen

Dit repository bevat een pytest-testframework dat alle plugins valideert op syntax, imports, structuur en configuratie.

```bash
pip install pytest
pytest tests/ -v
```

| Categorie | Aantal | Status |
|-----------|--------|--------|
| Syntax validatie | 198 | ✅ Alle plugins parseren correct |
| Import validatie | 198 | ✅ Alle modules laden |
| Structuur validatie | 198 | ✅ Plugin-classen gevonden |
| Config validatie | 120 | ✅ TOML-bestanden geldig |
| **Totaal** | **1977 passed** | **✅ 0 failed** |

## Bijdragers

- [itsdarklikehell](https://github.com/itsdarklikehell) — Onderhouder
- [evilsocket](https://github.com/evilsocket) — Pwnagotchi creator
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

## Licentie

MIT — zie [LICENSE](LICENSE) voor details.

## Ontwikkeltijdlijn

<video src="https://raw.githubusercontent.com/itsdarklikehell/pwnagotchi-plugins/master/gource.mp4" controls width="100%"></video>

## Credits

Special thanks go to:

- [Pwnagotchi Unofficial](https://github.com/Pwnagotchi-Unofficial)
- [pwnagotchi.org](https://pwnagotchi.org/)
