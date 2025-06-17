#UI.py

from kivy.uix.widget import Widget
from kivy.graphics import Color, Rectangle
from kivy.core.image import Image as CoreImage
from kivy.core.text import Label as CoreLabel
from kivy.properties import NumericProperty

class CustomWidget(Widget):
    score = NumericProperty(0)  # Initialize score as a NumericProperty
    def __init__(self):
        super(CustomWidget, self).__init__()
        with self.canvas:
            # Set the color to white for the rectangles
            Color(1, 1, 1, 1)

            # Initialize rectangles with dummy positions and sizes
            self.rect1 = Rectangle(size=(216, 145))
            self.rect2 = Rectangle(size=(216, 145))
            self.rect3 = Rectangle(size=(129, 163))

    def update_rect_positions(self):
        if self.parent:
            # Calculate total width of all rectangles
            total_rects_width = self.rect1.size[0] + self.rect2.size[0] + self.rect3.size[0]
            # Calculate remaining space after placing all rectangles
            remaining_space = self.parent.width - total_rects_width
            # Calculate spacing between rectangles
            spacing = remaining_space / 4

            
            # Set positions with equal spacing and offset from the top by 20 units
            top_offset = 40  # Offset from the top
            self.rect1.pos = (spacing, self.parent.height - self.rect1.size[1] - top_offset)
            self.rect2.pos = (self.rect1.pos[0] + self.rect1.size[0] + spacing, self.parent.height - self.rect2.size[1] - top_offset)
            self.rect3.pos = (self.rect2.pos[0] + self.rect2.size[0] + spacing, self.parent.height - self.rect3.size[1] - top_offset)

            #Calculate centre of window 2 to be returned
            # Calculate the center position for the label within rect2
            rect2_center_x = self.rect2.pos[0] + self.rect2.size[0] / 4
            rect2_center_y = self.rect2.pos[1] + self.rect2.size[1] / 6

            return (rect2_center_x,rect2_center_y)
        
            
    def update_labels(self, score, highscore, level):
        self.score = score
        self.highscore = highscore
        self.level = level
        with self.canvas.after:
            # Clear only the score-related drawing instructions
            self.canvas.after.clear()
            Color(1, 1, 1, 1)  # Set color for the text

            # Create the label with the score text and specify the custom font
            score_label = CoreLabel(text=f'{self.score}', font_size=20, font_name='Assets/Fonts/PressStart2P-Regular.ttf')
            highscore_label = CoreLabel(text=f'{self.highscore}', font_size=20, font_name='Assets/Fonts/PressStart2P-Regular.ttf')
            level_label = CoreLabel(text=f'{self.level}', font_size=20, font_name='Assets/Fonts/PressStart2P-Regular.ttf')
            score_label.refresh()  # Refresh to ensure the texture is updated with the text
            highscore_label.refresh()  # Refresh to ensure the texture is updated with the text
            level_label.refresh()  # Refresh to ensure the texture is updated with the text
            highscore_label.refresh()  # Refresh to ensure the texture is updated with the text
            score_texture = score_label.texture
            highscore_texture = highscore_label.texture
            level_texture = level_label.texture

            # Calculate the center position for the label within rect1
            rect1_center_x = self.rect1.pos[0] + self.rect1.size[0] / 2
            rect1_center_y = self.rect1.pos[1] + self.rect1.size[1] / 2

            # Calculate the center position for the label within rect3
            rect3_center_x = self.rect3.pos[0] + self.rect3.size[0] / 2
            rect3_center_y = self.rect3.pos[1] + self.rect3.size[1] / 2

            # Adjust the score label's position so that it's centered
            score_label_pos_x = rect1_center_x - score_texture.size[0] / 2
            score_label_pos_y = rect1_center_y - score_texture.size[1] / 4  # Adjusted as per your change

            #Adjust position of highscore label
            highscore_label_pos_x = rect1_center_x - highscore_texture.size[0] / 2
            highscore_label_pos_y = rect1_center_y - highscore_texture.size[1] * 2.75  # Adjusted as per your change

            # Adjust the score label's position so that it's centered
            level_label_pos_x = rect3_center_x - level_texture.size[0] / 2
            level_label_pos_y = rect3_center_y - level_texture.size[1] / 2  # Adjusted as per your change


            # Draw the labels's textures as rectangles at their calculated positions
            Rectangle(texture=score_texture, pos=(score_label_pos_x, score_label_pos_y), size=score_texture.size)
            Rectangle(texture=highscore_texture, pos=(highscore_label_pos_x, highscore_label_pos_y), size=highscore_texture.size)
            Rectangle(texture=level_texture, pos=(level_label_pos_x, level_label_pos_y), size=level_texture.size)



    def on_parent(self, widget, parent):
        self.update_rect_positions()
        # Load textures from the sprite sheet
        sprite_sheet_path = 'Assets/Sprites/sprite_sheet_UI.png'  # Make sure this path is correct
        score_highscore_texture = self.getImageFromSheet(2205, 980-242, 367, 241, sprite_sheet_path)
        next_piece_texture = self.getImageFromSheet(1660, 980-242, 367, 241, sprite_sheet_path)
        level_window_texture = self.getImageFromSheet(1101, 980-235, 192, 237, sprite_sheet_path)

        with self.canvas:
            # Clear any previous instructions
            self.canvas.clear()
            Color(1, 1, 1, 1)
            # Re-create rectangles with the new textures and updated positions
            self.rect1 = Rectangle(texture=score_highscore_texture, pos=self.rect1.pos, size=(216, 145))
            self.rect2 = Rectangle(texture=next_piece_texture, pos=self.rect2.pos, size=(216, 145))
            self.rect3 = Rectangle(texture=level_window_texture, pos=self.rect3.pos, size=(129, 163))
            
    def on_size(self, *args):
        self.update_rect_positions()

    def getImageFromSheet(self, x, y, width, height, sprite_sheet_path):
        core_image = CoreImage(sprite_sheet_path).texture
        texture_region = core_image.get_region(x, y, width, height)
        return texture_region
