#Next_piece.py

from kivy.uix.widget import Widget
from kivy.graphics import Color, Rectangle

class DrawNextPiece(Widget):
    def __init__(self, **kwargs):
        super(DrawNextPiece, self).__init__(**kwargs)
        self.block_size = 30

    def draw_piece(self, gotten_piece, gotten_pos, color=(117 / 255.0, 147 / 255.0, 163 / 255.0)):
        self.canvas.clear()
        with self.canvas:
            for y, row in enumerate(gotten_piece):
                for x, cell in enumerate(row):
                    if cell:
                        Color(*color, 1)
                        pos_x = x * self.block_size + gotten_pos[0]
                        pos_y = (len(gotten_piece) - y - 1) * self.block_size + gotten_pos[1]
                        Rectangle(pos=(pos_x, pos_y), size=(self.block_size, self.block_size))
