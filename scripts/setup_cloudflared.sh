#!/bin/bash

# Check if cloudflared is installed
if ! command -v cloudflared &> /dev/null
then
    echo "cloudflared could not be found. Installing..."
    # Add Cloudflare gpg key
    sudo mkdir -p --mode=0755 /usr/share/keyrings
    curl -fsSL https://pkg.cloudflare.com/cloudflare-main.gpg | sudo tee /usr/share/keyrings/cloudflare-main.gpg >/dev/null

    # Add this repo to your apt repositories
    echo 'deb [signed-by=/usr/share/keyrings/cloudflare-main.gpg] https://pkg.cloudflare.com/cloudflared jammy main' | sudo tee /etc/apt/sources.list.d/cloudflared.list

    # install cloudflared
    sudo apt-get update && sudo apt-get install cloudflared
else
    echo "cloudflared is already installed."
fi

echo "To authenticate, run: cloudflared tunnel login"
echo "Then create a tunnel: cloudflared tunnel create printbot"
echo "Configure it to point to http://localhost:8000"
