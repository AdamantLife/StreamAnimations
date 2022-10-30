from argparse import ArgumentError
from StreamAnimations.sprite import Sprite
from StreamAnimations.engine import Event

class CanvasBase():
    def __init__(self, size: tuple, steplength:int) -> None:
        ## Size of Canvas
        self.size = size
        ## Distance between animations
        self.steplength = steplength
        ## Sprites on Canvas
        self.sprites = []
        self.events = dict(movement = [])

    def add_listener(self, event:str, callback):
        listeners = self.events.get(event, [])
        listeners.append(callback)
        self.events[event] = listeners

    def remove_listener(self, event:str, callback):
        self.events.get(event, []).remove(callback)

    def trigger_event(self, eventname: str, eventobject: Event):
        """ Helper generator function to make triggering events uniform (and aid in debugging) """
        for callback in self.events[eventname]:
            yield callback(eventobject)

    def add_sprite(self, sprite: Sprite, location: any = None, zindex: int = 0)-> None:
        if not isinstance(sprite, Sprite):
            raise TypeError("Can only add Sprites to the canvas")
        self.sprites.append(sprite)
        sprite.location = location
        sprite.zindex = zindex

    def move_sprite(self, sprite: Sprite, direction: str = None, offset: tuple = None)-> None:
        """ Animates the given sprite and updates its location based on the provided movement """
        if direction is None and offset is None:
            raise ArgumentError("Direction or offset is needed")
        if direction and offset:
            d = sprite.cs.determine_direction(offset= offset)
            if d != direction:
                raise ArgumentError("Direction and Offset were and do not match")
        if isinstance(direction, tuple):
            offset = direction
            direction = None
        if direction and not offset:
            offset = sprite.cs.determine_offset(direction)
        elif offset and not direction:
            direction = sprite.cs.determine_direction(offset= offset)
        deltas = [off*self.steplength for off in offset]
        self._handle_move(sprite, direction, deltas)

    def _handle_move(self, sprite: Sprite, direction: str, deltas: tuple) -> None:
        dx, dy, *dz = deltas
        dz = dz[0] if dz else None
        x,y, *z = sprite.location
        z = z[0] if z else sprite.zindex
        event = Event(canvas = self, sprite = sprite, x = x, y = y , z = z, dx = dx, dy = dy, dz = dz)
        for response in self.trigger_event("movement", event):
            if response is False:
                return
        self._execute_move(sprite, direction, deltas)

    def _execute_move(self, sprite: Sprite, direction: str, deltas: tuple) -> None:
        sprite.move(direction)
        sprite.location = [loc+delta for (loc, delta) in zip(sprite.location, deltas)]

    def cycle_animation(self, sprite: Sprite):
        """ Increments the animation frame for the given Sprite.
        
            This is useful for edge cases: most sprites should just rely on idleanimations
        """
        sprite.animations.cycle()

    def animate_idlesprites(self, idlesprites):
        for sprite in idlesprites:
            sprite.cycle_idle()

class SinglePageMixin:
    def attach_singlepage(self):
        self.add_listener("movement", self.check_bounds)
    def detach_singlepage(self):
        self.remove_listener("movement", self.check_bounds)

    def check_bounds(self, event: Event):
        targetx= event.x+event.dx
        targety = event.y+event.dy
        if 0 > (targetx:= event.x+event.dx) or targetx > self.size[0]-1\
            or 0> (targety := event.y+event.dy) or targety > self.size[1]-1:
            return False

class SinglePageCanvas(CanvasBase, SinglePageMixin):
    def __init__(self, *args, **kw) -> None:
        super().__init__(*args, **kw)
        self.attach_singlepage()