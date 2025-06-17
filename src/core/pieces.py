"""
Tetromino pieces and their behavior.
"""

import random
from typing import List, Tuple
from ..utils.constants import POWERUP_CHANCES

class Piece:
    """Base class for all tetromino pieces."""
    def __init__(self, shape: List[List[int]], color_index: int):
        self.shape = shape
        self.color_index = color_index

    def rotate(self) -> 'Piece':
        """Rotate the piece clockwise."""
        rotated_shape = [list(row) for row in zip(*self.shape[::-1])]
        return Piece(rotated_shape, self.color_index)

class TetrominoFactory:
    """Factory class for creating tetromino pieces."""
    
    # Standard tetromino shapes
    SHAPES = {
        'T': ([[1, 1, 1], [0, 1, 0]], 1),  # T shape
        'Z': ([[0, 2, 2], [2, 2, 0]], 2),  # Z shape
        'S': ([[3, 3, 0], [0, 3, 3]], 3),  # S shape
        'J': ([[4, 0, 0], [4, 4, 4]], 4),  # J shape
        'L': ([[0, 0, 5], [5, 5, 5]], 5),  # L shape
        'O': ([[6, 6], [6, 6]], 6),        # O shape
        'I': ([[7, 7, 7, 7]], 7),          # I shape
    }

    # Powerup pieces
    POWERUPS = {
        'ICE': ([[8]], 8),          # Ice block
        'BOMB': ([[9]], 9),         # Bomb block
        'GRAVITY': ([[10]], 10),    # Gravity block
        'WILDCARD': ([[11]], 11),   # Wild card block
    }

    @classmethod
    def create_random_piece(cls) -> Piece:
        """
        Create a random piece based on weighted probabilities.
        
        Returns:
            Piece: A new random piece (either standard or powerup)
        """
        r = random.random()
        current_prob = 0

        # Check for powerups first
        for powerup_name, chance in POWERUP_CHANCES.items():
            current_prob += chance
            if r < current_prob:
                shape, color = cls.POWERUPS[powerup_name]
                return Piece(shape, color)

        # If no powerup was selected, choose a random standard piece
        shape_name = random.choice(list(cls.SHAPES.keys()))
        shape, color = cls.SHAPES[shape_name]
        return Piece(shape, color)

    @classmethod
    def create_piece_queue(cls, size: int = 3) -> List[Piece]:
        """
        Create a queue of upcoming pieces.
        
        Args:
            size: Number of pieces to generate
            
        Returns:
            List[Piece]: List of generated pieces
        """
        return [cls.create_random_piece() for _ in range(size)] 