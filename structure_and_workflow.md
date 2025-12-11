# PrintJoy System Architecture

## 📂 Project Structure

### Root Directory
- **`launch.sh`**: The main entry point. Starts both the FastAPI Backend and the Kiosk UI.
- **`README.md`**: General project information and quick start guide.
- **`SETUP.md`**: Detailed installation and configuration instructions (especially for Cloudflare Tunnel).
- **`.env`**: Configuration file for environment variables (API keys, Printer Name, etc.).
- **`printbot.db`**: SQLite database storing jobs, payments, and pricing rules.

### `web/` - Backend Application (FastAPI)
This is the core of the system, handling business logic, database interactions, and the mobile web interface.
- **`main.py`**: Entry point for the FastAPI server (`web.main:app`). Initializes the app and background workers.
- **`routers/`**: API endpoints.
    - `upload.py`: Handles file uploads from the mobile web app.
    - `print_settings.py`: Manages print configuration (copies, range) and pricing.
    - `payment.py` / `webhooks.py`: Manages Razorpay interactions.
    - `admin.py`: Secure admin dashboard endpoints.
    - `status.py`: Endpoint for the Kiosk to poll machine status.
- **`services/`**: logic.
    - `printer_service.py`: Handles file conversion (LibreOffice/Img2PDF) and CUPS printing (pycups).
    - `razorpay_service.py`: Payment gateway integration.
- **`templates/`**: HTML/Jinja2 templates for the mobile web app and admin dashboard.
- **`static/`**: CSS (Tailwind/DaisyUI), JS, and images for the web app.

### `kiosk/` - Touchscreen Application (KivyMD)
The "Face" of the machine running on the Raspberry Pi touchscreen.
- **`main.py`**: Entry point for the Kivy app.
- **`screens.py`**: Defines the different UI screens (Attract, Connect, Status).
- **`mascot.py`**: Code for the animated "Printo" character.
- **`assets/`**: Images and fonts for the Kiosk UI.

### `core/` - Shared Resources
- **`config.py`**: Environment variable loading.
- **`database.py`**: SQLAlchemy database connection setup.

## 🔄 System Workflow

### 1. User Interaction (Kiosk)
- The Kiosk app (`kiosk/main.py`) runs in a loop, displaying the "Attract Screen".
- It displays a **static QR code** saved on the device (pointing to the Cloudflare Tunnel URL).
- It constantly looks for status updates from the backend via `http://localhost:8000/status`.

### 2. Mobile Flow (Web)
1.  **Scan**: User scans the QR code and lands on `https://print.yourdomain.com` (served by `web/`).
2.  **Upload**: User uploads a file (PDF, Docx, Image).
    - Backend (`web/routers/upload.py`) saves the file to `uploads/` and creates a `Job` record (status: `PENDING`).
3.  **Configure**: User selects print options (Copies, Simplex/Duplex).
    - Backend calculates price.
4.  **Pay**: User clicks "Pay".
    - Backend (`web/services/razorpay_service.py`) generates a UPI QR code string.
    - User completes payment on their phone.
5.  **Verify**: Razorpay sends a Webhook to the Backend.
    - Backend updates `Job` status to `PAID`.

### 3. Printing Process
- A background worker (started in `web/main.py`) watches for jobs with status `PAID`.
- When found:
    1.  **Conversion**: `web/services/printer_service.py` converts the file to PDF if needed.
    2.  **Print**: The file is sent to the local CUPS print queue using `pycups`.
    3.  **Update**: Job status updated to `PRINTING` -> `COMPLETED`.
    4.  **Feedback**: The Kiosk polls this status and shows a "Printing..." animation to the user.
