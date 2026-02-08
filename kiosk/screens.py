from kivymd.uix.screen import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.card import MDCard
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDFlatButton, MDFillRoundFlatButton
from kivymd.uix.screenmanager import MDScreenManager
from kivymd.uix.transition import MDFadeSlideTransition
from kivy.uix.image import Image
from kivy.properties import StringProperty
from kiosk.mascot import MascotWidget

# ==========================================
# SUB-VIEWS (RIGHT PANEL)
# ==========================================

class IdleView(MDScreen):
    """Shown when no job is active."""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = MDBoxLayout(orientation='vertical', padding=40, spacing=20)
        
        # Mascot (Wave/Idle)
        self.mascot = MascotWidget(size_hint=(1, 0.5), state="wave")
        self.layout.add_widget(self.mascot)
        
        # Welcome Text
        self.label = MDLabel(
            text="Welcome to PrintJoy!\nScan the QR code to start.",
            halign="center",
            font_style="H4",
            theme_text_color="Primary"
        )
        self.layout.add_widget(self.label)
        
        self.add_widget(self.layout)

class ProcessingView(MDScreen):
    """Shown during upload/payment/printing."""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = MDBoxLayout(orientation='vertical', padding=40, spacing=20)
        
        # Mascot (Happy/Working)
        self.mascot = MascotWidget(size_hint=(1, 0.4), state="happy")
        self.layout.add_widget(self.mascot)
        
        # Spinner
        from kivymd.uix.spinner import MDSpinner
        self.spinner = MDSpinner(
            size_hint=(None, None),
            size=(60, 60),
            pos_hint={'center_x': 0.5},
            active=True
        )
        self.layout.add_widget(self.spinner)
        
        # Status Text
        self.status_label = MDLabel(
            text="Processing...",
            halign="center",
            font_style="H5",
            theme_text_color="Custom",
            text_color=(0.2, 0.6, 1, 1) # Brand Blueish
        )
        self.layout.add_widget(self.status_label)
        
        self.add_widget(self.layout)

    def update_status(self, text):
        self.status_label.text = text
        # If text implies printing, maybe change mascot to 'working' if we had one
        
class ErrorView(MDScreen):
    """Shown when hardware error occurs."""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = MDBoxLayout(orientation='vertical', padding=40, spacing=20)
        
        # Mascot (Sad)
        self.mascot = MascotWidget(size_hint=(1, 0.4), state="sad")
        self.layout.add_widget(self.mascot)
        
        # Error Icon (Text for now)
        self.icon_label = MDLabel(
            text="⚠️",
            halign="center",
            font_style="H2"
        )
        self.layout.add_widget(self.icon_label)
        
        # Error Text
        self.error_label = MDLabel(
            text="Printer Error",
            halign="center",
            font_style="H5",
            theme_text_color="Error"
        )
        self.layout.add_widget(self.error_label)
        
        self.add_widget(self.layout)
        
    def update_error(self, text):
        self.error_label.text = text

class SuccessView(MDScreen):
    """Shown when job is complete."""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = MDBoxLayout(orientation='vertical', padding=40, spacing=20)
        
        # Mascot (Party)
        self.mascot = MascotWidget(size_hint=(1, 0.5), state="happy")
        self.layout.add_widget(self.mascot)
        
        self.label = MDLabel(
            text="Done! Please collect your paper below.",
            halign="center",
            font_style="H4",
            theme_text_color="Custom",
            text_color=(0, 0.7, 0, 1) # Green
        )
        self.layout.add_widget(self.label)
        
        self.add_widget(self.layout)

# ==========================================
# MAIN SPLIT LAYOUT
# ==========================================

class SplitScreenKiosk(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        # Root Container (Horizontal Split)
        # Left: 40%, Right: 60%
        self.root_box = MDBoxLayout(orientation='horizontal', spacing=0)
        
        # -----------------------
        # LEFT PANEL (Static QR)
        # -----------------------
        self.left_panel = MDCard(
            size_hint_x=0.4,
            elevation=10,
            radius=[0, 20, 20, 0], # Rounded on right side
            md_bg_color=(1, 1, 1, 1),
            padding=30
        )
        left_layout = MDBoxLayout(orientation='vertical', spacing=20, pos_hint={'center_y': 0.5})
        
        # Header
        scan_label = MDLabel(
            text="Scan to Print",
            halign="center",
            font_style="H4",
            theme_text_color="Custom",
            text_color=(0.2, 0.2, 0.2, 1),
            size_hint_y=None,
            height=60
        )
        
        # QR Code Image
        # Using a container to keep it square
        qr_container = MDBoxLayout(size_hint=(1, None), height=300) 
        self.qr_img = Image(
            source="kiosk/assets/qr_placeholder.png",
            fit_mode="contain"
        )
        qr_container.add_widget(self.qr_img)
        
        # Instruction
        instr_label = MDLabel(
            text="No App Needed.\nJust scan to upload file.",
            halign="center",
            font_style="Subtitle1",
            theme_text_color="Hint"
        )
        
        left_layout.add_widget(scan_label)
        left_layout.add_widget(qr_container)
        left_layout.add_widget(instr_label)
        self.left_panel.add_widget(left_layout)
        
        # -----------------------
        # RIGHT PANEL (Dynamic)
        # -----------------------
        self.right_panel = MDScreenManager(transition=MDFadeSlideTransition())
        self.right_panel.add_widget(IdleView(name='idle'))
        self.right_panel.add_widget(ProcessingView(name='processing'))
        self.right_panel.add_widget(ErrorView(name='error'))
        self.right_panel.add_widget(SuccessView(name='success'))
        
        # -----------------------
        # ASSEMBLY
        # -----------------------
        self.root_box.add_widget(self.left_panel)
        self.root_box.add_widget(self.right_panel)
        
        self.add_widget(self.root_box)
        
        # Admin Hidden Button (Top Right Overlay)
        admin_btn = MDFlatButton(
             text=" ",
             size_hint=(None, None),
             size=(60, 60),
             pos_hint={'top': 1, 'right': 1},
             on_release=self.open_admin
        )
        self.add_widget(admin_btn)

    def open_admin(self, instance):
        print("Admin Triggered")
        # Feature: 5-tap pattern or long press
