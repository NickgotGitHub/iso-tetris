"""
Powerup system implementation.
"""

from typing import List, TYPE_CHECKING
import random

if TYPE_CHECKING:
    from .game import TetrisGame

class PowerUp:
    """Base class for all powerups."""
    def apply(self, game_instance: 'TetrisGame') -> None:
        """Apply the powerup effect."""
        raise NotImplementedError("Subclasses must implement apply method.")

class IceBlockPowerUp(PowerUp):
    """Slows down the game and adds a frost effect."""
    def apply(self, game_instance: 'TetrisGame') -> None:
        original_speed = game_instance.fall_speed
        game_instance.fall_speed += 0.2
        print(f"IceBlock Power-Up activated! Fall speed increased from {original_speed} to {game_instance.fall_speed}")
        game_instance.activate_ice_effect(duration=10)

class BombBlockPowerUp(PowerUp):
    """Explodes blocks in a radius around the placement point."""
    def __init__(self, row: int, col: int, radius: int = 2):
        self.row = row
        self.col = col
        self.radius = radius

    def apply(self, game_instance: 'TetrisGame') -> None:
        board = game_instance.board
        height = len(board)
        width = len(board[0]) if board else 0

        for r in range(self.row - self.radius, self.row + self.radius + 1):
            for c in range(self.col - self.radius, self.col + self.radius + 1):
                if 0 <= r < height and 0 <= c < width:
                    board[r][c] = 0
        print(f"BombBlock Power-Up activated at ({self.row}, {self.col}). Blocks within radius {self.radius} removed.")

class GravityBlockPowerUp(PowerUp):
    """Shifts the entire board down by one row."""
    def apply(self, game_instance: 'TetrisGame') -> None:
        board = game_instance.board
        height = len(board)
        width = len(board[0]) if board else 0

        for row in range(height - 1, 0, -1):
            for col in range(width):
                board[row][col] = board[row - 1][col]
        board[0] = [0 for _ in range(width)]
        print("GravityBlock Power-Up activated! All blocks shifted down.")

class WildCardBlockPowerUp(PowerUp):
    """Randomizes the colors of all blocks on the board."""
    def apply(self, game_instance: 'TetrisGame') -> None:
        board = game_instance.board
        for row in range(len(board)):
            for col in range(len(board[row])):
                if board[row][col] > 0:
                    board[row][col] = random.randint(1, 7)
        print("WildCard Power-Up activated! All board blocks randomized.")

def apply_powerups(game_instance: 'TetrisGame', cleared_row: List[int], row_index: int) -> None:
    """
    Check the cleared row for any powerup blocks and apply their effects.
    
    Args:
        game_instance: The current game instance
        cleared_row: List of block values in the cleared row
        row_index: Index of the cleared row on the board
    """
    # Check for IceBlock (value 8)
    if 8 in cleared_row:
        powerup = IceBlockPowerUp()
        powerup.apply(game_instance)
    
    # Check for other powerups
    for col_index, cell in enumerate(cleared_row):
        if cell == 9:
            powerup = BombBlockPowerUp(row_index, col_index)
            powerup.apply(game_instance)
        elif cell == 10:
            powerup = GravityBlockPowerUp()
            powerup.apply(game_instance)
        elif cell == 11:
            powerup = WildCardBlockPowerUp()
            powerup.apply(game_instance) 