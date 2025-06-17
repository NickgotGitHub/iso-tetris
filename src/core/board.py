"""
Game board implementation and management.
"""

from typing import List, Tuple, Optional
from ..utils.constants import WALL_WIDTH, WALL_HEIGHT
from .pieces import Piece
from .powerups import apply_powerups

class Board:
    """Manages the Tetris game board state and operations."""
    
    def __init__(self):
        """Initialize an empty board."""
        self.grid = [[0 for _ in range(WALL_WIDTH)] for _ in range(WALL_HEIGHT)]

    def is_valid_position(self, piece: Piece, position: Tuple[int, int]) -> bool:
        """
        Check if a piece can be placed at the given position.
        
        Args:
            piece: The piece to check
            position: (column, row) position to check
            
        Returns:
            bool: True if the position is valid, False otherwise
        """
        off_column, off_row = position
        for row_index, row in enumerate(piece.shape):
            for col_index, cell in enumerate(row):
                if cell:
                    board_row = row_index + off_row
                    board_col = col_index + off_column
                    
                    # Check bounds
                    if (board_col < 0 or board_col >= WALL_WIDTH or 
                        board_row >= WALL_HEIGHT):
                        return False
                    
                    # Check collision with other pieces
                    if board_row >= 0 and self.grid[board_row][board_col] != 0:
                        return False
        return True

    def place_piece(self, piece: Piece, position: Tuple[int, int]) -> None:
        """
        Place a piece on the board at the given position.
        
        Args:
            piece: The piece to place
            position: (column, row) position to place the piece
        """
        column, row = position
        for row_index, piece_row in enumerate(piece.shape):
            for col_index, cell in enumerate(piece_row):
                if cell:
                    self.grid[row + row_index][column + col_index] = cell

    def remove_piece(self, piece: Piece, position: Tuple[int, int]) -> None:
        """
        Remove a piece from the board at the given position.
        
        Args:
            piece: The piece to remove
            position: (column, row) position of the piece
        """
        column, row = position
        for row_index, piece_row in enumerate(piece.shape):
            for col_index, cell in enumerate(piece_row):
                if cell:
                    self.grid[row + row_index][column + col_index] = 0

    def clear_lines(self) -> int:
        """
        Clear completed lines and return the number of lines cleared.
        
        Returns:
            int: Number of lines cleared
        """
        lines_cleared = 0
        row = WALL_HEIGHT - 1
        while row >= 0:
            if all(cell != 0 for cell in self.grid[row]):
                # Apply powerups before clearing
                apply_powerups(self, self.grid[row], row)
                
                # Remove the line and shift everything down
                self.grid.pop(row)
                self.grid.insert(0, [0 for _ in range(WALL_WIDTH)])
                lines_cleared += 1
            else:
                row -= 1
        return lines_cleared

    def get_shadow_position(self, piece: Piece, start_position: Tuple[int, int]) -> Tuple[int, int]:
        """
        Calculate the position where the piece would land if dropped.
        
        Args:
            piece: The piece to check
            start_position: Starting position of the piece
            
        Returns:
            tuple: (column, row) final position
        """
        column, row = start_position
        while self.is_valid_position(piece, (column, row + 1)):
            row += 1
        return (column, row)

    def get_piece_width(self, piece: Piece) -> int:
        """
        Calculate the width of a piece.
        
        Args:
            piece: The piece to measure
            
        Returns:
            int: Width of the piece
        """
        leftmost = float('inf')
        rightmost = float('-inf')

        for row in piece.shape:
            for col, cell in enumerate(row):
                if cell:
                    leftmost = min(leftmost, col)
                    rightmost = max(rightmost, col)

        if leftmost == float('inf') or rightmost == float('-inf'):
            return 0

        return rightmost - leftmost + 1

    def is_game_over(self, piece: Piece, start_position: Tuple[int, int]) -> bool:
        """
        Check if the game is over (can't place new piece at starting position).
        
        Args:
            piece: The piece to check
            start_position: Starting position for new pieces
            
        Returns:
            bool: True if game is over, False otherwise
        """
        return not self.is_valid_position(piece, start_position) 