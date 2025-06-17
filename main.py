# main.py

from kivy.app import App
from kivy.uix.screenmanager import ScreenManager
from kivy.utils import platform
from kivy.core.audio import SoundLoader

# If running on Android, handle storage permissions
if platform == 'android':
    from android.permissions import request_permissions, Permission

# Import our two screens from the `src.screens` folder
from src.screens.home_screen import HomeScreen
from src.screens.game_screen import GameScreen
from src.screens.settings_screen import SettingsScreen



class TetrisApp(App):
    def build(self):
        # Request file permissions on Android if needed
        if platform == 'android':
            request_permissions([Permission.READ_EXTERNAL_STORAGE, Permission.WRITE_EXTERNAL_STORAGE])

        # Create the ScreenManager and add our screens
        sm = ScreenManager()

        # Load and loop the background music
        self.background_sound = SoundLoader.load('Assets/Audios/tetris_base.mp3')
        if self.background_sound:
            self.background_sound.loop = True
            self.background_sound.play()

        sm.add_widget(HomeScreen(name='home'))
        sm.add_widget(GameScreen(name='game'))
        sm.add_widget(SettingsScreen(name='settings'))

        # Start on the home screen
        sm.current = 'home'
        return sm


if __name__ == '__main__':
    TetrisApp().run()
