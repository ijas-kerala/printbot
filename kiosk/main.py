import os
import sys
import time
from kivy.config import Config

# Reliability: Hardened UI Config
Config.set('graphics', 'cursor_visible', '0') # Hide mouse
Config.set('graphics', 'fullscreen', 'auto') # Force fullscreen
Config.set('input', 'mouse', 'mouse,multitouch_on_demand') # Disable red dots
Config.set('kivy', 'exit_on_escape', '0') # Disable ESC exit

from kivy.lang import Builder
from kivymd.uix.screenmanager import MDScreenManager
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
        try:
            self.theme_cls.theme_style = "Light"
            self.theme_cls.primary_palette = "Indigo"
            self.theme_cls.accent_palette = "Pink"
            self.title = "PrintJoy"
            self.icon = "kiosk/assets/icon.png"
    
            # Screen Manager
            sm = MDScreenManager(transition=MDFadeSlideTransition())
            sm.add_widget(AttractScreen(name='attract'))
            sm.add_widget(ConnectScreen(name='connect'))
            sm.add_widget(StatusScreen(name='status'))
            
            return sm
        except Exception as e:
            print(f"CRITICAL BUILD ERROR: {e}")
            raise e

    def on_start(self):
        # Start watchdog heartbeat
        Clock.schedule_interval(self.touch_heartbeat, 5.0)
        # Start polling for status updates
        Clock.schedule_interval(self.check_status, 3.0)

    def touch_heartbeat(self, dt):
        """
        Updates a timestamp file or systemd watchdog.
        If using systemd, we can notify systemd here (requires python-systemd or sd_notify).
        For now, we just print ALIVE to stdout which we can grep or monitor.
        """
        # print("HEARTBEAT: ALIVE") 
        pass 


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
        try:
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
        except Exception as e:
            print(f"Error in handle_status_update: {e}")

def restart_program():
    """Restarts the current program."""
    print("RESTARTING APPLICATION...")
    python = sys.executable
    os.execl(python, python, *sys.argv)

if __name__ == '__main__':
    CRASH_LOG_PATH = "/home/ijas/printjoy_logs/kivy_crash.log"
    os.makedirs(os.path.dirname(CRASH_LOG_PATH), exist_ok=True)
    
    try:
        PrintJoyApp().run()
    except Exception as e:
        import traceback
        import datetime
        
        timestamp = datetime.datetime.now().isoformat()
        with open(CRASH_LOG_PATH, "a") as f:
            f.write(f"\n[{timestamp}] CRITICAL CRASH:\n")
            traceback.print_exc(file=f)
            
        print("CRITICAL ERROR CAUGHT. RESTARTING IN 3 SECONDS...")
        try:
            # Show a crude error if possible, or just sleep
            time.sleep(3)
        except:
            pass
        restart_program()

