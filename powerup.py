# powerup.py
"""
This module implements a powerup system for the Tetris game.
Powerups include:
 - IceBlockPowerUp (value 8): Slows the game.
 - BombBlockPowerUp (value 9): Explodes blocks in a radius.
 - GravityBlockPowerUp (value 10): Shifts the board downward.
 - WildCardBlockPowerUp (value 11): Randomizes the board colors.
"""

import random

class PowerUp:
    def apply(self, game_instance):
        raise NotImplementedError("Subclasses must implement the apply method.")

class IceBlockPowerUp(PowerUp):
    def apply(self, game_instance):
        original_speed = game_instance.fall_speed
        game_instance.fall_speed += 0.2
        print(f"IceBlock Power-Up activated! Fall speed increased from {original_speed} to {game_instance.fall_speed}")

        # Activate the frost effect for 10 seconds
        game_instance.activate_ice_effect(duration=10)

class BombBlockPowerUp(PowerUp):
    def __init__(self, row, col, radius=2):
        self.row = row
        self.col = col
        self.radius = radius

    def apply(self, game_instance):
        board = game_instance.board
        WALL_HEIGHT = len(board)
        WALL_WIDTH = len(board[0]) if board else 0
        # Remove blocks in a square region with side-length (2*radius + 1)
        for r in range(self.row - self.radius, self.row + self.radius + 1):
            for c in range(self.col - self.radius, self.col + self.radius + 1):
                if 0 <= r < WALL_HEIGHT and 0 <= c < WALL_WIDTH:
                    board[r][c] = 0
        print(f"BombBlock Power-Up activated at ({self.row}, {self.col}). Blocks within radius {self.radius} removed.")

class GravityBlockPowerUp(PowerUp):
    def apply(self, game_instance):
        board = game_instance.board
        WALL_HEIGHT = len(board)
        WALL_WIDTH = len(board[0]) if board else 0
        # Shift every row down by one:
        for row in range(WALL_HEIGHT - 1, 0, -1):
            for col in range(WALL_WIDTH):
                board[row][col] = board[row - 1][col]
        # Clear the top row.
        board[0] = [0 for _ in range(WALL_WIDTH)]
        print("GravityBlock Power-Up activated! All blocks shifted down.")

class WildCardBlockPowerUp(PowerUp):
    def apply(self, game_instance):
        board = game_instance.board
        for row in range(len(board)):
            for col in range(len(board[row])):
                # For every non-empty block, assign a random value between 1 and 7.
                if board[row][col] > 0:
                    board[row][col] = random.randint(1, 7)
        print("WildCard Power-Up activated! All board blocks randomized.")

def apply_powerups(game_instance, cleared_row, row_index):
    """
    Check the cleared row for any powerup blocks and apply their effects.
    
    Parameters:
        game_instance: The current game instance (e.g. IsometricGrid).
        cleared_row: A list of block values in the cleared row.
        row_index: The index of the cleared row on the board.
    """
    # Check for IceBlock (value 8)
    if 8 in cleared_row:
        powerup = IceBlockPowerUp()
        powerup.apply(game_instance)
    
    # Check for BombBlock (value 9), GravityBlock (value 10), and WildCard (value 11)
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
