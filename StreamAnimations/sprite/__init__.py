from StreamAnimations.sprite.hitbox import Hitbox

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
        pass

    def __exit__(self, *exc):
        self.sprite.location = self._initial_location



class Sprite():
    """ Base class for Sprite Objects """
    def __init__(self, idleanimations = None, hitboxes = None):
        """
        hitboxes - a list of Hitbox Objects
        """
        self._location = None
        self.representation = None
        
        if idleanimations is None: idleanimations = []
        self.idleanimations = list(idleanimations)
        
        if not hitboxes:
            hitboxes = list()
        else:
            hitboxes = list(hitboxes)
        self.hitboxes = hitboxes
        
        self.idleindex = 0
        self.zindex = 0

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
        self.idleindex +=1
        if self.idleindex > len(self.idleanimations)-1: self.idleindex = 0

    def move(self,*args, **kw):
        raise NotImplementedError("Subclass has not implemented move")

    def get_image(self):
        raise NotImplementedError("Subclass has not implemented get_image")

    @property
    def bbox(self):
        raise NotImplementedError("Subclass has not implemented bbox")

    @classmethod
    def valid_direction(cls, direction):
        raise NotImplementedError("Subclass has not implemented valid_direction ")

    @classmethod
    def determine_direction(cls, offset: tuple)->str:
        """ Given an offset, determine the direction in which the offset lies """
        raise NotImplementedError("Subclass has not implemented determine_direction ")

    @classmethod
    def determine_offset(cls, direction: str)-> tuple:
        """ Converts a direction to an offset """
        raise NotImplementedError("Subclass has not implemented determine_offset ")

    def add_hitbox(self, hitbox: Hitbox):
        self.hitboxes.append(hitbox)
        hitbox.sprite = self

    def at(self, location):
        """ Returns a startlocation instance which is intended to be used as a Context Manager so that
            the sprite is returned to its current (pre-at()) location when the context is exited

            Example Usage:

            mysprite.location = (0,0)
            with mysprite.at( (10, 10) ):
                dosomethingat10_10()

            assert mysprite.location == (0,0)
        """
        return startlocation(self, newlocation= location)

class StationarySprite(Sprite):
    def __init__(self, representation: list = []):
        super().__init__()
        self.representation = list(representation)
        ## Current animation frame
        self.frame = 0

    def move(self, direction_or_offset =None):
        self.idleindex = 0
        self.frame+=1
        if self.frame > len(self.representation)-1: self.frame = 0

    def get_image(self):
        return self.representation[self.frame]

    @property
    def bbox(self):
        img = self.get_image()
        return [self.location[0], self.location[1], self.location[0]+img.width, self.location[1]+img.height]

    def valid_direction(self, direction):
        return True
    def determine_direction(self, offset):
        return None
    def determine_offset(self, direction): return None

class CosmeticSprite(Sprite):
    def __init__(self, idleanimations: list = [], parent = None, offset = None, zindex = 1):
        super().__init__(idleanimations)
        self.parent = parent
        self.offset = offset
        self._zindex = zindex

    def get_image(self):
        return self.idleanimations[self.idleindex]

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


class Sprite2D(Sprite):
    CARDINALS = ["up", "down", "left", "right"]
    CARDINALOFFSETS = {
        -1: "up",
        +1: "down",
        +1: "right",
        -1: "left",
        "up": (0,-1),
        "down": (0, +1),
        "right": (+1, 0),
        "left": (-1, 0)
    }
    """ Creates a Sprite for a 2 Dimensional Plane """
    def __init__(self, cardinalsprites: dict = None, *args, **kw) -> None:
        """ """
        super().__init__(*args, **kw)
        self.representation = dict()
        ## Current cardinal directionm the sprite is facing
        self.currentdirection = "down"
        ## Current animation frame
        self.frame = 0
        for cardinal in self.CARDINALS:
            if self.representation.get(cardinal) is None: self.representation[cardinal] = []
        
        if cardinalsprites:
            for cardinal in self.CARDINALS:
                if cardinal in cardinalsprites:
                    self.representation[cardinal] = list(cardinalsprites[cardinal])


    @classmethod
    def valid_direction(cls, direction):
        if direction not in cls.CARDINALS:
            raise ValueError(f"Not a valid direction: {direction}")

    @classmethod
    def determine_direction(cls, offset: tuple)->str:
        """ Given an offset, determine the direction in which the offset lies """
        if offset[0] == 0 and offset[1] == 0: return
        if abs(offset[0]) >= abs(offset[1]):
            if offset[0] > 0: return "right"
            return "left"
        if offset[1] > 0: return "down"
        return "up"

    @classmethod
    def determine_offset(cls, direction: str)-> tuple:
        """ Converts a direction to an offset """
        cls.valid_direction(direction)
        return cls.CARDINALOFFSETS[direction]

    def move(self, cardinal):
        """ Increment the sprite's frame in the given direction """
        self.valid_direction(cardinal)
        self.idleindex = 0

        if cardinal != self.currentdirection:
            self.frame = 0
            self.currentdirection = cardinal

        else:
            self.frame += 1
            if self.frame > len(self.representation.get(cardinal))-1: self.frame = 0
        
    def up(self):
        self.move("up")
    def down(self):
        self.move("down")
    def left(self):
        self.move("left")
    def right(self):
        self.move("right")

    def get_image(self):
        return self.representation[self.currentdirection][self.frame]

    @property
    def bbox(self):
        img = self.get_image()
        return [self.location[0], self.location[1], self.location[0]+img.width, self.location[1]+img.height]

class Pivotting2DSprite(Sprite2D): pass

