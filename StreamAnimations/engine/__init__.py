## This Module
from StreamAnimations.sprite import Sprite
## Builtin
from dataclasses import dataclass, field


@dataclass
class Event:
    canvas: "CanvasBase"
    sprite: Sprite
    x: int
    y: int
    z: int
    dx: int
    dy: int
    dz: int
    extra:dict = field(default_factory= dict)


class SpriteAction():
    def __init__(self, callback: "function"):
        """ Initializes a new SpriteAction which acts a factory to create action callbacks for
                sprite/canvas combinations.

            Callback- Takes a function decorator which should accept a sprite and canvas and
                return a function which executes the action for the given sprite and canvas.
        """
        self.callback = callback

    def __call__(self,sprite: Sprite, canvas: "CanvasBase"):
        return self.callback(sprite, canvas)


