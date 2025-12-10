from kivy.uix.image import Image
from kivy.uix.boxlayout import BoxLayout
from kivy.clock import Clock
from kivy.properties import StringProperty

class MascotWidget(BoxLayout):
    state = StringProperty("idle")  # idle, wave, happy, sad, processing
    source = StringProperty("kiosk/assets/printo_idle.png")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = "vertical"
        self.img = Image(source=self.source, allow_stretch=True)
        self.add_widget(self.img)
        self.bind(state=self.update_mascot)
        
        # Idle Animation Loop
        Clock.schedule_interval(self.idle_animation, 8.0)

    def update_mascot(self, instance, value):
        # In a real implementation, switch to specific GIF or PNG sequence
        # For now, we simulate with state changes
        if value == "idle":
            self.img.source = "kiosk/assets/printo_idle.png"
        elif value == "wave":
            self.img.source = "kiosk/assets/printo_wave.png"
        elif value == "happy":
             self.img.source = "kiosk/assets/printo_happy.png"
        elif value == "sad":
             self.img.source = "kiosk/assets/printo_sad.png"

    def idle_animation(self, dt):
        if self.state == "idle":
            self.state = "wave"
            Clock.schedule_once(lambda d: setattr(self, 'state', 'idle'), 2.0)

    def dance(self):
        self.state = "happy"
        # Reset after 5 seconds
        Clock.schedule_once(lambda d: setattr(self, 'state', 'idle'), 5.0)
