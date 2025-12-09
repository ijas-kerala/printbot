Here is a breakdown of the file structure for your PrintBot Vending Machine:

📂 Root Directory

.env.example: Template for environment variables. You copy this to .env and fill in your secrets (Razorpay keys, Database URL, Printer Name, etc.).

requirements.txt: List of all Python libraries needed (FastAPI, sqlalchemy, razorpay, kivy, pycups, etc.).

kivy_app.py: The entry point for the Touchscreen Interface. This runs the Kivy app that shows the big QR code and status on the Raspberry Pi screen.

README.md: The master instruction manual. Contains installation steps, hardware setup, and troubleshooting tips.
printbot-backend.service  & printbot-kivy.service: Systemd configuration files to automatically start the backend and the screen UI when the Raspberry Pi boots up.

📂 app/ (The Core Backend)

main.py: The heart of the web server. It starts FastAPI, connects to the database, launches the background print worker, and registers all the "routers" (URL endpoints).
core/config.py: Loads settings from your .env file so other parts of the app can use them safely.
database.py: Handles variables and connections to the SQLite database.
models/models.py: Defines the database tables:Job (print jobs),PricingRule (costs), and Payment (transaction records).

📂 app/routers/ (URL Endpoints)

upload.py: Handles the file upload page (/upload). Saves files to the uploads/ folder and creates a "Job" in the database.
print_settings.py: Handles file configuration (/settings). logic for calculating price (Copies × Pages × Price) and generating the Razorpay Payment Link/QR.
status.py: A simple API (/machine-status) that the Kivy app asks "Are you printing?" every few seconds.
admin.py: The secure Admin Dashboard (/admin). Handles login, charts, and price updates.

📂 app/services/ (Business Logic)

razorpay_service.py: Talks to Razorpay. Generates the payment links/QR codes and checks if a payment has been made.
printer_service.py: The heavy lifter.
Converts files (DOCX, Images) to PDF using LibreOffice/Img2PDF.
Talks to CUPS (via pycups) to actually send the data to the Canon printer with specific settings (Duplex, A4, etc.).
job_worker.py: A background loop that constantly watches for "PAID" jobs and sends them to the printer_service.

📂 app/templates/ (Web Frontend)

base.html: The master layout (header, footer, loaded scripts like Tailwind/HTMX) shared by all pages.
index.html: The mobile-friendly Upload page.
settings.html: The Print Options page (copies, simplex/duplex).
pay.html: Displays the QR code to the user and polls for success.
admin_dashboard.html: The protected admin panel with charts and tables.
admin_login.html: Simple login screen for the admin.

📂 gui/

kv/main.kv: The design file for the Kivy Touchscreen App (colors, button positions, text size).

📂 scripts/

cleanup.py: A maintenance script to delete old uploaded files so the SD card doesn't fill up.
setup_cloudflared.sh: Helper helper to install the Cloudflare Tunnel software.

📂 Tests

test_agent*.py: Scripts verifying each "phase" of the build (Database, Web UI, Kivy, Printing, Admin). Useful for debugging if something breaks.

