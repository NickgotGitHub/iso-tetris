# main.py
from kivy.app import App
from kivy.uix.widget import Widget
from kivy.graphics import Rectangle, Color, Line, Fbo, RenderContext, BindTexture
from kivy.core.window import Window
from kivy.core.image import Image as CoreImage
from kivy.clock import Clock
from kivy.uix.floatlayout import FloatLayout
import random
from kivy.utils import platform

if platform == 'android':
    from android.permissions import request_permissions, Permission

Window.clearcolor = (198 / 255.0, 40 / 255.0, 78 / 255.0, 1)

WALL_WIDTH, WALL_HEIGHT = 10, 20
BLOCK_SIZE = 60
BLOCK_WIDTH = BLOCK_SIZE
BLOCK_HEIGHT = BLOCK_SIZE
ISO_BLOCK_HEIGHT = BLOCK_HEIGHT // 2
ISO_MATRIX = [[0.5, -0.5], [0.25, 0.25, 0]]

SPRITE_SHEET_PATH = 'Assets/Sprites/sprite_sheet.png'

# Introduce the GAME_SPEED variable
GAME_SPEED = 0.04  # Lower value = faster game speed

def to_isometric(column, row, z):
    iso_x = ISO_MATRIX[0][0] * column + ISO_MATRIX[0][1] * row
    iso_y = ISO_MATRIX[1][0] * column + ISO_MATRIX[1][1] * row + ISO_MATRIX[1][2] * z
    return iso_x, iso_y

class IsometricGrid(Widget):  
    shapes = [
        [[1, 1, 1], [0, 1, 0]],  # T shape
        [[0, 2, 2], [2, 2, 0]],  # Z shape
        [[3, 3, 0], [0, 3, 3]],  # S shape
        [[4, 0, 0], [4, 4, 4]],  # J shape
        [[0, 0, 5], [5, 5, 5]],  # L shape
        [[6, 6], [6, 6]],        # O shape
        [[7, 7, 7, 7]],           # I shape
        [[8]]
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

class IsometricApp(App):
    
    def build(self):
        if platform == 'android':
            request_permissions([Permission.READ_EXTERNAL_STORAGE, Permission.WRITE_EXTERNAL_STORAGE])
    
        # Create the main layout
        main_layout = FloatLayout()

        # Create the game board
        board = [[0 for _ in range(WALL_WIDTH)] for _ in range(WALL_HEIGHT)]
        self.game_widget = IsometricGrid(board=board)

        # Add the game widget to the main layout
        main_layout.add_widget(self.game_widget)

        return main_layout

if __name__ == '__main__':
    IsometricApp().run()
