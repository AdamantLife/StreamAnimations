from multiprocessing.sharedctypes import Value
from StreamAnimations.sprite.hitbox import Hitbox, create_rect_hitbox_image
from StreamAnimations import utils
from  PIL import Image

class Animations():
    def __init__(self, **kw):
        self.animations = dict()
        for animation, frames in kw.items():
            self.animations[animation] = AnimationLoop(frames)
        self.current_animation = list(kw.keys())[0] if kw else -1
        self._paused = False
    
    def pause(self):
        self._paused = True
    def unpause(self):
        self._paused = False

    def set_animation(self, animation: str):
        ## TODO: handle resetting animations
        self.current_animation = animation

    def cycle(self, animation:str = None, count:int = 1)-> tuple:
        """ Cycles the current_index by count (default 1) for the given animation and returns the new index and frame.
            If animation is not provided, current_animation will be used instead

            Cycle wraps in both directions so the index is never greater than len(frames) or
            less than 0.
            If Animation is paused, returns immediately
        """
        if self._paused: return
        animation = self.animations[animation] if animation else self.current_loop()
        animation.cycle(count)

    def current_loop(self):
        return self.animations.get(self.current_animation) or self.animations[list(self.animations)[0]]

    def current_frame(self):
        return self.current_loop().current_frame()

    def is_last_frame(self):
        return self.current_loop().is_last_frame()

class AnimationLoop():
    ## TODO: implement resetting animations
    def __init__(self, frames: list) -> None:
        ## Makes it easier for non-animated sprites
        if isinstance(frames,Image.Image): frames = [frames,] 
        self.frames = list(frames)
        self.current_index = 0

    def cycle(self, count:int = 1)-> tuple:
        """ Cycles the current_index by count (default 1) and returns the new index and frame.

            Cycle wraps in both directions so the index is never greater than len(frames) or
            less than 0.
        """
        ## Increment and wrap around to the first frame
        self.current_index = (self.current_index + count) % len(self.frames)
        return self.current_index, self.frames[self.current_index]

    def current_frame(self):
        return self.frames[self.current_index]

    def is_last_frame(self):
        return self.current_index == len(self.frames) - 1
    

class startlocation():
    """ A class for memorizing the initial location of a sprite and acting as a context manager to automatically return the sprite to its location. """
    NULL = object()
    def __init__(self, sprite, newlocation = NULL):
        """ Initializes a new startlocation class.
        
            newlocation defaults to startlocation.NULL because None is a valid location to set on a sprite
        """
        self.sprite = sprite
        self._initial_location = sprite.location
        if newlocation is not startlocation.NULL:
            sprite.location = newlocation

    def revert(self):
        """ Returns the sprite to its initial location """
        self.sprite.location = self._initial_location

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        self.sprite.location = self._initial_location



class Sprite():
    """ Base class for Sprite Objects """
    def __init__(self, animations = None, hitboxes = None):
        """
        hitboxes - a list of Hitbox Objects
        """
        self._location = None

        if not animations: animations = dict()
        self.animations = Animations(**animations)
        
        if not hitboxes:
            hitboxes = list()
        elif isinstance(hitboxes, tuple) and len(hitboxes) == 2:
            hitboxes = [Hitbox(create_rect_hitbox_image(*hitboxes)),]
        else:
            hitboxes = list(hitboxes)
        self.hitboxes = hitboxes
        for hitbox in self.hitboxes: hitbox.sprite = self
        
        self.zindex = 0

    @property
    def is_idle(self):
        return self.animations.current_animation == "idle"

    @property
    def location(self):
        return self._location
    @location.setter
    def location(self, value: tuple):
        if value is None:
            self._location = value
        else:
            self._location = tuple(value)

    def cycle_idle(self):
        self.animations.set_animation("idle")
        self.animations.cycle()

    def move(self,*args, **kw):
        raise NotImplementedError("Subclass has not implemented move")

    def get_image(self, with_hitboxes:bool = False):
        raise NotImplementedError("Subclass has not implemented get_image")

    @property
    def bbox(self):
        raise NotImplementedError("Subclass has not implemented bbox")

    def add_hitbox(self, hitbox: Hitbox):
        self.hitboxes.append(hitbox)
        hitbox.sprite = self

    def at(self, location: tuple)-> startlocation:
        """ Returns a startlocation instance which is intended to be used as a Context Manager so that
            the sprite is returned to its current (pre-at()) location when the context is exited

            Example Usage:

            mysprite.location = (0,0)
            with mysprite.at( (10, 10) ):
                dosomethingat10_10()

            assert mysprite.location == (0,0)
        """
        return startlocation(self, newlocation= location)

    def paste_hitboxes(self, img):
        for box in self.hitboxes:
            bx = box.image
            color = bx.convert("RGBA")
            pixels= color.load()
            for x in range(color.width):
                for y in range(color.height):
                    if pixels[x,y] == (255, 255, 255, 255):
                        pixels[x,y] = (255, 0, 0, 255)
                    # elif pixels[x,y] == (0, 0, 0, 255):
                    #     pixels[x,y] = (0, 0 , 0, 0)
            ## bbox is global: need to convert back to local
            img.paste(color, utils.offset_boundingbox(box.bbox, -self.location[0], -self.location[1]), bx)
        return img

class StationarySprite(Sprite):
    """ A Class for Sprites that animate without moving and do not rely on idle animations.
        Typically this sprite's animations are triggered by an outside force.
        
    """ 
    def __init__(self, *args, **kw):
        super().__init__(*args, **kw)

    def move(self, direction_or_offset =None):
        ## We accept direction_or_offset in order to be compatible with other sprites
        self.animations.current_index = 0
        self.animations.cycle()

    def get_image(self, with_hitboxes: bool = False):
        img = self.animations.current_frame()
        if with_hitboxes: return self.paste_hitboxes(img)
        return img

    @property
    def bbox(self):
        img = self.get_image()
        return [self.location[0], self.location[1], self.location[0]+img.width, self.location[1]+img.height]

class CosmeticSprite(Sprite):
    def __init__(self, parent = None, offset = None, zindex = 1, **kw):
        super().__init__(**kw)
        self.parent = parent
        self.offset = offset
        self._zindex = zindex

    def get_image(self, with_hitboxes:bool = False):
        img = self.animations.current_frame()
        if with_hitboxes: return self.paste_hitboxes(img)
        return img

    @property
    def location(self):
        x,y = self.parent.location
        return x+self.offset[0], y+self.offset[1]

    @location.setter
    def location(self, value):
        return

    @property
    def zindex(self):
        return self._zindex
    @zindex.setter
    def zindex(self,value):
        return

    @property
    def bbox(self):
        img = self.get_image()
        return [self.location[0], self.location[1], self.location[0]+img.width, self.location[1]+img.height]


class MobileSprite(Sprite):
    """ Creates a Sprite which moves around a Coordinate System"""

    _COORDINATESYSTEM = None

    def __init__(self, directionalsprites: dict = None, coordinatesystem = None, *args, **kw) -> None:
        """ """
        if coordinatesystem: self._COORDINATESYSTEM = coordinatesystem

        animations = kw.pop("animations", {})
        ## Make sure animations is prepopulated with all directions
        for direction in self._COORDINATESYSTEM.directions():
            if not animations.get(direction): animations[direction] = []

        ## Validate and normalize directions before adding them to animations
        if directionalsprites:
            for [direction,sprites] in directionalsprites.items():
                ndir = self._COORDINATESYSTEM.normalize_direction(direction)
                animations[ndir] = sprites

        super().__init__(*args, animations= animations, **kw)
        
                        

    @property
    def cs(self):
        return self._COORDINATESYSTEM

    def valid_moves(self, engine: "engine.Engine", atlocation: "coordinates.Coordinate" = None):
        """ Checks which directions the sprite can move in """
        for direction in self.cs.directions():
            with self.at(atlocation) as start:
                engine.move_sprite(self, direction)
                if self.location != atlocation:
                    yield direction

    def move(self, direction):
        """ Increment the sprite's frame in the given direction """
        direction = self.cs.normalize_direction(direction)

        ## We are now using self.animations to "track" our direction
        if direction != self.animations.current_animation:
            self.animations.set_animation(direction)

        else:
            self.animations.cycle()

    def get_image(self, with_hitboxes: bool = False):
        img = self.animations.current_frame()
        if with_hitboxes: return self.paste_hitboxes(img)
        return img

    @property
    def bbox(self):
        img = self.get_image()
        return [self.location[0], self.location[1], self.location[0]+img.width, self.location[1]+img.height]

class Pivotting2DSprite(MobileSprite): pass

