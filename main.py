from kivy.app import App
from kivy.uix.widget import Widget
from kivy.graphics import Rectangle
from kivy.core.window import Window
from kivy.core.image import Image as CoreImage  # Used to load the sprite sheet
import random
from kivy.clock import Clock
import ast

# Set the background color for the entire window
Window.clearcolor = (198 / 255.0, 40 / 255.0, 78 / 255.0, 1)  # Normalized RGBA for the background color

# Constants
WALL_WIDTH, WALL_HEIGHT = 10, 20  # Updated to 10x10
BLOCK_SIZE = 60  # Adjusted block size
block_width = BLOCK_SIZE
block_height = BLOCK_SIZE
iso_block_height = block_height // 2
ISO_MATRIX = [[0.5, -0.5], [0.25, 0.25, 0]]

sprite_sheet_path = 'sprite_sheet.png'  # Path to your sprite sheet

def to_isometric(x, y, z):
    iso_x = ISO_MATRIX[0][0] * x + ISO_MATRIX[0][1] * y
    iso_y = ISO_MATRIX[1][0] * x + ISO_MATRIX[1][1] * y + ISO_MATRIX[1][2] * z
    return iso_x, iso_y

class IsometricGrid(Widget):
    def __init__(self, board, **kwargs):
        super(IsometricGrid, self).__init__(**kwargs)
        self.board = board  # Store the 10x20 board array
        self.sprite_sheet = CoreImage(sprite_sheet_path).texture
        self.block_images = self.load_block_images()
        self.bind(size=self.draw_grid)
        self.bind(pos=self.draw_grid)
        self.current_x, self.current_y = 0, 3
        self.game_over = False
        self.current_piece = random.choice(self.shapes)
        self.time_since_last_fall = 0
        self.fall_speed = 1300
        self.score = 0
        Clock.schedule_interval(self.running, 1.0 / 60.0)
        self.time_since_last_fall = 0
        self.fall_speed = 0.5

    def load_block_images(self):
        block_images = {}
        for i in range(8):  # Assuming 8 different block types
            block_images[i + 1] = self.sprite_sheet.get_region(
                i * self.sprite_sheet.width / 8, 0,
                self.sprite_sheet.width / 8, self.sprite_sheet.height
            )
        return block_images

    def draw_grid(self, *args):
        self.canvas.clear()
        with self.canvas:
            temporary_board_state = self.get_temporary_board_state(self.current_piece, self.current_x, self.current_y)
            formatted_text = self.format_board_state(temporary_board_state)
            evaluated_board_state = ast.literal_eval(formatted_text)
            center_x = Window.width / 2.5
            center_y = Window.height / 1.5

            for y in range(WALL_HEIGHT-1, -1, -1):
                for x in range(WALL_WIDTH-1, -1, -1):
                    wall_array = evaluated_board_state[::-1]
                    block_value = wall_array[WALL_HEIGHT - 1 - y][x]
                    # Only draw if block_value is not 0
                    if block_value > 0:
                        iso_x, iso_y = to_isometric(x * block_width, 0, y * iso_block_height)
                        adjusted_iso_y = iso_y - y * iso_block_height

                        block_texture = self.block_images[block_value]
                        Rectangle(texture=block_texture, pos=(center_x + iso_x, center_y + adjusted_iso_y),
                              size=(block_width, block_height))

    

    def running(self, dt):
        self.time_since_last_fall += dt
        if self.time_since_last_fall >= self.fall_speed:
            self.time_since_last_fall = 0
            self.current_y += 1
        # Attempt to move the piece down
        if not self.valid_space(self.current_piece, (self.current_x, self.current_y)):
            self.current_y -= 1  # Revert the move if the space is not valid
            self.place_piece()  # Lock the piece in its current position on the board
            
            # Select a new piece and reset the position for the new piece
            self.current_piece = random.choice(self.shapes)
            self.current_x, self.current_y = 3, 0

            # Check if the new piece can be placed at the starting position
            if not self.valid_space(self.current_piece, (self.current_x, self.current_y)):
                self.game_over = True  # End the game if the new piece cannot be placed
                print("Game Over")
        #print the board state
        
        self.draw_grid()  # Redraw the board with the updated state


        

    def get_temporary_board_state(self, current_piece, current_x, current_y):
            """
            Creates a temporary board state including the current falling piece.
            :param current_piece: The currently falling piece
            :param current_x: X position of the current piece
            :param current_y: Y position of the current piece
            :return: Temporary board state including the current piece
            """
            temp_board = [row[:] for row in self.board]
            for y, row in enumerate(current_piece):
                for x, cell in enumerate(row):
                    if cell:
                        # Ensure the piece is within the board bounds before placing it
                        if 0 <= y + current_y < WALL_HEIGHT and 0 <= x + current_x < WALL_WIDTH:
                            temp_board[y + current_y][x + current_x] = cell
            return temp_board

        

    def format_board_state(self, board_state):
            """
            Formats the given board state into a string for display or debugging.
            :param board_state: The current board state as a 2D list.
            :return: A string representing the formatted board state.
            """
            formatted_text = "[\n" + ",\n".join(
                [" [" + ", ".join(str(cell) for cell in row) + "]" for row in board_state]
            ) + "\n]"
            return formatted_text

    
    def place_piece(self):
        # Loop through each block in the piece's shape
        for y, row in enumerate(self.current_piece):
            for x, cell in enumerate(row):
                if cell:  # If the cell is not empty (0 means empty, any other value represents a piece block)
                    # Update the board's cell to the value of the piece's cell
                    self.board[self.current_y + y][self.current_x + x] = cell

        # After placing the piece, you might want to check for complete lines, update the score, etc.
        cleared_lines = self.check_line_for_lines_cleared()
        self.score += cleared_lines

        # Then, generate a new piece and reset its position
        self.current_piece = random.choice(self.shapes)
        self.current_x, self.current_y = 3, 0

        # Optionally, you can also check if the new piece can be placed; if not, the game is over
        if not self.valid_space(self.current_piece, (self.current_x, self.current_y)):
            self.game_over = True

    def valid_space(self, shape, position):
        """
        Check if a given shape can fit into a given position on the board.
        
        :param shape: The 2D list representing the shape of the piece.
        :param position: A tuple (x, y) representing the top-left position of the shape on the board.
        :return: True if the shape fits in the position without colliding or going out of bounds, False otherwise.
        """
        off_x, off_y = position
        for y, row in enumerate(shape):
            for x, cell in enumerate(row):
                if cell:  # If the cell in the shape is not empty
                    # Check if the position is outside the board boundaries
                    if (x + off_x < 0 or x + off_x >= WALL_WIDTH or y + off_y >= WALL_HEIGHT):
                        return False
                    # Check if the position collides with a filled space on the board
                    if self.board[y + off_y][x + off_x] != 0:
                        return False
        return True


    
    def check_line_for_lines_cleared(self):
        lines_cleared = 0
        for y in range(WALL_HEIGHT):
            if all(cell != 0 for cell in self.board[y]):
                lines_cleared += 1
                # Clear the line by setting all its cells to 0
                self.board[y] = [0 for _ in range(WALL_WIDTH)]
                # Move down all lines above the cleared line
                for prev_y in range(y, 0, -1):
                    self.board[prev_y] = self.board[prev_y - 1][:]
                self.board[0] = [0 for _ in range(WALL_WIDTH)]
        return lines_cleared
    
    def rotate(self, shape):
        return [list(row) for row in zip(*shape[::-1])]

    def on_touch_down(self, touch):
        touch.ud['touch_start'] = (touch.x, touch.y)  # Store the starting point of the touch

    def on_touch_up(self, touch):
        dx = touch.x - touch.ud['touch_start'][0]  # Calculate the change in the x-coordinate
        dy = touch.y - touch.ud['touch_start'][1]  # Calculate the change in the y-coordinate
        min_swipe_distance = 50  # Set a minimum threshold for a swipe to be recognized

        # Check if the touch movement was more vertical than horizontal and if it exceeds the threshold
        if abs(dy) > abs(dx) and abs(dy) > min_swipe_distance:
            if dy > 0:  # Swipe was upwards
                rotated_piece = self.rotate(self.current_piece)  # Get the rotated version of the current piece
                # Check if the rotated piece can be placed in the current position
                if self.valid_space(rotated_piece, (self.current_x, self.current_y)):
                    self.current_piece = rotated_piece  # Update current piece only if the rotated position is valid
            else:  # Swipe was downwards
                # Move the block all the way down
                while self.valid_space(self.current_piece, (self.current_x, self.current_y + 1)):
                    self.current_y += 1
                self.place_piece()  # Place the piece at its final position
                # Prepare a new piece
                self.current_piece = random.choice(self.shapes)
                self.current_x, self.current_y = 3, 0
                if not self.valid_space(self.current_piece, (self.current_x, self.current_y)):
                    self.game_over = True  # End the game if the new piece cannot be placed
        else:
            # Handle left/right movement only if the swipe wasn't vertical and exceeds the threshold
            if abs(dx) > min_swipe_distance:
                if touch.ud['touch_start'][0] < Window.width / 2:
                    self.current_x -= 1
                else:
                    self.current_x += 1

                # Revert the move if the new position is not valid
                if not self.valid_space(self.current_piece, (self.current_x, self.current_y)):
                    if touch.ud['touch_start'][0] < Window.width / 2:
                        self.current_x += 1
                    else:
                        self.current_x -= 1

    colors = [
        (0, 0, 0), (255, 0, 0), (0, 255, 0), (0, 0, 255),
        (255, 255, 0), (255, 165, 0), (0, 255, 255), (128, 0, 128)
    ]
    
    shapes = [
        [[1, 1, 1], [0, 1, 0]],
        [[0, 2, 2], [2, 2, 0]],
        [[3, 3, 0], [0, 3, 3]],
        [[4, 0, 0], [4, 4, 4]],
        [[0, 0, 5], [5, 5, 5]],
        [[6, 6], [6, 6]],
        [[7, 7, 7, 7]]
    ]
        

class IsometricApp(App):
    def build(self):
        # Example board initialization
        board = [[0 for _ in range(10)] for _ in range(20)]
        return IsometricGrid(board=board)

if __name__ == '__main__':
    IsometricApp().run()