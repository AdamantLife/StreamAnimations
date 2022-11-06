from StreamAnimations import coordinates
from StreamAnimations import sprite

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

class Sprite(sprite.Sprite):
    _COORDINATESYSTEM = TwoDimensional_4Way

class StationarySprite(sprite.StationarySprite):
    _COORDINATESYSTEM = TwoDimensional_4Way
    
class CosmeticSprite(sprite.CosmeticSprite):
    _COORDINATESYSTEM = TwoDimensional_4Way

class MobileSprite(sprite.MobileSprite):
    _COORDINATESYSTEM = TwoDimensional_4Way
    def up(self):
        self.move("up")
    def down(self):
        self.move("down")
    def left(self):
        self.move("left")
    def right(self):
        self.move("right")

class CounterHUD(sprite.CounterHUD):
    _COORDINATESYSTEM = TwoDimensional_4Way
class BarHUD(sprite.BarHUD):
    _COORDINATESYSTEM = TwoDimensional_4Way


def twod_sprite_sorter(*positions: tuple) -> list:
    """ Takes a list of (sprite.location, sprite.z-index) values and returns
        the enumerated indexes for all displayed sprites sorted by how close
        they are to the camera.
    """
    positions = [(enum, pos) for enum,pos in enumerate(positions) if pos[1] > -1]
    output =  sorted(positions, key = lambda pos: (pos[1][1], pos[1][0][1]), reverse=True) ## Sort by z-index first, then by y axis, then reverse
    return [enum for enum, pos in output]