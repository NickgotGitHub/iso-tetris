# main_game.py

import random
from kivy.uix.widget import Widget
from kivy.graphics import Rectangle, Color
from kivy.core.window import Window
from kivy.core.image import Image as CoreImage
from kivy.clock import Clock
from kivy.utils import platform
from kivy.graphics import Fbo, Rectangle

from UI import CustomWidget
from Next_piece import DrawNextPiece
from kivy.uix.widget import Widget
from kivy.graphics import Color, Line, Rectangle, ClearColor, ClearBuffers
import math


next_piece_instance = DrawNextPiece()

# Import your game save logic
from Game_save_state import handle_data
Window.clearcolor = (198 / 255.0, 40 / 255.0, 78 / 255.0, 1)

# You might also import `os` if needed, etc.

# --- Global constants from your code ---
WALL_WIDTH, WALL_HEIGHT = 10, 20
BLOCK_SIZE = 60
BLOCK_WIDTH = BLOCK_SIZE
BLOCK_HEIGHT = BLOCK_SIZE
ISO_BLOCK_HEIGHT = BLOCK_HEIGHT // 2
ISO_MATRIX = [[0.5, -0.5], [0.25, 0.25, 0]]
SPRITE_SHEET_PATH = 'Assets/Sprites/sprite_sheet.png'

# --- Utility function for isometric transform ---
def to_isometric(column, row, z):
    iso_x = ISO_MATRIX[0][0] * column + ISO_MATRIX[0][1] * row
    iso_y = ISO_MATRIX[1][0] * column + ISO_MATRIX[1][1] * row + ISO_MATRIX[1][2] * z
    return iso_x, iso_y

# --- The main Tetris widget ---
class IsometricGrid(Widget):
    def __init__(self, board, ui_reference=None, next_piece_reference=None, **kwargs):
        super().__init__(**kwargs)

        
        self.fbo = Fbo(size=self.size)
        with self.canvas:
            self.fbo_rect = Rectangle(texture=self.fbo.texture, pos=self.pos, size=self.size)
        self.bind(pos=self.update_fbo_rect, size=self.update_fbo_rect)
        Clock.schedule_interval(self.update_fbo, 1/60.0)
        Clock.schedule_interval(self.update_wildcard_color, 1/60.0)  # 60 FPS update


        self.ui_ref = ui_reference
        self.next_piece_ref = next_piece_reference


        self.board = board

        # Initialize attributes for the wild card color animation.
        self.wildcard_colors = [
            [250/255.0, 78/255.0, 94/255.0],    # rgba(250,78,94,255)
            [109/255.0, 109/255.0, 109/255.0],    # rgba(109,109,109,255)
            [144/255.0, 234/255.0, 223/255.0],    # rgba(144,234,223,255)
            [230/255.0, 224/255.0, 103/255.0],    # rgba(230,224,103,255)
            [245/255.0, 190/255.0, 133/255.0],    # rgba(245,190,133,255)
            [192/255.0, 221/255.0, 112/255.0],    # rgba(192,221,112,255)
            [218/255.0, 148/255.0, 218/255.0]     # rgba(218,148,218,255)
        ]

        
        # Set the initial wild card colors:
        self.wildcard_current_color = list(self.wildcard_colors[0])  # Start with the first color
        self.wildcard_color_index = 1  # Next target color is at index 1
        self.wildcard_target_color = self.wildcard_colors[self.wildcard_color_index]

        self.frost_active = False
        self.frost_rect = None
        self.frost_start_time = 0
        self.frost_duration = 0
        self.frost_base_alpha = 0.5   # average opacity
        self.frost_glow_amplitude = 0.4  # how much it fluctuates above/below base


        # Schedule the color update at 60 FPS.
        Clock.schedule_interval(self.update_wildcard_color, 1/60.0)

        self.sprite_sheet = CoreImage(SPRITE_SHEET_PATH).texture
        self.block_images = self.load_block_images()

        self.bind(size=self.draw_grid)
        self.bind(pos=self.draw_grid)

        # Initial position for the falling piece
        self.current_column, self.current_row = 3, 0

        # Game state flags
        self.game_over = False

        # Preload shapes for the upcoming blocks using the weighted selection.
        self.upcoming_blocks = [self.choose_piece() for _ in range(3)]
        self.current_piece = self.upcoming_blocks.pop(0)
        self.next_piece = self.upcoming_blocks[0]

        # Timing and speed
        self.time_since_last_fall = 0
        self.fall_speed = 0.2

        # Score and level
        self.score = 0
        self.level = 1

        # High score
        self.highscore = handle_data('highscore', 'get', default=0)


        # Keyboard
        self._keyboard = Window.request_keyboard(self._keyboard_closed, self)
        self._keyboard.bind(on_key_down=self._on_keyboard_down)

    # --- Tetris shapes ---
    shapes = [
        [[1, 1, 1], [0, 1, 0]],
        [[0, 2, 2], [2, 2, 0]],
        [[3, 3, 0], [0, 3, 3]],
        [[4, 0, 0], [4, 4, 4]],
        [[0, 0, 5], [5, 5, 5]],
        [[6, 6], [6, 6]],
        [[7, 7, 7, 7]],
        [[8]],    # Ice block powerup
        [[9]],    # Bomb block powerup
        [[10]],   # Gravity block powerup
        [[11]]    # Wild card block powerup
    ]

    def update_fbo_rect(self, *args):
        # Update both the Fbo size and the persistent rectangle's position/size.
        self.fbo.size = self.size
        self.fbo_rect.pos = self.pos
        self.fbo_rect.size = self.size


    def update_fbo(self, dt):
        # Bind the Fbo to draw into it.
        self.fbo.bind()

        # Instead of fully clearing the Fbo, use ClearColor/ClearBuffers only once at startup.
        # Here we draw a semi-transparent overlay to fade the previous frame.
        with self.fbo:
            # Draw a semi-transparent black rectangle over the entire Fbo.
            # This overlay fades out previous content slowly.
            # (You may adjust the alpha value for more or less trail.)
            Color(0, 0, 0, 0.05)
            Rectangle(pos=(0, 0), size=self.fbo.size)

        # Draw the current game state (board and falling piece).
        self.draw_game_state()

        self.fbo.release()

        # Update the persistent rectangle's texture reference.
        self.fbo_rect.texture = self.fbo.texture


    
    def start_game_loop(self):
        """Call this to actually begin the Tetris updates."""
        Clock.schedule_interval(self.running, 1.0 / 60.0)

    def choose_piece(self):
        """
        Choose a new tetromino piece based on weighted probabilities.
        
        Powerup chances:
            Ice block (value 8): 1/10 (10%)
            Bomb block (value 9): 1/15 (~6.67%)
            Gravity block (value 10): 1/30 (~3.33%)
            Wild card block (value 11): 1/50 (2%)
        Normal pieces (first 7 shapes): remaining probability (~78%)
        """
        r = random.random()
        if r < 0.10:
            return [[8]]  # Ice block powerup
        elif r < 0.10 + 0.00667:
            return [[9]]  # Bomb block powerup
        elif r < 0.10 + 0.00667 + 0.00333:
            return [[10]]  # Gravity block powerup
        elif r < 0.10 + 0.00667 + 0.00333 + 0.002:
            return [[11]]  # Wild card powerup
        else:
            # Choose one of the 7 normal tetromino shapes (indices 0 to 6).
            return random.choice(self.shapes[:7])

    def activate_ice_effect(self, duration=10):
        """
        Show a frost overlay for the given duration (in seconds).
        During that time, the opacity will fluctuate like a glow.
        """
        from kivy.clock import Clock
        import time

        # If it's already active, we can refresh it or ignore.
        self.frost_active = True
        self.frost_duration = duration
        self.frost_start_time = time.time()

        # Create the Rectangle for the frost overlay if it doesn't exist.
        if not self.frost_rect:
            with self.canvas.after:  # draw on top of everything
                Color(1, 1, 1, 1)  # alpha will be set dynamically
                self.frost_rect = Rectangle(texture=self.frost_texture,
                                            pos=self.pos,
                                            size=self.size)

        # Make sure the rectangle is sized/positioned to fill the screen
        self.frost_rect.pos = self.pos
        self.frost_rect.size = self.size

        # Schedule the update function to animate the glow
        Clock.unschedule(self.update_frost_effect)  # unschedule any old calls
        Clock.schedule_interval(self.update_frost_effect, 1/60.0)

    def on_size(self, *args):
        # If the frost overlay is active, resize it
        if self.frost_rect:
            self.frost_rect.pos = self.pos
            self.frost_rect.size = self.size


    def update_frost_effect(self, dt):
        import time
        elapsed = time.time() - self.frost_start_time

        if elapsed < self.frost_duration:
            # Still active: compute a glow alpha
            # Example: a simple sine wave for alpha between (base - amplitude) and (base + amplitude).
            import math
            glow = math.sin(elapsed * 2.0)  # 2.0 => glow speed; adjust to taste
            current_alpha = self.frost_base_alpha + self.frost_glow_amplitude * glow

            # Clamp alpha between 0 and 1
            current_alpha = max(0, min(1, current_alpha))

            # Update the color instruction for the frost overlay
            if self.frost_rect:
                # We have to re-enter the canvas.after context to change the color
                self.canvas.after.remove(self.frost_rect)
                with self.canvas.after:
                    Color(1, 1, 1, current_alpha)
                    self.frost_rect = Rectangle(texture=self.frost_texture,
                                                pos=self.pos,
                                                size=self.size)

        else:
            # Effect duration is over: remove the overlay and unschedule
            self.frost_active = False
            if self.frost_rect:
                self.canvas.after.remove(self.frost_rect)
                self.frost_rect = None
            from kivy.clock import Clock
            Clock.unschedule(self.update_frost_effect)


    def update_wildcard_color(self, dt):
        """
        Gradually interpolate the current wild card color toward the target color.
        Once the target is reached, move to the next color in the list.
        """
        speed = 5  # Adjust this value for faster or slower transitions
        for i in range(3):
            # Interpolate the current color channel value toward the target.
            self.wildcard_current_color[i] += (self.wildcard_target_color[i] - self.wildcard_current_color[i]) * speed * dt

        # If all channels are close enough to the target, snap to it and choose the next color.
        if all(abs(self.wildcard_current_color[i] - self.wildcard_target_color[i]) < 0.01 for i in range(3)):
            # Snap current color exactly to the target.
            self.wildcard_current_color = list(self.wildcard_target_color)
            # Update index to cycle through the colors.
            self.wildcard_color_index = (self.wildcard_color_index + 1) % len(self.wildcard_colors)
            self.wildcard_target_color = self.wildcard_colors[self.wildcard_color_index]



    def draw_game_state(self):
        """
        Draws the fixed board and the falling piece (with smooth interpolation) onto the Fbo.
        """
        # Calculate center offset (example from your current code).
        center_x = Window.width / 2 - (WALL_WIDTH / 2) * (BLOCK_SIZE / 2)
        center_y = Window.height / 2 + (WALL_HEIGHT / 2) * (ISO_BLOCK_HEIGHT / 2)

        # Draw fixed board (placed blocks).
        for row in range(WALL_HEIGHT):
            for col in range(WALL_WIDTH):
                cell = self.board[row][col]
                if cell > 0:
                    iso_x, iso_y = to_isometric(col * BLOCK_WIDTH, 0, row * ISO_BLOCK_HEIGHT)
                    adjusted_iso_y = iso_y - row * ISO_BLOCK_HEIGHT
                    # Choose texture based on cell value (example: bomb, gravity, wild, or normal).
                    if cell == 9:
                        block_texture = self.bomb_texture
                        Color(1, 1, 1, 1)
                    elif cell == 10:
                        block_texture = self.gravity_texture
                        Color(1, 1, 1, 1)
                    elif cell == 11:
                        block_texture = self.wildcard_texture
                        Color(self.wildcard_current_color[0],
                            self.wildcard_current_color[1],
                            self.wildcard_current_color[2], 1)

                    else:
                        block_texture = self.block_images[cell + 1]
                        Color(1, 1, 1, 1)
                    Rectangle(texture=block_texture,
                            pos=(center_x + iso_x, center_y + adjusted_iso_y),
                            size=(BLOCK_WIDTH, BLOCK_HEIGHT))
        
        # Draw falling piece with interpolation.
        fraction = self.time_since_last_fall / self.fall_speed
        for row_idx, row in enumerate(self.current_piece):
            for col_idx, cell in enumerate(row):
                if cell:
                    # Compute the interpolated (floating point) row.
                    float_row = self.current_row + fraction + row_idx
                    float_col = self.current_column + col_idx
                    iso_x, iso_y = to_isometric(float_col * BLOCK_WIDTH, 0, float_row * ISO_BLOCK_HEIGHT)
                    adjusted_iso_y = iso_y - float_row * ISO_BLOCK_HEIGHT
                    if cell == 9:
                        block_texture = self.bomb_texture
                        Color(1, 1, 1, 1)
                    elif cell == 10:
                        block_texture = self.gravity_texture
                        Color(1, 1, 1, 1)
                    elif cell == 11:
                        block_texture = self.wildcard_texture
                        Color(self.wildcard_current_color[0],
                            self.wildcard_current_color[1],
                            self.wildcard_current_color[2], 1)
                    else:
                        block_texture = self.block_images[cell + 1]
                        Color(1, 1, 1, 1)
                    Rectangle(texture=block_texture,
                            pos=(center_x + iso_x, center_y + adjusted_iso_y),
                            size=(BLOCK_WIDTH, BLOCK_HEIGHT))

    def load_block_images(self):
        block_images = {}
        # Load regular block textures from the sprite sheet.
        for i in range(10):
            block_images[i] = self.sprite_sheet.get_region(
                i * self.sprite_sheet.width / 10, 0,
                self.sprite_sheet.width / 10, self.sprite_sheet.height
            )
        from kivy.core.image import Image as CoreImage
        # Load bomb and gravity textures (already implemented)
        self.bomb_texture = CoreImage("Assets/Sprites/Powerups/bomb_block.png").texture
        self.gravity_texture = CoreImage("Assets/Sprites/Powerups/gravity_block.png").texture
        # Load the wild card texture.
        self.wildcard_texture = CoreImage("Assets/Sprites/Powerups/wild_card.png").texture
        self.frost_texture = CoreImage("Assets/Sprites/frost_effect.png").texture
        return block_images

    def draw_grid(self, *args):
        self.canvas.clear()
        with self.canvas:
            temporary_board_state = self.get_temporary_board_state(self.current_piece, self.current_column, self.current_row)
            center_x = Window.width / 2 - (WALL_WIDTH/2) * (BLOCK_SIZE/2)
            center_y = Window.height / 2 + (WALL_HEIGHT/2) * (ISO_BLOCK_HEIGHT/2)
            wall_array = temporary_board_state[::-1]
            for row in range(WALL_HEIGHT-1, -1, -1):
                for column in range(WALL_WIDTH-1, -1, -1):
                    block_value = wall_array[WALL_HEIGHT - 1 - row][column]
                    iso_x, iso_y = to_isometric(column * BLOCK_WIDTH, 0, row * ISO_BLOCK_HEIGHT)
                    adjusted_iso_y = iso_y - row * ISO_BLOCK_HEIGHT
                    if block_value > 0:
                        if block_value == 9:
                            block_texture = self.bomb_texture
                            Color(1, 1, 1, 1)
                        elif block_value == 10:
                            block_texture = self.gravity_texture
                            Color(1, 1, 1, 1)
                        elif block_value == 11:
                            # Use the wildcard texture and the smoothly transitioning color.
                            block_texture = self.wildcard_texture
                            Color(self.wildcard_current_color[0],
                                  self.wildcard_current_color[1],
                                  self.wildcard_current_color[2], 1)
                        else:
                            block_texture = self.block_images[block_value+1]
                            Color(1, 1, 1, 1)
                        
                        Rectangle(texture=block_texture, pos=(center_x + iso_x, center_y + adjusted_iso_y),
                                  size=(BLOCK_WIDTH, BLOCK_HEIGHT))
  
            #Shadow drawing logic
            # Distance from the bottom:
            distance = WALL_HEIGHT - self.current_row

            # Decide a threshold. If the piece is more than 'blur_threshold' rows from the bottom,
            # use the blurred shadow texture (block_images[1]). Otherwise use the sharp texture (block_images[0]).
            blur_threshold = 5

            #Check if the piece lands in the next move
            landing = self.check_if_will_land_next_step()
            piece_width = self.get_piece_width()
            block_texture = self.block_images[1]
            block_placed = [False] * WALL_WIDTH
            alpha = max(0.1, min(1, 0.1 + self.current_row * 0.02))
            Color(0.9, 0.9, 1, alpha)
            for row in range(WALL_HEIGHT):
                for column in range(WALL_WIDTH):
                    iso_x, iso_y = to_isometric(column * BLOCK_WIDTH, 0, row * ISO_BLOCK_HEIGHT)
                    adjusted_iso_y = iso_y - row * ISO_BLOCK_HEIGHT + ISO_BLOCK_HEIGHT
              
                    if (self.current_column <= column < self.current_column + piece_width) and landing == False:                     
                        for check_row in range(WALL_HEIGHT):
                            if (row + 1== WALL_HEIGHT and self.board[row][column] == 0 and not block_placed[column]):
                                    
                                    if (self.board[row][column-1] > 0) and self.board[row][column] != (19,0):
                                        block_texture = self.block_images[0]
                                        Rectangle(texture=block_texture, pos=(center_x + iso_x, center_y + adjusted_iso_y - ISO_BLOCK_HEIGHT),
                                        size=(BLOCK_WIDTH, BLOCK_HEIGHT))
                                        block_placed[column] = True
                                    else:
                                        block_texture = self.block_images[1]
                                        Rectangle(texture=block_texture, pos=(center_x + iso_x, center_y + adjusted_iso_y - ISO_BLOCK_HEIGHT),
                                            size=(BLOCK_WIDTH, BLOCK_HEIGHT))
                                        block_placed[column] = True

                            if (self.board[row][column] > 0 and not block_placed[column]):
                                if (self.board[row-1][column-1] > 0):
                                    block_texture = self.block_images[0]
                                    Rectangle(texture=block_texture, pos=(center_x + iso_x, center_y + adjusted_iso_y),
                                    size=(BLOCK_WIDTH, BLOCK_HEIGHT))
                                    block_placed[column] = True
                                else:
                                    block_texture = self.block_images[1]
                                    Rectangle(texture=block_texture, pos=(center_x + iso_x, center_y + adjusted_iso_y),
                                        size=(BLOCK_WIDTH, BLOCK_HEIGHT))
                                    block_placed[column] = True

    def check_if_will_land_next_step(self):
        simulated_row = self.current_row + 1

        for row in range(len(self.current_piece)):
            for col in range(len(self.current_piece[row])):
                if self.current_piece[row][col] > 0:  # Part of the block
                    board_row = simulated_row + row
                    board_col = self.current_column + col

                    # Ensure the indices are within the board's range
                    if 0 <= board_row < len(self.board) and 0 <= board_col < len(self.board[0]):
                        if board_row >= WALL_HEIGHT or self.board[board_row][board_col] > 0:
                            return True
                    else:
                        # Handle the case where the check is outside the board's bounds
                        # For example, you might consider a piece at the bottom if it's trying to move below the board
                        if board_row >= WALL_HEIGHT:
                            return True

        return False
    
    def get_piece_width(self):
        """
        Calculate the width of the current falling piece.

        :return: Width of the piece.
        """
        current_piece = self.current_piece
        leftmost = float('inf')
        rightmost = float('-inf')

        for row in current_piece:
            for column, cell in enumerate(row):
                if cell:
                    leftmost = min(leftmost, column)
                    rightmost = max(rightmost, column)

        if leftmost == float('inf') or rightmost == float('-inf'):
            return 0

        return rightmost - leftmost + 1


    def running(self, dt):
        
        self.time_since_last_fall += dt

        self.draw_grid()
        self.draw_game_state()

        # Logic to handle the falling piece
        if self.time_since_last_fall >= self.fall_speed:
            self.time_since_last_fall = 0
            self.current_row += 1
            should_redraw = True

        # If the piece cannot move down anymore, place it and load the next piece
        if not self.valid_space(self.current_piece, (self.current_column, self.current_row)):
            self.current_row -= 1
            self.place_piece()

            # Load the next piece and update the upcoming blocks array
            self.current_piece = self.next_piece
            self.upcoming_blocks.pop(0)  # Remove the used block
            self.upcoming_blocks.append(self.choose_piece())  # Add a new block using weighted choice
            self.next_piece = self.upcoming_blocks[0]  # Update the next piece


            # Update the display of the next piece
            if self.ui_ref and self.next_piece_ref:
                next_piece_pos = self.ui_ref.update_rect_positions()
                self.next_piece_ref.draw_piece(self.next_piece, next_piece_pos)

            # Reset the position for the new piece
            self.current_column, self.current_row = 3, 0
            should_redraw = True

        # Check and update the high score
        if self.score > self.highscore:
            self.highscore = self.score
            # Save the new high score immediately after it's updated
            handle_data('highscore', 'save', self.highscore)

        # Update the UI with the current score, high score, and level
        if self.ui_ref:
            self.ui_ref.update_labels(self.score, self.highscore, self.level)

    def funcscore(self):
        return self.score
    
    def funchighscore(self):
        return self.highscore

    def get_temporary_board_state(self, current_piece, current_column, current_row):
        """
        Get a temporary board state including the current falling piece.

        :param current_piece: The currently falling piece.
        :param current_column: The column position of the current piece.
        :param current_row: The row position of the current piece.
        :return: Temporary board state including the current piece.
        """
        temp_board = [row[:] for row in self.board]
        for row_index, row in enumerate(current_piece):
            for column_index, cell in enumerate(row):
                if cell:
                    if 0 <= row_index + current_row < WALL_HEIGHT and 0 <= column_index + current_column < WALL_WIDTH:
                        temp_board[row_index + current_row][column_index + current_column] = cell
        return temp_board

    
    def place_piece(self):
        """
        Place the current piece on the board.
        """
        for row_index, row in enumerate(self.current_piece):
            for column_index, cell in enumerate(row):
                if cell:
                    self.board[self.current_row + row_index][self.current_column + column_index] = cell

        cleared_lines = self.check_line_for_lines_cleared()
        self.level, self.fall_speed = self.determine_level_and_fall_speed(cleared_lines, self.fall_speed)
        self.score += self.calculate_score(cleared_lines, self.level)


        self.highscore = handle_data('highscore', 'get')

        
            
        if not self.valid_space(self.current_piece, (self.current_column, self.current_row)):
            self.game_over = True


    def calculate_score(self, cleared_lines, level):
        if cleared_lines == 1:
            base_points = 40
        elif cleared_lines == 2:
            base_points = 100
        elif cleared_lines == 3:
            base_points = 300
        else:  # cleared_lines == 4 (Tetris)
            base_points = 1200

        return (cleared_lines * base_points) * level
    
    def determine_level_and_fall_speed(self, lines_cleared, initial_fall_speed):
        """Calculates the current level and the corresponding fall speed.

        Args:
            lines_cleared: The total number of lines cleared by the player.
            initial_fall_speed: The fall speed (in milliseconds) at level 1.

        Returns:
            tuple: (current_level, fall_speed)
        """

        level = lines_cleared // 10 + 1  # Calculate level based on lines cleared

        # Determine fall speed
        level_adjustment = initial_fall_speed * (0.1 * (level - 1))  
        fall_speed = initial_fall_speed - level_adjustment


        return level, fall_speed 

    def valid_space(self, shape, position):
        """
        Check if a given shape can fit into a given position on the board.

        :param shape: The 2D list representing the shape of the piece.
        :param position: A tuple (column, row) representing the top-left position of the shape on the board.
        :return: True if the shape fits in the position without colliding or going out of bounds, False otherwise.
        """
        off_column, off_row = position
        for row_index, row in enumerate(shape):
            for column_index, cell in enumerate(row):
                if cell:
                    if (column_index + off_column < 0 or column_index + off_column >= WALL_WIDTH or row_index + off_row >= WALL_HEIGHT):
                        return False
                    if self.board[row_index + off_row][column_index + off_column] != 0:
                        return False
        return True
    
    def check_line_for_lines_cleared(self):
        """
        Check if any lines are fully filled, clear them, and apply powerup effects.
        
        :return: Number of lines cleared.
        """
        lines_cleared = 0
        for row_index in range(WALL_HEIGHT):
            if all(cell != 0 for cell in self.board[row_index]):
                # Apply powerup effects before clearing the row.
                from powerup import apply_powerups
                apply_powerups(self, self.board[row_index], row_index)
                
                lines_cleared += 1
                # Clear the row.
                self.board[row_index] = [0 for _ in range(WALL_WIDTH)]
                # Shift all rows above this row down by one.
                for prev_row_index in range(row_index, 0, -1):
                    self.board[prev_row_index] = self.board[prev_row_index - 1][:]
                self.board[0] = [0 for _ in range(WALL_WIDTH)]
        return lines_cleared


    
    def rotate(self, shape):
        """
        Rotate the given shape.

        :param shape: The shape to rotate.
        :return: Rotated shape.
        """
        rotated_piece = [list(row) for row in zip(*shape[::-1])]
        self.draw_grid()
        return rotated_piece

    def on_touch_down(self, touch):
        """
        Handle touch down event.

        :param touch: Touch event.
        """
        touch.ud['touch_start'] = (touch.x, touch.y)

    def on_touch_up(self, touch):
        """
        Handle touch up event.

        :param touch: Touch event.
        """
        dx = touch.x - touch.ud['touch_start'][0]  # Change in x-coordinate
        dy = touch.y - touch.ud['touch_start'][1]  # Change in y-coordinate
        min_swipe_distance = 50  # Minimum distance to consider it a swipe

        # Check for vertical swipe
        if abs(dy) > abs(dx) and abs(dy) > min_swipe_distance:
            self.draw_grid()
            if dy > 0:
                # Swipe up
                rotated_piece = self.rotate(self.current_piece)
                if self.valid_space(rotated_piece, (self.current_column, self.current_row)):
                    self.current_piece = rotated_piece
                    self.draw_grid()
            else:
                # Swipe down
                while self.valid_space(self.current_piece, (self.current_column, self.current_row + 1)):
                    self.current_row += 1

                self.draw_grid()
                if not self.valid_space(self.current_piece, (self.current_column, self.current_row)):
                    self.game_over = True
        # Check for horizontal swipe
        elif abs(dx) > min_swipe_distance:
            if dx > 0:
                # Swipe right
                self.current_column += 1
            else:
                # Swipe left
                self.current_column -= 1

            self.draw_grid()

            # Check if the new position is valid, if not, undo the move
            if not self.valid_space(self.current_piece, (self.current_column, self.current_row)):
                if dx > 0:
                    # Undo right swipe
                    self.current_column -= 1
                else:
                    # Undo left swipe
                    self.current_column += 1
                self.draw_grid()

    def _keyboard_closed(self):
        self._keyboard.unbind(on_key_down=self._on_keyboard_down)
        self._keyboard = None

    def _on_keyboard_down(self, keyboard, keycode, text, modifiers):
        """
        Handle keyboard key press events.

        :param keyboard: The keyboard instance.
        :param keycode: Tuple containing the key code and string representation.
        :param text: Text of the pressed key.
        :param modifiers: List of any modifiers used (shift, ctrl, etc.).
        """
        key = keycode[1]  # Get the string representation of the key

        if key in ('up', 'w'):
            # Handle up movement or rotation
            rotated_piece = self.rotate(self.current_piece)
            if self.valid_space(rotated_piece, (self.current_column, self.current_row)):
                self.current_piece = rotated_piece
        elif key in ('down', 's'):
            # Handle down movement
            while self.valid_space(self.current_piece, (self.current_column, self.current_row + 1)):
                self.current_row += 1
            if not self.valid_space(self.current_piece, (self.current_column, self.current_row)):
                self.game_over = True
        elif key in ('left', 'a'):
            # Handle left movement
            self.current_column -= 1
            if not self.valid_space(self.current_piece, (self.current_column, self.current_row)):
                self.current_column += 1  # Undo the move if invalid
        elif key in ('right', 'd'):
            # Handle right movement
            self.current_column += 1
            if not self.valid_space(self.current_piece, (self.current_column, self.current_row)):
                self.current_column -= 1  # Undo the move if invalid

        self.draw_grid()  # Redraw the grid after movement

        return True  # Return True to accept the key. Otherwise, it could be used by other widgets.

