# PrintBot Setup & Deployment Guide

This guide provides detailed instructions on how to set up the PrintBot Print Vending Machine, specifically focusing on the Cloudflare Tunnel configuration for remote access and running the application on your Raspberry Pi.

## 1. Prerequisites

- **Hardware**: Raspberry Pi 4 OR 5 recommended.
- **OS**: Raspberry Pi OS (Bookworm 64-bit recommended).
- **Network**: Stable Internet connection (WiFi or Ethernet).
- **Domain**: A domain name managed on Cloudflare (required for Tunnel).

## 2. Initial Installation
Run the automated setup commands if you haven't already:

```bash
# Update System
sudo apt-get update && sudo apt-get upgrade -y

# Install System Dependencies
sudo apt-get install -y python3-venv libcups2-dev cups libreoffice-writer libreoffice-java-common default-jre libopenjp2-7 libxml2-dev libxslt-dev

# Install Cloudflared
./scripts/setup_cloudflared.sh
```

## 3. Cloudflare Tunnel Setup

To allow users to upload files from their phones without being on the same local WiFi, we use Cloudflare Tunnel. This exposes the local web server (`localhost:8000`) to the internet securely.

### Option A: Dashboard Method (Recommended for Ease)

1.  **Login to Cloudflare Zero Trust Dashboard**:
    Go to [one.dash.cloudflare.com](https://one.dash.cloudflare.com/).
2.  Navigate to **Networks > Tunnels**.
3.  Click **Create a Tunnel**.
4.  Select **Cloudflared** connector.
5.  Name it `printbot-pi` (or similar) and save.
6.  **Install Connector**:
    - Choose your OS: **Debian** and Architecture: **arm64** (for Pi 4/5).
    - You will see a command starting with `sudo cloudflared service install ...`.
    - **Copy the Token**: The long string after `ey...`.
    - Paste this command into your Raspberry Pi terminal to install and start the tunnel service automatically.
    
    ```bash
    # Example (DO NOT COPY, USE YOURS FROM DASHBOARD):
    sudo cloudflared service install eyJhIjoiM...
    ```

7.  **Route Traffic (Public Hostname)**:
    - In the Tunnel configuration page (Next step).
    - **Public Hostname**: Choose a subdomain (e.g., `print.yourdomain.com`).
    - **Service**: `HTTP` -> `localhost:8000`.
    - Save.

8.  **Verify**:
    - Visit `https://print.yourdomain.com` on your phone. You should see the PrintBot upload page.

### Option B: CLI Method (Terminal Only)

1.  **Login**:
    ```bash
    cloudflared tunnel login
    ```
    This prints a URL. Open it in a browser on any computer, log in to Cloudflare, and authorize the domain.

2.  **Create Tunnel**:
    ```bash
    cloudflared tunnel create printbot
    ```
    This creates a JSON credentials file in `~/.cloudflared/`.

3.  **Configure**:
    Create a config file `~/.cloudflared/config.yml`:
    ```yaml
    tunnel: <Tunnel-UUID>
    credentials-file: /home/ijas/.cloudflared/<Tunnel-UUID>.json
    
    ingress:
      - hostname: print.yourdomain.com
        service: http://localhost:8000
      - service: http_status:404
    ```

4.  **Route DNS**:
    ```bash
    cloudflared tunnel route dns printbot print.yourdomain.com
    ```

5.  **Run**:
    ```bash
    cloudflared tunnel run printbot
    ```

## 4. Running the Application Services

To ensure the PrintBot runs automatically when the Pi turns on:

### 1. Configure Services
Copy the service files to the system directory:

```bash
sudo cp printbot-backend.service /etc/systemd/system/
sudo cp printbot-kivy.service /etc/systemd/system/
```

### 2. Enable and Start
```bash
sudo systemctl daemon-reload
sudo systemctl enable printbot-backend
sudo systemctl enable printbot-kivy

# Start them now
sudo systemctl start printbot-backend
sudo systemctl start printbot-kivy
```

### 3. Verification
Check the status of the services:
```bash
# Backend Status
sudo systemctl status printbot-backend

# Kiosk UI Status
sudo systemctl status printbot-kivy
```

## 5. Connecting from Other Devices

### Remote Access (Public Internet)
- Use the **Cloudflare Tunnel Domain** you set up (e.g., `https://print.yourdomain.com`).
- This is what users will scan via the QR code on the kiosk.

### Local Network Access (Same WiFi)
- Find your Pi's IP address: `hostname -I`
- Open `http://<PI_IP>:8000` in a browser.

## 6. Development vs Production
- **Development**: Update `.env` with `ENV=development` and run manually.
- **Production**: Update `.env` with `ENV=production`. Ensure `DEBUG=False`. Use systemd services.

