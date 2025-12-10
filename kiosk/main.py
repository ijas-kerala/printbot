import os
import sys
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager
from kivymd.app import MDApp
from kivymd.uix.transition import MDFadeSlideTransition
from kivy.clock import Clock
import requests
from requests.exceptions import RequestException

# Add project root to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from kiosk.screens import AttractScreen, ConnectScreen, StatusScreen
from kiosk.mascot import MascotWidget

class PrintJoyApp(MDApp):
    def build(self):
        self.theme_cls.theme_style = "Light"
        self.theme_cls.primary_palette = "Indigo"
        self.theme_cls.accent_palette = "Pink"
        self.title = "PrintJoy"
        self.icon = "kiosk/assets/icon.png"

        # Screen Manager
        sm = ScreenManager(transition=MDFadeSlideTransition())
        sm.add_widget(AttractScreen(name='attract'))
        sm.add_widget(ConnectScreen(name='connect'))
        sm.add_widget(StatusScreen(name='status'))
        
        return sm

    def on_start(self):
        # Start polling for status updates
        Clock.schedule_interval(self.check_status, 3.0)

    def check_status(self, dt):
        """
        Poll the backend for the latest status.
        Use a lightweight endpoint that returns the current machine state.
        """
        try:
            # In production, this URL should be configurable or discovered
            response = requests.get("http://127.0.0.1:8000/status", timeout=1)
            if response.status_code == 200:
                data = response.json()
                self.handle_status_update(data)
        except RequestException:
            # Backend might be down or starting up
            pass

    def handle_status_update(self, data):
        """
        State Machine Logic:
        - idle -> AttractScreen
        - uploading -> ConnectScreen
        - printing -> StatusScreen
        """
        current_screen = self.root.current
        new_state = data.get("state", "idle")
        
        # Simple State Transition Mapping
        state_map = {
            "idle": "attract",
            "uploading": "connect",
            "printing": "status"
        }
        
        target_screen = state_map.get(new_state, "attract")
        
        if current_screen != target_screen:
            self.root.current = target_screen
            
        # Update specific screen data if needed
        if new_state == "printing" and "progress" in data:
            # TODO: Update StatusScreen progress bar
            pass

if __name__ == '__main__':
    PrintJoyApp().run()
