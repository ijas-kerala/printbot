from kivymd.uix.screen import MDScreen
from kivymd.uix.button import MDFillRoundFlatButton, MDFlatButton
from kivymd.uix.label import MDLabel
from kivymd.uix.card import MDCard
from kivymd.uix.boxlayout import MDBoxLayout
from kivy.uix.image import Image
from kivy.clock import Clock
from kiosk.mascot import MascotWidget

class AttractScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = MDBoxLayout(orientation='vertical', padding=20, spacing=20)
        
        # Mascot
        self.mascot = MascotWidget(size_hint=(1, 0.6))
        self.layout.add_widget(self.mascot)
        
        # Welcome Text
        self.label = MDLabel(
            text="Hi! I'm Printo.\nTouch me to print!",
            halign="center",
            font_style="H4",
            theme_text_color="Primary",
            size_hint=(1, 0.2)
        )
        self.layout.add_widget(self.label)
        
        # Invisible button covering screen to trigger start
        self.start_btn = MDFlatButton(
            size_hint=(1, 1),
            pos_hint={'center_x': 0.5, 'center_y': 0.5},
            on_release=self.goto_connect
        )
        self.add_widget(self.layout)
        self.add_widget(self.start_btn)

    def goto_connect(self, instance):
        self.manager.current = 'connect'

class ConnectScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = MDBoxLayout(orientation='horizontal', padding=40, spacing=20)
        
        # Left: Playful Instructions
        left_panel = MDBoxLayout(orientation='vertical', spacing=10)
        mascot = MascotWidget(size_hint=(1, 0.4), state="idle")
        
        title = MDLabel(text="Scan to Upload", font_style="H3", halign="center")
        desc = MDLabel(text="Connect your phone to WiFi or Data.\nScan the code to send me your file!", halign="center")
        
        left_panel.add_widget(mascot)
        left_panel.add_widget(title)
        left_panel.add_widget(desc)
        
        # Right: QR Code Card
        right_panel = MDCard(
            radius=[20,],
            elevation=4,
            size_hint=(0.8, 0.8),
            pos_hint={"center_y": 0.5},
            md_bg_color=(1, 1, 1, 1) # White
        )
        
        # Placeholder QR
        # In real app, bind this to the correct Tunnel URL
        qr_img = Image(source="kiosk/assets/qr_placeholder.png")
        right_panel.add_widget(qr_img)
        
        layout.add_widget(left_panel)
        layout.add_widget(right_panel)
        
        # Admin hidden button (top right)
        admin_btn = MDFlatButton(
            text=" ",
            size_hint=(None, None),
            size=(50, 50),
            pos_hint={'top': 1, 'right': 1},
            on_release=self.open_admin_login
        )
        
        self.add_widget(layout)
        self.add_widget(admin_btn)

    def open_admin_login(self, instance):
        print("Admin login triggered")
        # TODO: Implement pattern lock overlay

class StatusScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = MDBoxLayout(orientation='vertical', padding=40, spacing=20)
        
        # Mascot
        self.mascot = MascotWidget(size_hint=(1, 0.5), state="happy")
        self.layout.add_widget(self.mascot)
        
        # Status Text
        self.status_label = MDLabel(
            text="Initializing Printer...",
            halign="center",
            font_style="H4",
            theme_text_color="Primary"
        )
        self.layout.add_widget(self.status_label)
        
        self.add_widget(self.layout)

    def update_status(self, text):
        self.status_label.text = text
