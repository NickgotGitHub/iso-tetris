"""
Visual effects for the game.
"""

import time
import math
from typing import List, Tuple
from kivy.graphics import Color, Rectangle
from kivy.core.image import Image as CoreImage
from ..utils.constants import (
    FROST_BASE_ALPHA,
    FROST_GLOW_AMPLITUDE,
    COLOR_TRANSITION_SPEED,
    WILDCARD_COLORS,
    FROST_TEXTURE_PATH
)

class Effect:
    """Base class for visual effects."""
    def __init__(self):
        self.active = False

    def update(self, dt: float) -> None:
        """Update the effect state."""
        raise NotImplementedError("Subclasses must implement update method.")

    def start(self) -> None:
        """Start the effect."""
        self.active = True

    def stop(self) -> None:
        """Stop the effect."""
        self.active = False

class FrostEffect(Effect):
    """Creates a frost overlay effect with pulsing opacity."""
    
    def __init__(self, canvas):
        super().__init__()
        self.canvas = canvas
        self.start_time = 0
        self.duration = 0
        self.frost_rect = None
        self.frost_texture = CoreImage(FROST_TEXTURE_PATH).texture

    def start(self, duration: float = 10.0) -> None:
        """
        Start the frost effect.
        
        Args:
            duration: How long the effect should last in seconds
        """
        super().start()
        self.start_time = time.time()
        self.duration = duration

        # Create the frost overlay if it doesn't exist
        if not self.frost_rect:
            with self.canvas.after:
                Color(1, 1, 1, 1)
                self.frost_rect = Rectangle(
                    texture=self.frost_texture,
                    pos=self.canvas.pos,
                    size=self.canvas.size
                )

    def update(self, dt: float) -> None:
        """
        Update the frost effect animation.
        
        Args:
            dt: Time delta since last update
        """
        if not self.active:
            return

        elapsed = time.time() - self.start_time

        if elapsed < self.duration:
            # Calculate pulsing glow effect
            glow = math.sin(elapsed * 2.0)
            current_alpha = FROST_BASE_ALPHA + FROST_GLOW_AMPLITUDE * glow
            current_alpha = max(0, min(1, current_alpha))

            # Update the frost overlay
            if self.frost_rect:
                self.canvas.after.remove(self.frost_rect)
                with self.canvas.after:
                    Color(1, 1, 1, current_alpha)
                    self.frost_rect = Rectangle(
                        texture=self.frost_texture,
                        pos=self.canvas.pos,
                        size=self.canvas.size
                    )
        else:
            self.stop()

    def stop(self) -> None:
        """Stop the frost effect and clean up."""
        super().stop()
        if self.frost_rect:
            self.canvas.after.remove(self.frost_rect)
            self.frost_rect = None

class ColorTransitionEffect(Effect):
    """Creates smooth color transitions for wild card blocks."""
    
    def __init__(self):
        super().__init__()
        self.current_color = list(WILDCARD_COLORS[0])
        self.color_index = 1
        self.target_color = WILDCARD_COLORS[self.color_index]

    def update(self, dt: float) -> None:
        """
        Update the color transition animation.
        
        Args:
            dt: Time delta since last update
        """
        if not self.active:
            return

        # Interpolate each color channel
        for i in range(3):
            self.current_color[i] += (
                self.target_color[i] - self.current_color[i]
            ) * COLOR_TRANSITION_SPEED * dt

        # Check if we've reached the target color
        if all(abs(self.current_color[i] - self.target_color[i]) < 0.01 for i in range(3)):
            # Snap to exact color
            self.current_color = list(self.target_color)
            # Move to next color
            self.color_index = (self.color_index + 1) % len(WILDCARD_COLORS)
            self.target_color = WILDCARD_COLORS[self.color_index]

    @property
    def current_rgb(self) -> Tuple[float, float, float]:
        """Get the current RGB color values."""
        return tuple(self.current_color) 