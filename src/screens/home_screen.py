# src/screens/home_screen.py
from kivy.app import App
from kivy.uix.widget import Widget
from kivy.graphics import Rectangle, Color, Line, Fbo, RenderContext, BindTexture
from kivy.core.window import Window
from kivy.core.image import Image as CoreImage
from kivy.uix.image import Image
from kivy.clock import Clock
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.animation import Animation
import random, os, time, tempfile
from kivy.utils import platform
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.image import Image
from kivy.properties import NumericProperty
from kivy.animation import Animation
from kivy.uix.widget import Widget
from kivy.graphics import Color, Line, Rectangle, ClearColor, ClearBuffers
import math

from src.utils.constants import (
    WINDOW_CLEARCOLOR,
    WALL_WIDTH, WALL_HEIGHT,
    BLOCK_SIZE, BLOCK_WIDTH, BLOCK_HEIGHT,
    ISO_BLOCK_HEIGHT, ISO_MATRIX,
    SPRITE_SHEET_PATH, GAME_SPEED
)
from src.utils.helpers import to_isometric

if platform == 'android':
    from android.permissions import request_permissions, Permission

Window.clearcolor = WINDOW_CLEARCOLOR

def to_isometric(column, row, z):
    iso_x = ISO_MATRIX[0][0] * column + ISO_MATRIX[0][1] * row
    iso_y = ISO_MATRIX[1][0] * column + ISO_MATRIX[1][1] * row + ISO_MATRIX[1][2] * z
    return iso_x, iso_y

class RoomBackground(Widget):
    def __init__(self, **kwargs):
        super(RoomBackground, self).__init__(**kwargs)
        self.bind(pos=self.update_canvas, size=self.update_canvas)
        self.update_canvas()

    def update_canvas(self, *args):
        self.canvas.clear()
        with self.canvas:
            # Fill background with a pink color for the room.
            Color(198 / 255.0, 40 / 255.0, 78 / 255.0, 1)  # adjust for your desired pink
            Rectangle(pos=self.pos, size=self.size)

            # --- Calculate the starting point ---
            # Constants from your Tetris game:
            WALL_WIDTH = 10
            WALL_HEIGHT = 20
            BLOCK_SIZE = 60
            ISO_BLOCK_HEIGHT = BLOCK_SIZE // 2

            column = WALL_WIDTH - 1
            row = WALL_HEIGHT - 1

            center_x = self.width / 2 - (WALL_WIDTH / 2) * (BLOCK_SIZE / 2)
            center_y = self.height / 2 + (WALL_HEIGHT / 2) * (ISO_BLOCK_HEIGHT / 2)

            iso_x, iso_y = to_isometric(column * BLOCK_WIDTH, 0, row * ISO_BLOCK_HEIGHT)

            # Compute a center offset (similar to your IsometricGrid logic)
        
            
            # The bottom–right block: use column = WALL_WIDTH - 1, and bottom row = 0.
            # Assume its "back" (i.e. top of block in z) is at z = BLOCK_SIZE.
            adjusted_iso_y = iso_y - row * ISO_BLOCK_HEIGHT
        
            start_x = center_x + iso_x + (BLOCK_WIDTH // 2)
            start_y = center_y + adjusted_iso_y + ISO_BLOCK_HEIGHT

            # --- Define three directions:
            # Up (in screen space) is (0, 1)
            L = 1000  # length of the perspective lines
            up_dx, up_dy = 0, L

            # 60 degrees to the left: rotate (0,1) by +60° (counterclockwise)
            left_dx = -1 * L  # ~ -0.866*L
            left_dy = math.cos(math.radians(120)) * L     # ~ 0.5*L

            # 60 degrees to the right: rotate (0,1) by -60° (clockwise)
            right_dx = math.sin(math.radians(120)) * L    # ~ 0.866*L
            right_dy = math.cos(math.radians(120)) * L      # ~ 0.5*L

            end_up = (start_x + up_dx, start_y + up_dy)
            end_left = (start_x + left_dx, start_y + left_dy)
            end_right = (start_x + right_dx, start_y + right_dy)

            # --- Draw the perspective lines (simulate the room's edges)
            Color(0.5, 0.3, 0.4, 1)  # a darker hue for the edges; adjust as needed
            Line(points=[start_x, start_y, end_up[0], end_up[1]], width=2)
            Line(points=[start_x, start_y, end_left[0], end_left[1]], width=2)
            Line(points=[start_x, start_y, end_right[0], end_right[1]], width=2)

class AnimatedImageButton(ButtonBehavior, Image):
    scale = NumericProperty(1)
    
    def __init__(self, **kwargs):
        super(AnimatedImageButton, self).__init__(**kwargs)
        # When the widget's size is set by its parent, record its original size.
        self.bind(size=self._on_size)
        # Bind our scale property to update our size.
        self.bind(scale=self._update_scale)
        # Bind on_press and on_release to trigger animations.
        self.bind(on_press=self.animate_down, on_release=self.animate_up)

    def _on_size(self, instance, value):
        # Save the current size as our base size.
        self._base_size = value

    def _update_scale(self, instance, value):
        # Update the size relative to the base size.
        if hasattr(self, '_base_size'):
            self.size = (self._base_size[0] * value, self._base_size[1] * value)

    def animate_down(self, *args):
        Animation(scale=0.9, duration=0.1).start(self)

    def animate_up(self, *args):
        Animation(scale=1, duration=0.1).start(self)

class IsometricGrid(Widget):  
    shapes = [
        [[1, 1, 1], [0, 1, 0]],  # T shape
        [[0, 2, 2], [2, 2, 0]],  # Z shape
        [[3, 3, 0], [0, 3, 3]],  # S shape
        [[4, 0, 0], [4, 4, 4]],  # J shape
        [[0, 0, 5], [5, 5, 5]],  # L shape
        [[6, 6], [6, 6]],        # O shape
        [[7, 7, 7, 7]]           # I shape
    ]
    
    def __init__(self, board, **kwargs):
        super().__init__(**kwargs)
        
        self.board = board
        self.sprite_sheet = CoreImage(SPRITE_SHEET_PATH).texture
        self.block_images = self.load_block_images()

        # Initial position for the falling piece
        self.current_piece = random.choice(self.shapes)
        self.current_piece_position = [WALL_WIDTH // 2 - len(self.current_piece[0]) // 2, 0]
        self.current_rotation = 0

        # Game state flags
        self.game_over = False

        # Initialize AI movement
        self.best_rotation = 0
        self.best_x = self.current_piece_position[0]
        self.ai_move()

        # Start the game loop with adjustable speed
        Clock.schedule_interval(self.update, GAME_SPEED)


    def load_block_images(self):
        """
        Load block images from the sprite sheet.
        """
        block_images = {}
        for i in range(10):
            block_images[i] = self.sprite_sheet.get_region(
                i * self.sprite_sheet.width / 10, 0,
                self.sprite_sheet.width / 10, self.sprite_sheet.height
            )
        return block_images

    def update_fbo(self, *args):
        self.fbo.size = self.size

    def draw_grid(self, *args):
        """
        Draw the isometric grid onto the canvas directly.
        """
        self.canvas.clear()
        with self.canvas:
            Color(1, 1, 1, 1)
            center_x = self.width / 2 - (WALL_WIDTH / 2) * (BLOCK_SIZE / 2)
            center_y = self.height / 2 + (WALL_HEIGHT / 2) * (ISO_BLOCK_HEIGHT / 2)
            wall_array = self.board[::-1]
            for row in range(WALL_HEIGHT - 1, -1, -1):
                for column in range(WALL_WIDTH - 1, -1, -1):
                    block_value = wall_array[WALL_HEIGHT - 1 - row][column]
                    iso_x, iso_y = to_isometric(column * BLOCK_WIDTH, 0, row * ISO_BLOCK_HEIGHT)
                    adjusted_iso_y = iso_y - row * ISO_BLOCK_HEIGHT
                    if block_value > 0:
                        block_texture = self.block_images[block_value + 1]
                        Rectangle(texture=block_texture, pos=(center_x + iso_x, center_y + adjusted_iso_y),
                                  size=(BLOCK_WIDTH, BLOCK_HEIGHT))


    def valid_space(self, shape, position):
        """
        Check if a given shape can fit into a given position on the board.
        """
        off_column, off_row = position
        for row_index, row in enumerate(shape):
            for column_index, cell in enumerate(row):
                if cell:
                    x = column_index + off_column
                    y = row_index + off_row
                    if x < 0 or x >= WALL_WIDTH or y >= WALL_HEIGHT:
                        return False
                    if y >= 0 and self.board[y][x] != 0:
                        return False
        return True

    def rotate_piece(self, piece):
        """
        Rotate a piece clockwise.
        """
        return [list(row) for row in zip(*piece[::-1])]

    def place_piece(self, piece, position):
        """
        Place the piece on the board.
        """
        for row_index, row in enumerate(piece):
            for column_index, cell in enumerate(row):
                if cell:
                    x = position[0] + column_index
                    y = position[1] + row_index
                    if 0 <= x < WALL_WIDTH and 0 <= y < WALL_HEIGHT:
                        self.board[y][x] = cell

    def remove_piece(self, piece, position):
        """
        Remove the piece from the board.
        """
        for row_index, row in enumerate(piece):
            for column_index, cell in enumerate(row):
                if cell:
                    x = position[0] + column_index
                    y = position[1] + row_index
                    if 0 <= x < WALL_WIDTH and 0 <= y < WALL_HEIGHT:
                        self.board[y][x] = 0

    def lock_piece(self):
        """
        Lock the current piece into the board.
        """
        pass  # The piece is already placed on the board

    def clear_lines(self):
        """
        Clear completed lines from the board.
        """
        new_board = [row for row in self.board if any(cell == 0 for cell in row)]
        lines_cleared = WALL_HEIGHT - len(new_board)
        for _ in range(lines_cleared):
            new_board.insert(0, [0 for _ in range(WALL_WIDTH)])
        self.board = new_board

    def update(self, dt):
        if self.game_over:
            return

        # Remove the current piece from the board
        self.remove_piece(self.current_piece, self.current_piece_position)

        # AI-controlled movement
        # Rotate the piece if needed
        if self.current_rotation != self.best_rotation:
            self.current_piece = self.rotate_piece(self.current_piece)
            self.current_rotation = (self.current_rotation + 1) % 4
        # Move the piece towards best_x
        elif self.current_piece_position[0] < self.best_x:
            self.current_piece_position[0] += 1
        elif self.current_piece_position[0] > self.best_x:
            self.current_piece_position[0] -= 1
        else:
            # Move the piece down
            self.current_piece_position[1] += 1
            if not self.valid_space(self.current_piece, self.current_piece_position):
                # Can't move down, move back up
                self.current_piece_position[1] -= 1
                # Place the piece back into the board
                self.place_piece(self.current_piece, self.current_piece_position)
                # Lock the piece
                self.lock_piece()
                self.clear_lines()
                # Spawn new piece
                self.current_piece = random.choice(self.shapes)
                self.current_piece_position = [WALL_WIDTH // 2 - len(self.current_piece[0]) // 2, 0]
                self.current_rotation = 0
                if not self.valid_space(self.current_piece, self.current_piece_position):
                    # Game over
                    self.game_over = True
                    Clock.unschedule(self.update)
                    print("Game Over")
                    return
                # Calculate AI move for the new piece
                self.ai_move()

        # Place the current piece back into the board
        self.place_piece(self.current_piece, self.current_piece_position)

        # Redraw the grid
        self.draw_grid()

    def ai_move(self):
        best_score = None
        best_rotation = 0
        best_x = 0

        original_piece = self.current_piece
        for rotation in range(4):
            piece = original_piece
            for _ in range(rotation):
                piece = self.rotate_piece(piece)
            for x in range(-2, WALL_WIDTH):
                y = 0
                position = [x, y]
                if not self.valid_space(piece, position):
                    continue
                # Simulate dropping the piece
                while self.valid_space(piece, position):
                    position[1] += 1
                position[1] -= 1  # Last valid position
                if position[1] < 0:
                    continue  # Skip invalid positions

                # Simulate the board state
                temp_board = [row[:] for row in self.board]  # Deep copy
                self.place_piece_on_board(piece, position, temp_board)
                temp_board = self.simulate_clear_lines(temp_board)
                score = self.evaluate_board(temp_board)
                if best_score is None or score > best_score:
                    best_score = score
                    best_rotation = rotation
                    best_x = x

        self.best_rotation = (self.current_rotation + best_rotation) % 4
        self.best_x = best_x

    def place_piece_on_board(self, piece, position, board):
        """
        Place the piece on a temporary board.
        """
        for row_index, row in enumerate(piece):
            for column_index, cell in enumerate(row):
                if cell:
                    x = position[0] + column_index
                    y = position[1] + row_index
                    if 0 <= x < WALL_WIDTH and 0 <= y < WALL_HEIGHT:
                        board[y][x] = cell

    def simulate_clear_lines(self, board):
        """
        Simulate line clearing on a temporary board.
        """
        new_board = [row for row in board if any(cell == 0 for cell in row)]
        lines_cleared = WALL_HEIGHT - len(new_board)
        for _ in range(lines_cleared):
            new_board.insert(0, [0 for _ in range(WALL_WIDTH)])
        return new_board

    def evaluate_board(self, board):
        """
        Evaluate the board state for the AI.
        """
        heights = [0] * WALL_WIDTH
        for x in range(WALL_WIDTH):
            for y in range(WALL_HEIGHT):
                if board[y][x]:
                    heights[x] = WALL_HEIGHT - y
                    break
        aggregate_height = sum(heights)
        holes = 0
        for x in range(WALL_WIDTH):
            block_found = False
            for y in range(WALL_HEIGHT):
                if board[y][x]:
                    block_found = True
                elif block_found and y < len(board) and not board[y][x]:
                    holes += 1
        bumpiness = sum([abs(heights[i] - heights[i + 1]) for i in range(WALL_WIDTH - 1)])
        # AI scoring weights
        score = -0.51066 * aggregate_height - 0.35663 * holes - 0.184483 * bumpiness
        return score

class HomeScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        layout = FloatLayout()

        # Add the room background first (index 0 so it is drawn behind)
        room_bg = RoomBackground(size_hint=(1, 1), pos_hint={'x': 0, 'y': 0})
        layout.add_widget(room_bg, index=0)

        # Background image for the home screen title (already added as before)
        bg_image = Image(
            source="Assets/Sprites/Home/tetris_homescreen.png",
            pos_hint={'center_x': 0.5, 'center_y': 0.85},
            size_hint=(0.7, 0.7),
            allow_stretch=True,
            keep_ratio=True
        )
        layout.add_widget(bg_image, index=0)


        # AI Tetris in the background
        board = [[0]*WALL_WIDTH for _ in range(WALL_HEIGHT)]
        self.tetris_ai = IsometricGrid(board=board)
        layout.add_widget(self.tetris_ai, index=1)

        # Replace the Start button with an image button.
        start_button = AnimatedImageButton(
            source="Assets/Sprites/Home/Buttons/startgame_button.png",
            size_hint=(0.3, 0.1),  # adjust size as needed
            pos_hint={'center_x': 0.5, 'center_y': 0.4}
        )
        start_button.bind(on_release=self.start_game)
        layout.add_widget(start_button, index=1)

        # Replace the Settings button with an image button.
        settings_button = AnimatedImageButton(
            source="Assets/Sprites/Home/Buttons/settings_button.png",
            size_hint=(0.3, 0.1),
            pos_hint={'center_x': 0.5, 'center_y': 0.3}
        )
        settings_button.bind(on_release=self.goto_settings)
        layout.add_widget(settings_button, index=1)

        # Replace the Quit button with an image button.
        quit_button = AnimatedImageButton(
            source="Assets/Sprites/Home/Buttons/quit_button.png",
            size_hint=(0.3, 0.1),
            pos_hint={'center_x': 0.5, 'center_y': 0.2}
        )
        quit_button.bind(on_release=self.quit_game)
        layout.add_widget(quit_button, index=1)

        self.add_widget(layout)



    def goto_settings(self, instance):
        # Switch to a settings screen if you have one
        print("Open settings...")
        # If you want to switch screens:
        self.manager.current = 'settings'

    def quit_game(self, instance):
        App.get_running_app().stop()

    
    def start_game(self, instance):
        # If you want to switch screens:
        self.manager.current = 'game'
        # or do something else, e.g. print, start playing, etc.
        print("Start the game logic here!")



    def getImageFileFromSheet(self, x, y, width, height, sheet_path):
        """
        1) Load the sheet as a texture
        2) Crop the region
        3) Create a new CoreImage from that region
        4) Save to a temporary file
        5) Return the file path (string) to use in background_normal
        """
        # 1) Full sprite sheet as a CoreImage
        sheet_image = CoreImage(sheet_path)
        # 2) Crop region from the texture
        cropped_tex = sheet_image.texture.get_region(x, y, width, height)
        # 3) Turn that texture into a new CoreImage
        cropped_image = CoreImage(cropped_tex)
        # 4) Save it to a tmp file
        tmp_dir = tempfile.gettempdir()
        filename = f"{tmp_dir}/kivy_sprite_{time.time()}.png"
        cropped_image.save(filename)
        # 5) Return the path
        return filename