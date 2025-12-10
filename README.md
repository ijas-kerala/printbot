# 🤖 PrintJoy Machine (PrintBot V2)

A joyful, complete printing vending machine software stack for Raspberry Pi.

## 🌟 Features

*   **Playful Kiosk UI**: KivyMD touchscreen interface with "Printo" mascot.
*   **Mobile Web Flow**: QR code upload, page selection, and payment (Tailwind/DaisyUI).
*   **Payment System**: Razorpay UPI integration (with Dev/Mock mode).
*   **Robust Printing**: PyMuPDF page slicing and CUPS integration.
*   **Admin Dashboard**: Secure pattern-lock login, revenue stats, and live pricing.

## 🛠️ Installation

1.  **Clone & Setup**:
    ```bash
    git clone <repo>
    cd printbot1
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    ```

2.  **Configuration**:
    Copy `.env.example` to `.env` and fill in your keys.
    ```bash
    cp .env.example .env
    nano .env
    ```
    *If no Razorpay keys are provided, the system runs in MOCK Payment mode.*

3.  **Launch**:
    ```bash
    ./launch.sh
    ```

## 📂 Project Structure

*   `kiosk/`: Touchscreen application (Python/KivyMD).
*   `web/`: Backend APIs and Mobile Web Templates (FastAPI).
*   `core/`: Shared config and database.
*   `b_process/`: Background job processing.

## 🛡️ Admin Access

*   URL: `/admin/login`
*   Pattern: "Z" shape (1-2-3-5-7-8-9)
*   Default PIN: `1234`
-ready printing vending machine solution for Raspberry Pi 4. Features a Kivy touchscreen UI, mobile-friendly file upload (HTMX/Tailwind), automatic pricing, Razorpay UPI integration, and CUPS printing.

## Features
- **Touchscreen UI**: Kivy-based "Attract Mode" with status updates.
- **Mobile Upload**: Scan QR code to open a local web app for file upload.
- **Format Support**: PDF, DOCX, JPG, PNG (auto-converted to PDF).
- **Payment**: Dynamic Razorpay UPI QR code generation and polling.
- **Admin Dashboard**: Secure stats, revenue charts, job logs, and pricing editor.
- **Reliability**: Queue management, auto-retry, and systemd service integration.

## Hardware Requirements
- **Raspberry Pi 4 (or 5)** with Raspberry Pi OS (Bookworm 64-bit recommended).
- **Touchscreen**: Waveshare 7-inch HDMI/DSI or official Pi display.
- **Printer**: Canon ImageCLASS LBP122dw (or any IPP/Apple AirPrint compatible printer supported by CUPS).
- **Internet**: WiFi or Ethernet (for Razorpay API and Cloudflare Tunnel).

## Installation

### 1. System Dependencies
Run the following commands on your Raspberry Pi:

```bash
sudo apt-get update
sudo apt-get install -y python3-venv libcups2-dev cups libreoffice-writer libreoffice-java-common default-jre libopenjp2-7 libxml2-dev libxslt-dev cloudflared
```

### 2. Project Setup
Clone the repository (if not already done) and set up the environment:

```bash
cd /home/ijas/printbot1
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. Configuration
Copy the example environment file and edit it:

```bash
cp .env.example .env
nano .env
```
Fill in your details:
- `RAZORPAY_KEY_ID` & `RAZORPAY_KEY_SECRET`: From Razorpay Dashboard.
- `CLOUDFLARE_TUNNEL_TOKEN`: From Cloudflare Zero Trust Dashboard.
- `PRINTER_NAME`: Exact name of the printer in CUPS (run `lpstat -p` to see names).

### 4. Printer Setup
Add your printer to CUPS:
1. Open browser to `http://localhost:631` on the Pi (or remote IP).
2. Administration -> Add Printer.
3. Select your local or network printer (Canon LBP122dw).
4. Name it `Canon_LBP122dw` (must match `.env`).
5. Set default options (A4, etc.).

### 5. Cloudflare Tunnel
To expose the local web server to the internet securely (allowing users to upload from their phones), we use Cloudflare Tunnel.

**See [SETUP.md](SETUP.md) for detailed instructions on how to set up the tunnel and system services.**

Briefly:
```bash
# Install
./scripts/setup_cloudflared.sh

# Configure (See SETUP.md for Token method recommended for production)
cloudflared tunnel login
cloudflared tunnel create printbot
```

## Running the Application

### Manual Run (Testing)
You need two terminals (or use screen/tmux):

**Terminal 1 (Backend):**
```bash
source venv/bin/activate
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

**Terminal 2 (Kivy UI):**
```bash
source venv/bin/activate
# If over SSH, you need to export display:
export DISPLAY=:0
python kivy_app.py
```

### Auto-Start Service (Production)
Enable systemd services to start on boot.

1. Copy service files:
```bash
sudo cp printbot-backend.service /etc/systemd/system/
sudo cp printbot-kivy.service /etc/systemd/system/
```

2. Reload and Enable:
```bash
sudo systemctl daemon-reload
sudo systemctl enable printbot-backend
sudo systemctl enable printbot-kivy
sudo systemctl start printbot-backend
sudo systemctl start printbot-kivy
```

## Admin Dashboard
- URL: `http://<PI_IP>:8000/admin` (or via Tunnel URL /admin)
- Default Credentials: `admin` / `password123` (Change in `app/routers/admin.py` or impl DB auth).

## Troubleshooting
- **Kivy Error "Unable to get a Window"**: Ensure you are running on the desktop environment or have proper EGL/SDL2 drivers. fast way: `export DISPLAY=:0`.
- **Printer Error**: Check `tail -f /var/log/cups/error_log`.
- **Payment Not Detected**: Check Razorpay Webhook or Polling status in `app/services/razorpay_service.py`.

## File Structure
- `app/`: Main FastAPI application.
  - `core/`: DB and Config.
  - `models/`: SQLAlchemy models.
  - `routers/`: API endpoints (Upload, Settings, Admin).
  - `services/`: Business logic (Printer, Razorpay).
  - `templates/`: HTML (Jinja2) templates.
- `gui/`: Kivy assets.
- `kivy_app.py`: Touchscreen application entry point.
- `scripts/`: Helper scripts.

License: MIT
