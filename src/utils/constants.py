"""
Game constants and configuration values.
"""

# Window/Display
WINDOW_CLEARCOLOR = (198 / 255.0, 40 / 255.0, 78 / 255.0, 1)

# Board dimensions
WALL_WIDTH = 10
WALL_HEIGHT = 20

# Block sizes
BLOCK_SIZE = 60
BLOCK_WIDTH = BLOCK_SIZE
BLOCK_HEIGHT = BLOCK_SIZE
ISO_BLOCK_HEIGHT = BLOCK_HEIGHT // 2

# Isometric transformation matrix
ISO_MATRIX = [[0.5, -0.5], [0.25, 0.25, 0]]

# Asset paths
SPRITE_SHEET_PATH = 'assets/sprites/sprite_sheet.png'
BOMB_TEXTURE_PATH = "assets/sprites/powerups/bomb_block.png"
GRAVITY_TEXTURE_PATH = "assets/sprites/powerups/gravity_block.png"
WILDCARD_TEXTURE_PATH = "assets/sprites/powerups/wild_card.png"
FROST_TEXTURE_PATH = "assets/sprites/frost_effect.png"
FONT_PATH = 'assets/fonts/PressStart2P-Regular.ttf'

# Game speeds and timings
BASE_FALL_SPEED = 0.2
GAME_SPEED = 0.06
FPS = 60

# Powerup probabilities
POWERUP_CHANCES = {
    'ICE': 0.10,      # 10%
    'BOMB': 0.00667,  # ~0.67%
    'GRAVITY': 0.00333,  # ~0.33%
    'WILDCARD': 0.002  # 0.2%
}

# Scoring system
SCORE_POINTS = {
    1: 40,    # Single line
    2: 100,   # Double
    3: 300,   # Triple
    4: 1200   # Tetris
}

# Touch controls
MIN_SWIPE_DISTANCE = 50

# Effect parameters
FROST_BASE_ALPHA = 0.5
FROST_GLOW_AMPLITUDE = 0.4
COLOR_TRANSITION_SPEED = 5

# Wildcard colors (RGB values)
WILDCARD_COLORS = [
    [250/255.0, 78/255.0, 94/255.0],    # Red
    [109/255.0, 109/255.0, 109/255.0],  # Gray
    [144/255.0, 234/255.0, 223/255.0],  # Cyan
    [230/255.0, 224/255.0, 103/255.0],  # Yellow
    [245/255.0, 190/255.0, 133/255.0],  # Orange
    [192/255.0, 221/255.0, 112/255.0],  # Green
    [218/255.0, 148/255.0, 218/255.0]   # Purple
] 