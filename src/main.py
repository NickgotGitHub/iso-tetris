"""
Main entry point for the Tetris game.
"""

from kivy.app import App
from kivy.uix.screenmanager import ScreenManager
from kivy.utils import platform
from kivy.core.audio import SoundLoader
from kivy.core.window import Window

from src.screens.home_screen import HomeScreen
from src.screens.game_screen import GameScreen
from src.screens.settings_screen import SettingsScreen
from src.utils.constants import WINDOW_CLEARCOLOR

# Request Android permissions if needed
if platform == 'android':
    from android.permissions import request_permissions, Permission

class TetrisApp(App):
    """Main application class."""
    
    def build(self):
        """Build and return the root widget."""
        # Set up window properties
        Window.clearcolor = WINDOW_CLEARCOLOR
        
        # Request Android permissions if needed
        if platform == 'android':
            request_permissions([
                Permission.READ_EXTERNAL_STORAGE,
                Permission.WRITE_EXTERNAL_STORAGE
            ])

        # Create screen manager
        sm = ScreenManager()
        
        # Load background music
        self.background_sound = SoundLoader.load('src/assets/audio/tetris_base.mp3')
        if self.background_sound:
            self.background_sound.loop = True
            self.background_sound.play()

        # Add screens
        sm.add_widget(HomeScreen(name='home'))
        sm.add_widget(GameScreen(name='game'))
        sm.add_widget(SettingsScreen(name='settings'))

        # Start on home screen
        sm.current = 'home'
        return sm

def main():
    """Application entry point."""
    TetrisApp().run()

if __name__ == '__main__':
    main() 