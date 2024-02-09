#!/bin/bash

SWAP_FILE="/swap"
SWAP_SIZE="2G"

# Check if swap is already mounted
if [ "$(sudo swapon -s | grep -o "$SWAP_FILE")" = "$SWAP_FILE" ]; then
    # Swap is already mounted, let's disable it first
    sudo swapoff "$SWAP_FILE"
    echo "Existing swap file '$SWAP_FILE' is unmounted."
fi

# Check if the swap file exists
if [ ! -f "$SWAP_FILE" ]; then
    # Create an empty file with the desired size for the swap file
    sudo fallocate -l "$SWAP_SIZE" "$SWAP_FILE"

    # Set the correct permissions for the swap file
    sudo chmod 600 "$SWAP_FILE"

    # Mark the file as a swap area
    sudo mkswap "$SWAP_FILE"
fi

# Enable the newly created swap file
sudo swapon "$SWAP_FILE"

# Make the swap file mount persist across reboots by adding it to /etc/fstab
if ! grep -q "$SWAP_FILE" /etc/fstab; then
    echo "$SWAP_FILE none swap sw 0 0" | sudo tee -a /etc/fstab
fi

echo "Swap file '$SWAP_FILE' created and activated with size '$SWAP_SIZE'."
# Verify system-wide swap usage
free -h
