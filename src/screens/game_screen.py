# src/screens/game_screen.py
from kivy.uix.screenmanager import Screen
from kivy.uix.floatlayout import FloatLayout

from src.core.game import TetrisGame
from src.ui.widgets import ScoreDisplay, NextPieceDisplay
from src.utils.constants import WALL_WIDTH, WALL_HEIGHT

class GameScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        main_layout = FloatLayout()

        # Create initial empty board
        board = [[0 for _ in range(WALL_WIDTH)] for _ in range(WALL_HEIGHT)]

        # Create the UI and NextPiece widgets
        self.ui_instance = ScoreDisplay()
        self.next_piece_instance = NextPieceDisplay()

        # Create the Tetris game instance
        self.game_widget = TetrisGame(
            ui_reference=self.ui_instance,
            next_piece_reference=self.next_piece_instance
        )

        # Add everything to the layout
        main_layout.add_widget(self.game_widget)
        main_layout.add_widget(self.ui_instance)
        main_layout.add_widget(self.next_piece_instance)
        self.add_widget(main_layout)

    def on_pre_enter(self):
        """Called just before this screen becomes the active screen."""
        super().on_pre_enter()
        # Start the game loop
        self.game_widget.start()