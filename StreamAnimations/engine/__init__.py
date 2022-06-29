## This Module
from StreamAnimations.sprite import Sprite
## Builtin
from dataclasses import dataclass, field


@dataclass
class Event:
    canvas: "Canvas"
    sprite: Sprite
    x: int
    y: int
    z: int
    dx: int
    dy: int
    dz: int
    extra:dict = field(default_factory= dict)