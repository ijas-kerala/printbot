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
        
        self.title = MDLabel(text="Scan to Upload", font_style="H3", halign="center")
        self.desc = MDLabel(text="Connect your phone to WiFi or Data.\nScan the code to send me your file!", halign="center")
        
        left_panel.add_widget(mascot)
        left_panel.add_widget(self.title)
        left_panel.add_widget(self.desc)
        
        # Status Label (Hidden by default until update)
        self.status_label = MDLabel(
            text="",
            halign="center",
            theme_text_color="Custom",
            text_color=(0, 0, 1, 1), # Blue
            font_style="Subtitle1"
        )
        left_panel.add_widget(self.status_label)
        
        # Right: QR Code Card
        self.qr_card = MDCard(
            radius=[20,],
            elevation=4,
            size_hint=(0.8, 0.8),
            pos_hint={"center_y": 0.5},
            md_bg_color=(1, 1, 1, 1) # White
        )
        
        # Placeholder QR
        # In real app, bind this to the correct Tunnel URL
        self.qr_img = Image(source="kiosk/assets/qr_placeholder.png")
        self.qr_card.add_widget(self.qr_img)

        # Processing Spinner (Hidden by default)
        from kivymd.uix.spinner import MDSpinner
        self.processing_spinner = MDSpinner(
            size_hint=(None, None),
            size=(50, 50),
            pos_hint={'center_x': 0.5, 'center_y': 0.5},
            active=False,
            opacity=0
        )
        # We add spinner to the layout but might need to position it better. 
        # Actually, let's swap QR card content or overlay.
        # Simplest: Add it to layout, but manage opacity.
        
        layout.add_widget(left_panel)
        # Wrap QR and Spinner in a Frame or just add both and toggle
        right_container = MDBoxLayout(orientation='vertical', size_hint=(0.8, 0.8), pos_hint={"center_y": 0.5})
        right_container.add_widget(self.qr_card)
        
        # Add spinner to right container (will center it if we play with layout)
        # Better: Add spinner to the card, removing QR img? No, slow.
        # Let's just put the spinner in the right_panel area later if needed.
        # For now, adding to the main layout for visibility control.
        
        layout.add_widget(right_container)
        
        # Add Spinner to right_container to swap visibility
        self.right_container = right_container
        
        
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

    def set_state(self, state_type):
        """
        state_type: 'scan' or 'busy'
        """
        if state_type == 'busy':
            # Hide QR, Show Spinner
            if self.qr_img in self.qr_card.children:
                self.qr_card.remove_widget(self.qr_img)
                self.qr_card.add_widget(self.processing_spinner)
                self.processing_spinner.active = True
                self.processing_spinner.opacity = 1
            self.title.text = "Processing..."
            self.desc.text = "Please follow the instructions\non your phone."
            
        else:
            # Show QR
            if self.processing_spinner in self.qr_card.children:
                self.qr_card.remove_widget(self.processing_spinner)
                self.qr_card.add_widget(self.qr_img)
                self.processing_spinner.active = False
            self.title.text = "Scan to Upload"
            self.desc.text = "Connect your phone to WiFi or Data.\nScan the code to send me your file!"


    def update_status(self, text):
        """Updates the status label on the connect screen."""
        if self.status_label:
            # Animation for smooth text update
            from kivy.animation import Animation
            anim = Animation(opacity=0, duration=0.2) + Animation(opacity=1, duration=0.2)
            anim.bind(on_mid_complete=lambda x,y: setattr(self.status_label, 'text', text))
            anim.start(self.status_label)

    def open_admin_login(self, instance):
        print("Admin login triggered")
        # TODO: Implement pattern lock overlay

class StatusScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = MDBoxLayout(orientation='vertical', padding=40, spacing=20)
        
        # Mascot
        self.mascot = MascotWidget(size_hint=(1, 0.4), state="happy")
        self.layout.add_widget(self.mascot)
        
        # Loading Spinner
        from kivymd.uix.spinner import MDSpinner
        self.spinner = MDSpinner(
            size_hint=(None, None),
            size=(50, 50),
            pos_hint={'center_x': 0.5},
            active=True
        )
        self.layout.add_widget(self.spinner)
        
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

class SuccessScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = MDBoxLayout(orientation='vertical', padding=40, spacing=20)
        
        self.mascot = MascotWidget(size_hint=(1, 0.5), state="happy")
        self.layout.add_widget(self.mascot)
        
        from kivymd.uix.label import MDLabel
        self.label = MDLabel(
            text="Printing Complete!\nEnjoy your document.",
            halign="center",
            font_style="H4",
            theme_text_color="Primary"
        )
        self.layout.add_widget(self.label)
        
        self.add_widget(self.layout)
