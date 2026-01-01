import os
import sys
import time
from kivy.config import Config

# Reliability: Hardened UI Config
# Fix Critical Clipboard Error: Force 'simple' (internal) clipboard to avoid xclip dependency
os.environ["KIVY_CLIPBOARD"] = "simple"

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

from kiosk.screens import AttractScreen, ConnectScreen, StatusScreen, SuccessScreen
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
            sm.add_widget(SuccessScreen(name='success'))
            
            return sm
        except Exception as e:
            print(f"CRITICAL BUILD ERROR: {e}")
            raise e

    def on_start(self):
        # Start watchdog heartbeat
        Clock.schedule_interval(self.touch_heartbeat, 5.0)
        # Start polling for status updates (Faster polling for responsiveness)
        Clock.schedule_interval(self.check_status, 1.5)

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
            api_url = os.environ.get("API_URL", "http://127.0.0.1:8000")
            response = requests.get(f"{api_url}/status", timeout=1)
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
        - (Internal) success -> SuccessScreen
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
            
            # SPECIAL CASE: Transition from Printing (status) -> Idle (attract)
            # This implies the job finished successfully. Show Success screen first.
            if current_screen == 'status' and target_screen == 'attract':
                self.show_success_and_reset()
                return

            # If we are currently showing success, don't interrupt it with 'idle'
            if current_screen == 'success' and target_screen == 'attract':
                return

            # FIX: If user is on Connect Screen (scanning) and backend is Idle,
            # DO NOT force them back to Attract Screen.
            if current_screen == 'connect' and target_screen == 'attract':
                # Just Ensure Connect Screen is in "Scan" mode (Show QR)
                screen = self.root.get_screen('connect')
                if hasattr(screen, 'set_state'):
                    screen.set_state('scan')
                return

            if current_screen != target_screen:
                self.root.current = target_screen
                
            # Update specific screen data if needed
            if new_state == "printing" or new_state == "uploading":
                screen = self.root.get_screen(target_screen)
                if hasattr(screen, 'update_status') and "status" in data:
                     screen.update_status(data["status"])
                
                # Logic to hide QR code if we are in "uploading" state (meaning file exists)
                if new_state == "uploading" and target_screen == "connect":
                    if hasattr(screen, 'set_state'):
                        screen.set_state('busy')

        except Exception as e:
            print(f"Error in handle_status_update: {e}")

    def show_success_and_reset(self):
        """Switch to Success screen and schedule return to Attract."""
        try:
            print("Job Complete. Showing Success Screen.")
            self.root.current = 'success'
            # Reset to attract screen after 5 seconds
            Clock.unschedule(self.reset_to_attract)
            Clock.schedule_once(self.reset_to_attract, 5.0)
        except Exception as e:
            print(f"Error in show_success: {e}")

    def reset_to_attract(self, dt):
        self.root.current = 'attract'

def restart_program():
    """Restarts the current program."""
    print("RESTARTING APPLICATION...")
    python = sys.executable
    os.execl(python, python, *sys.argv)

if __name__ == '__main__':

    # RPi Hardening: Ensure DISPLAY is set for Kivy
    if "DISPLAY" not in os.environ:
        print("WARNING: DISPLAY env var not set. Defaulting to :0 for Kiosk mode.")
        os.environ["DISPLAY"] = ":0"

    # NOTE: KivyMD 1.2.0+ Upgrade Note:
    # If upgrading KivyMD, ensure theme_cls usage is compatible.
    # Currently targeted for KivyMD 1.1.1 logic.

    # Dynamic Log Path (Fixes PermissionError on new devices)
    # Tries to log to project/logs/crash.log, falls back to /tmp/printbot_crash.log
    try:
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        log_dir = os.path.join(project_root, "logs")
        os.makedirs(log_dir, exist_ok=True)
        CRASH_LOG_PATH = os.path.join(log_dir, "crash.log")
        # Test write permission
        with open(CRASH_LOG_PATH, "a"): pass
    except OSError:
        print(f"WARNING: No write permission for {log_dir}. Fallback to /tmp")
        CRASH_LOG_PATH = "/tmp/printbot_crash.log"

    try:
        PrintJoyApp().run()
    except Exception as e:
        import traceback
        import datetime
        
        timestamp = datetime.datetime.now().isoformat()
        try:
            with open(CRASH_LOG_PATH, "a") as f:
                f.write(f"\n[{timestamp}] CRITICAL CRASH:\n")
                traceback.print_exc(file=f)
            print(f"CRITICAL ERROR CAUGHT. LOGGED TO {CRASH_LOG_PATH}")
        except Exception as log_err:
             print(f"CRITICAL ERROR CAUGHT (LOGGING FAILED): {e}")
             print(f"Logging Error: {log_err}")

        print("RESTARTING IN 3 SECONDS...")
        try:
            # Show a crude error if possible, or just sleep
            time.sleep(3)
        except:
            pass
        restart_program()

