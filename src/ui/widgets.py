"""
Custom UI widgets for the game.
"""

from kivy.uix.widget import Widget
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.image import Image
from kivy.graphics import Color, Rectangle
from kivy.core.text import Label as CoreLabel
from kivy.properties import NumericProperty
from kivy.animation import Animation
from kivy.core.image import Image as CoreImage

from ..utils.constants import FONT_PATH

class ScoreDisplay(Widget):
    """Widget to display score, high score, and level."""
    
    score = NumericProperty(0)
    
    def __init__(self):
        super().__init__()
        with self.canvas:
            Color(1, 1, 1, 1)
            self.rect1 = Rectangle(size=(216, 145))  # Score/Highscore
            self.rect2 = Rectangle(size=(216, 145))  # Next piece
            self.rect3 = Rectangle(size=(129, 163))  # Level

    def update_rect_positions(self):
        """Update the positions of the display rectangles."""
        if not self.parent:
            return None

        # Calculate layout
        total_width = sum(rect.size[0] for rect in [self.rect1, self.rect2, self.rect3])
        remaining_space = self.parent.width - total_width
        spacing = remaining_space / 4
        top_offset = 40

        # Position rectangles
        self.rect1.pos = (spacing, self.parent.height - self.rect1.size[1] - top_offset)
        self.rect2.pos = (
            self.rect1.pos[0] + self.rect1.size[0] + spacing,
            self.parent.height - self.rect2.size[1] - top_offset
        )
        self.rect3.pos = (
            self.rect2.pos[0] + self.rect2.size[0] + spacing,
            self.parent.height - self.rect3.size[1] - top_offset
        )

        # Calculate center of next piece window
        rect2_center_x = self.rect2.pos[0] + self.rect2.size[0] / 4
        rect2_center_y = self.rect2.pos[1] + self.rect2.size[1] / 6
        return (rect2_center_x, rect2_center_y)

    def update_labels(self, score: int, highscore: int, level: int):
        """Update the displayed scores and level."""
        self.score = score
        self.highscore = highscore
        self.level = level

        with self.canvas.after:
            self.canvas.after.clear()
            Color(1, 1, 1, 1)

            # Create labels
            labels = {
                'score': CoreLabel(text=f'{score}', font_size=20, font_name=FONT_PATH),
                'highscore': CoreLabel(text=f'{highscore}', font_size=20, font_name=FONT_PATH),
                'level': CoreLabel(text=f'{level}', font_size=20, font_name=FONT_PATH)
            }

            # Refresh all labels
            for label in labels.values():
                label.refresh()

            # Position and draw score
            score_pos_x = self.rect1.pos[0] + self.rect1.size[0]/2 - labels['score'].texture.size[0]/2
            score_pos_y = self.rect1.pos[1] + self.rect1.size[1]/2 - labels['score'].texture.size[1]/4
            Rectangle(
                texture=labels['score'].texture,
                pos=(score_pos_x, score_pos_y),
                size=labels['score'].texture.size
            )

            # Position and draw highscore
            highscore_pos_x = self.rect1.pos[0] + self.rect1.size[0]/2 - labels['highscore'].texture.size[0]/2
            highscore_pos_y = self.rect1.pos[1] + self.rect1.size[1]/2 - labels['highscore'].texture.size[1]*2.75
            Rectangle(
                texture=labels['highscore'].texture,
                pos=(highscore_pos_x, highscore_pos_y),
                size=labels['highscore'].texture.size
            )

            # Position and draw level
            level_pos_x = self.rect3.pos[0] + self.rect3.size[0]/2 - labels['level'].texture.size[0]/2
            level_pos_y = self.rect3.pos[1] + self.rect3.size[1]/2 - labels['level'].texture.size[1]/2
            Rectangle(
                texture=labels['level'].texture,
                pos=(level_pos_x, level_pos_y),
                size=labels['level'].texture.size
            )

class AnimatedButton(ButtonBehavior, Image):
    """Button with press/release animation."""
    
    scale = NumericProperty(1)
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bind(size=self._on_size)
        self.bind(scale=self._update_scale)
        self.bind(on_press=self.animate_down, on_release=self.animate_up)

    def _on_size(self, instance, value):
        """Save the base size when widget is sized."""
        self._base_size = value

    def _update_scale(self, instance, value):
        """Update size based on scale factor."""
        if hasattr(self, '_base_size'):
            self.size = (self._base_size[0] * value, self._base_size[1] * value)

    def animate_down(self, *args):
        """Animate button press."""
        Animation(scale=0.9, duration=0.1).start(self)

    def animate_up(self, *args):
        """Animate button release."""
        Animation(scale=1, duration=0.1).start(self)

class NextPieceDisplay(Widget):
    """Widget to display the next piece."""
    
    def __init__(self, block_size: int = 30):
        super().__init__()
        self.block_size = block_size

    def draw_piece(self, piece, position, color=(117/255.0, 147/255.0, 163/255.0)):
        """Draw the next piece preview."""
        self.canvas.clear()
        with self.canvas:
            for y, row in enumerate(piece):
                for x, cell in enumerate(row):
                    if cell:
                        Color(*color, 1)
                        pos_x = x * self.block_size + position[0]
                        pos_y = (len(piece) - y - 1) * self.block_size + position[1]
                        Rectangle(
                            pos=(pos_x, pos_y),
                            size=(self.block_size, self.block_size)
                        ) 