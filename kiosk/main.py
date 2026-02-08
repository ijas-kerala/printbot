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

from kiosk.screens import SplitScreenKiosk
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
            # sm = MDScreenManager(transition=MDFadeSlideTransition())
            # sm.add_widget(AttractScreen(name='attract'))
            # sm.add_widget(ConnectScreen(name='connect'))
            # sm.add_widget(StatusScreen(name='status'))
            # sm.add_widget(SuccessScreen(name='success'))
            
            # New Split Screen Root
            self.root_widget = SplitScreenKiosk(name='split_root')
            return self.root_widget
            
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
        - idle -> IdleView (Right Panel)
        - uploading -> ProcessingView (Right Panel)
        - printing -> ProcessingView (Right Panel)
        - error -> ErrorView (Right Panel)
        - (Internal) success -> SuccessView (Right Panel)
        """
        try:
            # Get Right Panel ScreenManager
            # self.root is the SplitScreenKiosk instance
            if not hasattr(self.root, 'right_panel'):
                return

            sm = self.root.right_panel
            current_screen = sm.current
            new_state = data.get("state", "idle")
            driver_status = data.get("driver_status", "") # Hypothical field from backend
            
            # Determine Target Screen based on State & Driver Status
            target_screen = "idle"
            
            if new_state == "idle":
                target_screen = "idle"
            elif new_state == "uploading":
                target_screen = "processing"
            elif new_state == "printing":
                target_screen = "processing"
            
            # Check for specific error overrides (if backend provides them in top-level or status object)
            # Assuming data['status'] text might contain "Error" or similar if we don't have codes yet
            status_text = data.get("status", "")
            if "Error" in status_text or "Offline" in status_text or "Jam" in status_text:
                 target_screen = "error"

            # SPECIAL CASE: Transition from Printing/Processing -> Idle
            # implies success. Show Success screen first.
            if current_screen == 'processing' and target_screen == 'idle':
                self.show_success_and_reset()
                return

            if current_screen == 'success':
                 # Don't interrupt success message until timeout
                 return

            if current_screen != target_screen:
                sm.current = target_screen
                
            # Update specific screen data
            screen = sm.get_screen(target_screen)
            
            if target_screen == "processing":
                 if hasattr(screen, 'update_status'):
                     screen.update_status(status_text)
            
            if target_screen == "error":
                 if hasattr(screen, 'update_error'):
                     screen.update_error(status_text)

        except Exception as e:
            print(f"Error in handle_status_update: {e}")

    def show_success_and_reset(self):
        """Switch to Success screen and schedule return to Attract."""
        try:
            print("Job Complete. Showing Success Screen.")
            sm = self.root.right_panel
            sm.current = 'success'
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

