import os
import qrcode
import threading
import requests
import time
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.popup import Popup
from kivy.lang import Builder
from kivy.properties import StringProperty
from kivy.clock import Clock
from kivy.core.window import Window

# Define KV path
KV_FILE = os.path.join(os.path.dirname(__file__), 'gui', 'kv', 'main.kv')
Builder.load_file(KV_FILE)

# Configuration
API_URL = "http://localhost:8000"
TUNNEL_URL = "https://your-tunnel.trycloudflare.com" # TODO: Fetch dynamically or from env
ADMIN_PIN = "1234"

class AdminPopup(Popup):
    def verify_pin(self, pin):
        if pin == ADMIN_PIN:
            import webbrowser
            webbrowser.open(f"{API_URL}/admin") # Placeholder for admin route
            self.dismiss()
        else:
            self.ids.pin_input.text = ""
            self.ids.pin_input.hint_text = "Wrong PIN"

class MainScreen(Screen):
    status_text = StringProperty("Initializing...")
    qr_code_path = StringProperty("static_qr.png")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.generate_static_qr()
        # Start polling
        Clock.schedule_interval(self.update_status, 2)

    def generate_static_qr(self):
        # Generate a QR that points to the tunnel URL
        # We save it to a file so Kivy can load it
        qr = qrcode.make(TUNNEL_URL)
        qr.save("static_qr.png")
        self.qr_code_path = "static_qr.png"

    def update_status(self, dt):
        try:
            # Run in a separate thread to avoid blocking UI? 
            # Requests is blocking, so strictly yes, but for local 5ms req, 
            # we might get away with it or use UrlRequest.
            # For simplicity in this demo, we'll just do it specific thread or non-blocking way.
            # Using threading to be safe.
            threading.Thread(target=self._fetch_status).start()
        except Exception:
            self.status_text = "Status Error"

    def _fetch_status(self):
        try:
            res = requests.get(f"{API_URL}/machine-status", timeout=2)
            if res.status_code == 200:
                data = res.json()
                # Update UI on main thread
                Clock.schedule_once(lambda dt: self._set_status(data['status']))
            else:
                 Clock.schedule_once(lambda dt: self._set_status("Backend Unreachable"))
        except:
             Clock.schedule_once(lambda dt: self._set_status("Connection Error"))

    def _set_status(self, text):
        self.status_text = text

    def open_admin_login(self):
        popup = AdminPopup()
        popup.open()

class PrintBotApp(App):
    def build(self):
        # Window settings for Pi Touchscreen
        # Window.fullscreen = 'auto' # Commented out for dev/testing
        sm = ScreenManager()
        sm.add_widget(MainScreen(name='main'))
        return sm

if __name__ == '__main__':
    PrintBotApp().run()
