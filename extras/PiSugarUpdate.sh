#!/bin/bash

set -e

TEMPDIR=$(mktemp -d /tmp/pisugar-update.XXXXXXX)
mkdir -p $TEMPDIR

function cleanup() {
    rm -rf $TEMPDIR
}
trap cleanup ERR

if which dpkg > /dev/null; then
    # Download fireware and programmer
    wget -O $TEMPDIR/pisugar-3-application.bin https://cdn.pisugar.com/release/PiSugar3Firmware/fm33lc023n/pisugar-3-application.bin

    # Install programmer
    if ! which pisugar-programmer > /dev/null; then
        wget -O $TEMPDIR/pisugar-programmer_1.6.4_armhf.deb https://cdn.pisugar.com/release/pisugar-programmer_1.6.4_armhf.deb
        sudo dpkg -i $TEMPDIR/pisugar-programmer_1.6.4_armhf.deb
    fi

    # Stop pisugar-server
    if which pisugar-server > /dev/null; then
        echo "Stoping pisugar-server..."
        sudo systemctl stop pisugar-server
    fi

    # Upgrade firmware
    echo y | pisugar-programmer -r $TEMPDIR/pisugar-3-application.bin
    
    # Wait until pisugar is ready
    echo "Wait for 10 seconds"
    sleep 10

    # Enable pisugar-server
    if which pisugar-server > /dev/null; then
        echo "Starting pisugar-server..."
        sudo systemctl start pisugar-server
    fi

    # Upgrade success
    echo "Upgrade complete!"
else
    echo "You need to manually download the fireware and upgrade the pisugar: "
    echo "Fireware url: https://cdn.pisugar.com/release/PiSugar3Firmware/fm33lc023n/pisugar-3-application.bin"
    echo "Programmer url: https://cdn.pisugar.com/release/pisugar-programmer_1.6.4_armhf.deb"
fi

echo "If you need help, visit https://github.com/PiSugar/"

cleanup