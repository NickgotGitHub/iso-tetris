"""
Main game logic for Tetris.
"""

from typing import Tuple, Optional
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.graphics import Color, Rectangle, Fbo
from kivy.uix.widget import Widget

from .board import Board
from .pieces import TetrominoFactory, Piece
from ..ui.effects import FrostEffect, ColorTransitionEffect
from ..utils.helpers import to_isometric, calculate_score, determine_level_and_fall_speed
from ..utils.constants import (
    WALL_WIDTH, WALL_HEIGHT, BLOCK_SIZE, BLOCK_WIDTH, BLOCK_HEIGHT,
    ISO_BLOCK_HEIGHT, BASE_FALL_SPEED, FPS
)
from ..utils.database import db

class TetrisGame(Widget):
    """Main game class that coordinates all game components."""

    def __init__(self, ui_reference=None, next_piece_reference=None, **kwargs):
        """Initialize the game state."""
        super().__init__(**kwargs)
        self.board = Board()
        self.ui_ref = ui_reference
        self.next_piece_ref = next_piece_reference

        # Game state
        self.score = 0
        self.level = 1
        self.highscore = db.get_data('highscore', default=0)
        self.game_over = False
        self.fall_speed = BASE_FALL_SPEED
        self.time_since_last_fall = 0

        # Piece management
        self.upcoming_pieces = TetrominoFactory.create_piece_queue()
        self.current_piece = self.upcoming_pieces.pop(0)
        self.next_piece = self.upcoming_pieces[0]
        self.current_column = WALL_WIDTH // 2 - len(self.current_piece.shape[0]) // 2
        self.current_row = 0

        # Visual effects
        self.frost_effect = None
        self.wildcard_effect = ColorTransitionEffect()
        self.wildcard_effect.start()

        # Input handling
        self._keyboard = Window.request_keyboard(self._keyboard_closed, self)
        self._keyboard.bind(on_key_down=self._on_keyboard_down)

        # Bind size and position updates
        self.bind(pos=self._update_canvas, size=self._update_canvas)

    def _update_canvas(self, *args):
        """Update the game canvas when the widget size or position changes."""
        self.canvas.clear()
        with self.canvas:
            # Draw the game state
            self.draw_board()
            self.draw_current_piece()

    def draw_board(self):
        """Draw the game board."""
        with self.canvas:
            Color(1, 1, 1, 1)
            center_x = self.width / 2 - (WALL_WIDTH / 2) * (BLOCK_SIZE / 2)
            center_y = self.height / 2 + (WALL_HEIGHT / 2) * (ISO_BLOCK_HEIGHT / 2)
            
            # Draw placed blocks
            for row in range(WALL_HEIGHT):
                for col in range(WALL_WIDTH):
                    block = self.board.grid[row][col]
                    if block:
                        iso_x, iso_y = to_isometric(col * BLOCK_WIDTH, 0, row * ISO_BLOCK_HEIGHT)
                        adjusted_iso_y = iso_y - row * ISO_BLOCK_HEIGHT
                        Rectangle(
                            pos=(center_x + iso_x, center_y + adjusted_iso_y),
                            size=(BLOCK_WIDTH, BLOCK_HEIGHT)
                        )

    def draw_current_piece(self):
        """Draw the currently falling piece."""
        if not self.current_piece:
            return

        with self.canvas:
            Color(1, 1, 1, 1)
            center_x = self.width / 2 - (WALL_WIDTH / 2) * (BLOCK_SIZE / 2)
            center_y = self.height / 2 + (WALL_HEIGHT / 2) * (ISO_BLOCK_HEIGHT / 2)
            
            # Draw current piece with interpolation
            fraction = self.time_since_last_fall / self.fall_speed
            for row_idx, row in enumerate(self.current_piece.shape):
                for col_idx, cell in enumerate(row):
                    if cell:
                        float_row = self.current_row + fraction + row_idx
                        float_col = self.current_column + col_idx
                        iso_x, iso_y = to_isometric(float_col * BLOCK_WIDTH, 0, float_row * ISO_BLOCK_HEIGHT)
                        adjusted_iso_y = iso_y - float_row * ISO_BLOCK_HEIGHT
                        Rectangle(
                            pos=(center_x + iso_x, center_y + adjusted_iso_y),
                            size=(BLOCK_WIDTH, BLOCK_HEIGHT)
                        )

    def start(self):
        """Start the game loop."""
        Clock.schedule_interval(self.update, 1.0 / FPS)

    def update(self, dt: float):
        """Main game update loop."""
        if self.game_over:
            return

        self.time_since_last_fall += dt
        self.wildcard_effect.update(dt)
        if self.frost_effect:
            self.frost_effect.update(dt)

        # Handle piece falling
        if self.time_since_last_fall >= self.fall_speed:
            self.time_since_last_fall = 0
            self.move_piece_down()

        # Update UI
        self._update_ui()

    def move_piece_down(self):
        """Move the current piece down one row."""
        self.current_row += 1
        if not self.board.is_valid_position(self.current_piece, (self.current_column, self.current_row)):
            self.current_row -= 1
            self.lock_piece()
            self.spawn_new_piece()

    def move_piece(self, direction: str):
        """Move the current piece horizontally."""
        delta = 1 if direction == 'right' else -1
        new_column = self.current_column + delta
        
        if self.board.is_valid_position(self.current_piece, (new_column, self.current_row)):
            self.current_column = new_column

    def rotate_piece(self):
        """Attempt to rotate the current piece."""
        rotated = self.current_piece.rotate()
        if self.board.is_valid_position(rotated, (self.current_column, self.current_row)):
            self.current_piece = rotated

    def hard_drop(self):
        """Drop the piece to the bottom instantly."""
        while self.board.is_valid_position(self.current_piece, (self.current_column, self.current_row + 1)):
            self.current_row += 1
        self.lock_piece()
        self.spawn_new_piece()

    def lock_piece(self):
        """Lock the current piece in place and check for cleared lines."""
        self.board.place_piece(self.current_piece, (self.current_column, self.current_row))
        lines_cleared = self.board.clear_lines()
        
        # Update game state
        self.level, self.fall_speed = determine_level_and_fall_speed(lines_cleared, BASE_FALL_SPEED)
        self.score += calculate_score(lines_cleared, self.level)
        
        # Update high score if needed
        if self.score > self.highscore:
            self.highscore = self.score
            db.save_data('highscore', self.highscore)

    def spawn_new_piece(self):
        """Spawn a new piece and update the piece queue."""
        self.current_piece = self.next_piece
        self.upcoming_pieces.pop(0)
        self.upcoming_pieces.append(TetrominoFactory.create_random_piece())
        self.next_piece = self.upcoming_pieces[0]
        
        # Reset position
        self.current_column = WALL_WIDTH // 2 - len(self.current_piece.shape[0]) // 2
        self.current_row = 0
        
        # Check for game over
        if not self.board.is_valid_position(self.current_piece, (self.current_column, self.current_row)):
            self.game_over = True
            Clock.unschedule(self.update)
        
        # Update next piece display
        if self.ui_ref and self.next_piece_ref:
            next_piece_pos = self.ui_ref.update_rect_positions()
            self.next_piece_ref.draw_piece(self.next_piece.shape, next_piece_pos)

    def activate_ice_effect(self, duration: float = 10.0):
        """Activate the frost visual effect."""
        if not self.frost_effect:
            self.frost_effect = FrostEffect(self.canvas)
        self.frost_effect.start(duration)

    def _update_ui(self):
        """Update UI elements with current game state."""
        if self.ui_ref:
            self.ui_ref.update_labels(self.score, self.highscore, self.level)

    def _keyboard_closed(self):
        """Handle keyboard cleanup."""
        self._keyboard.unbind(on_key_down=self._on_keyboard_down)
        self._keyboard = None

    def _on_keyboard_down(self, keyboard, keycode, text, modifiers):
        """Handle keyboard input."""
        key = keycode[1]
        
        if key in ('up', 'w'):
            self.rotate_piece()
        elif key in ('down', 's'):
            self.hard_drop()
        elif key in ('left', 'a'):
            self.move_piece('left')
        elif key in ('right', 'd'):
            self.move_piece('right')
        
        return True  # Mark the key as handled 