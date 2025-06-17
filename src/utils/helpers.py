"""
Utility functions for the Tetris game.
"""

from .constants import ISO_MATRIX

def to_isometric(column, row, z):
    """
    Convert cartesian coordinates to isometric coordinates.
    
    Args:
        column: X coordinate in cartesian space
        row: Y coordinate in cartesian space
        z: Z coordinate in cartesian space
        
    Returns:
        tuple: (iso_x, iso_y) coordinates in isometric space
    """
    iso_x = ISO_MATRIX[0][0] * column + ISO_MATRIX[0][1] * row
    iso_y = ISO_MATRIX[1][0] * column + ISO_MATRIX[1][1] * row + ISO_MATRIX[1][2] * z
    return iso_x, iso_y

def calculate_score(cleared_lines, level):
    """
    Calculate score based on number of lines cleared and current level.
    
    Args:
        cleared_lines: Number of lines cleared
        level: Current game level
        
    Returns:
        int: Score points earned
    """
    from .constants import SCORE_POINTS
    if cleared_lines == 0:
        return 0
    base_points = SCORE_POINTS[cleared_lines]
    return base_points * level

def determine_level_and_fall_speed(lines_cleared, initial_fall_speed):
    """
    Calculate the current level and fall speed based on lines cleared.
    
    Args:
        lines_cleared: Total number of lines cleared
        initial_fall_speed: Initial fall speed in seconds
        
    Returns:
        tuple: (level, fall_speed)
    """
    level = lines_cleared // 10 + 1
    level_adjustment = initial_fall_speed * (0.1 * (level - 1))
    fall_speed = initial_fall_speed - level_adjustment
    return level, fall_speed 