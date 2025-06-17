# src/screens/settings_screen.py
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.screenmanager import Screen
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.core.audio import SoundLoader


class SettingsScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        layout = FloatLayout()

        # Title
        title = Label(
            text="Settings",
            font_size='30sp',
            pos_hint={'center_x': 0.5, 'center_y': 0.85}
        )
        layout.add_widget(title)

        # Volume Control
        volume_button = Button(
            text="Volume: On",
            size_hint=(0.3, 0.05),
            pos_hint={'center_x': 0.5, 'center_y': 0.4}
        )
        volume_button.bind(on_release=self.toggle_volume)
        layout.add_widget(volume_button)
        self.volume_button = volume_button
        self.volume_on = True

        # Return to Home Button
        home_button = Button(
            text="Return to Home",
            size_hint=(0.3, 0.05),
            pos_hint={'center_x': 0.5, 'center_y': 0.2}
        )
        home_button.bind(on_release=self.goto_homescreen)
        layout.add_widget(home_button)

        self.add_widget(layout)
    
    def toggle_volume(self, instance):
        """Toggle game volume on/off."""
        app = self.manager.get_parent_window().children[0]
        if hasattr(app, 'background_sound'):
            if self.volume_on:
                app.background_sound.volume = 0
                self.volume_button.text = "Volume: Off"
            else:
                app.background_sound.volume = 1
                self.volume_button.text = "Volume: On"
            self.volume_on = not self.volume_on

    def goto_homescreen(self, instance):
        """Return to the home screen."""
        self.manager.current = 'home'