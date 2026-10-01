#!/bin/bash
# install-plugins.sh — Interactive plugin installer for pwnagotchi-plugins
# Usage: ./install-plugins.sh [plugin_name|all]

set -euo pipefail

PLUGIN_DIR="/usr/local/share/pwnagotchi/available-plugins"
CONFIG_DIR="/etc/pwnagotchi/conf.d"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_DIR="$(dirname "$SCRIPT_DIR")"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

log() { echo -e "${GREEN}[+]${NC} $*"; }
warn() { echo -e "${YELLOW}[!]${NC} $*"; }
error() { echo -e "${RED}[-]${NC} $*"; exit 1; }

check_root() {
    if [ "$EUID" -ne 0 ]; then
        error "Dit script moet als root worden uitgevoerd (sudo)"
    fi
}

list_plugins() {
    log "Beschikbare plugins:"
    echo ""
    printf "%-30s %s\n" "NAAM" "BESCHRIJVING"
    printf "%-30s %s\n" "----" "------------"
    for py in "$REPO_DIR"/*.py; do
        [ -f "$py" ] || continue
        name=$(basename "$py" .py)
        desc=$(grep -m1 "__description__" "$py" 2>/dev/null | sed "s/__description__ *= *['\"]//;s/['\"]$//" || echo "Geen beschrijving")
        printf "%-30s %s\n" "$name" "$desc"
    done
}

install_plugin() {
    local plugin="$1"
    local py_file="$REPO_DIR/${plugin}.py"
    local toml_file="$REPO_DIR/configs/${plugin}.toml"
    
    if [ ! -f "$py_file" ]; then
        error "Plugin '$plugin' niet gevonden"
    fi
    
    log "Installeren van $plugin..."
    cp "$py_file" "$PLUGIN_DIR/"
    log "  ✓ Plugin gekopieerd naar $PLUGIN_DIR"
    
    if [ -f "$toml_file" ]; then
        cp "$toml_file" "$CONFIG_DIR/"
        log "  ✓ Config gekopieerd naar $CONFIG_DIR"
    fi
    
    log "Plugin '$plugin' geïnstalleerd!"
    warn "Activeer met: sudo pwnagotchi plugins enable $plugin"
}

install_all() {
    log "Alle plugins installeren..."
    for py in "$REPO_DIR"/*.py; do
        [ -f "$py" ] || continue
        name=$(basename "$py" .py)
        install_plugin "$name"
    done
    log "Alle plugins geïnstalleerd!"
}

main() {
    check_root
    
    case "${1:-}" in
        ""|-h|--help)
            echo "Gebruik: $0 [plugin_name|all|list]"
            echo ""
            echo "Opties:"
            echo "  plugin_name  Installeer een specifieke plugin"
            echo "  all          Installeer alle plugins"
            echo "  list         Toon beschikbare plugins"
            echo ""
            echo "Voorbeelden:"
            echo "  $0 gps"
            echo "  $0 all"
            echo "  $0 list"
            ;;
        list)
            list_plugins
            ;;
        all)
            install_all
            ;;
        *)
            install_plugin "$1"
            ;;
    esac
}

main "$@"
