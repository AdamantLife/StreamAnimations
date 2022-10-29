from StreamAnimations import coordinates
from StreamAnimations.sprite import MobileSprite

class TwoDimensional_4Way(coordinates.CoordinateSystem):
    _AXES = ["x","y"]
    _ALIASES = {
        "up":   "y",
        "right":"X",
        "down": "Y",
        "left": "x",
        "north":"y",
        "east": "X",
        "south":"Y",
        "west": "x"
    }

@coordinates.mixeddirection
class TwoDimensional_8Way(TwoDimensional_4Way): pass


class Sprite2D(MobileSprite):
    _COORDINATESYSTEM = TwoDimensional_4Way

    def up(self):
        self.move("up")
    def down(self):
        self.move("down")
    def left(self):
        self.move("left")
    def right(self):
        self.move("right")