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
*   `structure_and_workflow.md`: Detailed architecture guide.

## 🛡️ Admin Access

*   URL: `/admin/login`
*   Pattern: "Z" shape (1-2-3-5-7-8-9)
*   Default PIN: `1234`

## Running the Application

### Manual Run (Testing)
You need two terminals (or use screen/tmux):

**Terminal 1 (Backend):**
```bash
source venv/bin/activate
uvicorn web.main:app --host 0.0.0.0 --port 8000
```

**Terminal 2 (Kiosk UI):**
```bash
source venv/bin/activate
# If over SSH, you need to export display:
export DISPLAY=:0
python kiosk/main.py
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
- Default Credentials: `admin` / `password123` (Change in `web/routers/admin.py` or impl DB auth).

## Troubleshooting
- **Kivy Error "Unable to get a Window"**: Ensure you are running on the desktop environment or have proper EGL/SDL2 drivers. fast way: `export DISPLAY=:0`.
- **Printer Error**: Check `tail -f /var/log/cups/error_log`.
- **Payment Not Detected**: Check Razorpay Webhook or Polling status in `web/services/razorpay_service.py`.

License: MIT

## 🚀 Deployment on New Devices

Follow these steps to deploy "PrintJoy" on a fresh Raspberry Pi or Linux machine.

### 1. System Requirements & Permissions
*   **OS**: Raspberry Pi OS (Bullseye/Bookworm) or Ubuntu.
*   **User Groups**: The user must have permission to access printers and input devices.
    ```bash
    sudo usermod -a -G lp,input,video $USER
    ```
*   **Dependencies**: Ensure system dependencies for Kivy/SDL2 are installed.
    ```bash
    sudo apt install python3-pip python3-venv libsdl2-dev libsdl2-image-dev libsdl2-mixer-dev libsdl2-ttf-dev libportmidi-dev libswscale-dev libavformat-dev libavcodec-dev zlib1g-dev libgstreamer1.0-gstreamer-plugins-base libgstreamer1.0-dev
    ```
*   **Directory Ownership**: Ensure the user running the app owns the project directory.
    ```bash
    sudo chown -R $USER:$USER /path/to/printbot1
    ```

### 2. Environment Variables
Create a `.env` file in the project root.
| Variable | Description | Default/Example |
| :--- | :--- | :--- |
| `RAZORPAY_KEY_ID` | Razorpay API Key | `rzp_test_...` |
| `RAZORPAY_KEY_SECRET` | Razorpay Secret | `YOUR_SECRET` |
| `ADMIN_PIN` | Dashboard Access PIN | `1234` |
| `ENV` | Environment Mode | `development` / `production` |

### 3. Kiosk Hardening (Raspberry Pi)
The application automatically defaults `DISPLAY` to `:0`.
If using the official RPi Touchscreen, ensure `dtoverlay=vc4-kms-v3d` is in `/boot/config.txt`.

### 4. Testing Checklist
- [ ] **Startup**: Run `./launch.sh`. Verify "Mascot" appears.
- [ ] **Logging**: Check `logs/crash.log` is created.
- [ ] **Printer**: Ensure CUPS is running (`localhost:631`) and default printer is set.
- [ ] **Payment**: Scan QR code on specific test page to verify Razorpay mock/live mode.
