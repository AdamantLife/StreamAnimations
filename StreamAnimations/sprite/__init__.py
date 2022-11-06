### This Module
from StreamAnimations.sprite.hitbox import Hitbox, create_rect_hitbox_image
from StreamAnimations import utils

## Builtin
import math

## Third Part
from  PIL import Image, ImageFont, ImageDraw

class Animations():
    def __init__(self, **kw):
        

        self.animations = dict()
        for animation, frames in kw.items():
            looptype = AnimationLoop
            ## Not a single image and not none/falsey (which means that it should be a list)
            ## and the first index of that list is not an Image
            if not isinstance(frames, Image.Image) and frames and not isinstance(frames[0], Image.Image):
                ## First index should be a AnimationLoop-type object
                looptype = frames.pop(0)
            self.animations[animation] = looptype(frames)
            
        self.current_animation = list(kw.keys())[0] if kw else -1
        self._paused = False
    
    def pause(self):
        self._paused = True
    def unpause(self):
        self._paused = False
    @property
    def is_paused(self):
        return self._paused

    def set_animation(self, animation: str, reset = True)-> tuple:
        self.current_animation = animation
        ## If reset, set index to 0
        ## Otherwise, make index is no more than the last index of the new loop
        loop = self.current_loop()
        loop.current_index = 0 if reset else min(loop.current_index, len(loop)-1)
        return loop.current_index, loop.current_frame()

    def cycle(self, animation:str = None, count:int = 1)-> tuple:
        """ Cycles the current_index by count (default 1) for the given animation and returns the new index and frame.
            If animation is not provided, current_animation will be used instead

            Cycle wraps in both directions so the index is never greater than len(frames) or
            less than 0.
            If Animation is paused, returns immediately
        """
        if self._paused: return
        animation = self.animations[animation] if animation else self.current_loop()
        return animation.cycle(count)

    def current_loop(self)->"AnimationLoop":
        return self.animations.get(self.current_animation) or self.animations[list(self.animations)[0]]

    def current_frame(self)->Image.Image:
        return self.current_loop().current_frame()

    def is_last_frame(self)->bool:
        return self.current_loop().is_last_frame()

class AnimationLoop():
    ## TODO: implement resetting animations
    def __init__(self, frames: list) -> None:
        ## Makes it easier for non-animated sprites
        if isinstance(frames,Image.Image): frames = [frames,] 
        self.frames = list(frames)
        self.current_index = 0
        
    def __len__(self):
        return len(self.frames)

    def cycle(self, count:int = 1)-> tuple:
        """ Cycles the current_index by count (default 1) and returns the new index and frame.

            Cycle wraps in both directions so the index is never greater than len(frames) or
            less than 0.
        """
        ## Increment and wrap around to the first frame
        self.current_index = (self.current_index + count) % len(self.frames)
        return self.current_index, self.frames[self.current_index]

    def current_frame(self)->Image.Image:
        return self.frames[self.current_index]

    def is_last_frame(self)->bool:
        return self.current_index == len(self.frames) - 1

class HUDLabel():
    """ Draws a label on the canvas hud """
    def __init__(self, options):
        ## Options is passed in as a list bundle with HUDLabel as its animator
        options = options[0]
        self.parent = options.pop('parent')

        size = options.pop("size", 11)
        font = options.pop("font", "times")
        self.font = ImageFont.truetype(font = font, size = size)
        
        self.textoptions = options
        self.lastvalue = None
        self.cachedimage = None

    @property
    def current_index(self):
        return 0
    @current_index.setter
    def current_index(self, value):
        return

    def __len__(self): return 1
    def cycle(self, *args, **kw)-> tuple:
        return 1, self.current_frame()

    def current_frame(self)-> Image.Image:
        text = self.parent.get_text()
        if self.lastvalue and self.lastvalue == text and self.cachedimage:
            return self.cachedimage

        self.lastvalue = text
        textbboxargs = ["anchor","spacing","align","direction","features","language","strok_width","embedded_color"]
        
        size = self.font.getbbox(text, **{key:self.textoptions[key] for key in textbboxargs if key in self.textoptions})
        img = Image.new("RGBA", (size[2]-size[0], size[3]-size[1]+20), (0,0,0,0) )
        ctx = ImageDraw.Draw(img)
        ctx.text((0,0), text, font = self.font, **self.textoptions)

        self.cachedimage = img
        return img

    def is_last_frame(self)->bool:
        return True
    

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
    _COORDINATESYSTEM = None

    def __init__(self, animations = None, hitboxes = None, coordinatesystem = None, imagescaler = utils.scale_image):
        """
        hitboxes - a list of Hitbox Objects
        """
        if coordinatesystem: self._COORDINATESYSTEM = coordinatesystem
        self._location = None

        if not animations: animations = dict()
        ## Make sure animations is prepopulated with all directions
        for direction in self._COORDINATESYSTEM.directions():
            if not animations.get(direction): animations[direction] = []

        ## Convert aliases to formal directions
        for alias in list(animations):
            try:
                ndir = self._COORDINATESYSTEM.normalize_direction(alias)
                ## Not an alternative alias (name of axis itself)
                assert ndir != alias
            ## Not actually an alias, so ignore it
            except (ValueError, AssertionError): pass
            ## Add alias to the normalized direction's key
            else:
                aliassprites = animations.pop(alias)
                sprites = animations.get(ndir,[])
                sprites.extend(aliassprites)
                animations[ndir] = sprites

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

        self.imagescaler = imagescaler
        
        ## This sprite is in a theoretical state
        ## (useful for algorithms which plan actions)
        self.virtual = False

    @property
    def cs(self):
        return self._COORDINATESYSTEM

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

    def set_animation(self, animation, **kw):
        self.animations.set_animation(animation= animation, **kw)

    def cycle_idle(self):
        self.animations.set_animation("idle", reset = False)
        self.animations.cycle()

    def move(self,*args, **kw):
        raise NotImplementedError("Subclass has not implemented move")

    def get_image(self, with_hitboxes: bool = False, scale = None):
        img = self.animations.current_frame()
        if with_hitboxes: return self.paste_hitboxes(img)
        if self.imagescaler and scale: img = self.imagescaler(img, multiplier= scale)
        return img

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

class HUD(Sprite):
    def __init__(self, *args, animations=None, hitboxes=None, coordinatesystem=None, label: str = None, **kw) -> "self":
        super().__init__(*args, animations=animations, hitboxes=hitboxes, coordinatesystem=coordinatesystem, **kw)
        self.zindex = math.inf
        self.label = label

    def get_text(self):
        return self.label

class ValueHUD(HUD):
    def __init__(self, *args, cmin:int = None, cmax:int = None, start:int = 0, animations = None, fontoptions = None, imagescaler = None, **kw) -> "self":
        if fontoptions is None: fontoptions = {}
        animator = fontoptions.pop("animator", HUDLabel)
        fontoptions['parent'] = self
        animations = {"idle": [animator, fontoptions]}
        super().__init__(*args, animations=animations, imagescaler= imagescaler, **kw)

        self.min = cmin
        self.max = cmax
        self.value = start
        self.previousvalue = start
        self.cachedimage = None

    def get_image(self, with_hitboxes: bool = False, scale=None):
        if self.value == self.previousvalue and self.cachedimage:
            return self.cachedimage
        self.previousvalue = self.value
        img = super().get_image(with_hitboxes = with_hitboxes, scale= scale)
        self.cachedimage = img
        return img

class CounterHUD(ValueHUD):
    def __init__(self, *args, **kw):
        super().__init__(*args, **kw)

    def get_text(self):
        return super().get_text() + str(self.value)

class BarHUD(ValueHUD):
    def __init__(self, *args, cmin = 0, cmax = 100, include_value = False, labelposition: str = "left", border:bool = False, size  = (100,10), background = None, fill = None,
        **kw) -> "self":
        super().__init__(*args, cmin = cmin, cmax = cmax, **kw)
        self.include_value = include_value
        self.labelposition = labelposition
        self.border = border
        self.background = background
        self.fill = fill
        self._size = None
        self.size = size
        


    @property
    def size(self): return self._size
    @size.setter
    def size(self, value):
        if not value: return
        if len(value) > 2:
            raise ValueError(f"BarHUD size should be length 2, length recieved: {len(value)}")
        if not isinstance(value, tuple):
            try:
                value = tuple(value)
            except: pass
        if not isinstance(value, tuple):
            raise TypeError(f"BarHUD requires an iterable of length two, recieved: {value}")

        self._size = value
        self._build_images()

    def _build_images(self):
        if not self.size:
            raise AttributeError("BarHUD size not set")
        backgroundcolor = self.background if self.background else (0,0,0,0)
        img = Image.new("RGBA", self.size, backgroundcolor)
        self.img = img

        border = Image.new("RGBA", self.size, (0,0,0,0))
        if self.border:
            ctx = ImageDraw.Draw(border)
            if callable(self.border):
                self.border(ctx)
            else:
                ctx.rectangle([0,0,*self.size], outline=(0,0,0,255))
        self.borderimage = border

        fillcolor = self.fil if self.fill else (255, 0, 0, 255)
        fill = Image.new("RGBA", self.size, fillcolor)
        self.fillimage = fill

    def get_text(self):
        return super().get_text() + str(self.value if self.include_value else "")

    def get_image(self, with_hitboxes: bool = False, scale=None):
        textimg = super().get_image(with_hitboxes= with_hitboxes, scale = scale)

        size = list(self.size)
        if self.labelposition == "left":
            size[0]+=textimg.width+5
            size[1] = max(size[1], textimg.height)
        elif self.labelposition == "top":
            size[0] = max(size[0], textimg.width)
            size[1]+= textimg.height + 5
        elif self.labelposition == "inside":
            size[0] = max(size[0], textimg.width)
            size[1] = max(size[1], textimg.height)

        baseimage = Image.new("RGBA", size, (0,0,0,0))
        barmask = baseimage.copy()

        ## Layer Bar Background
        barposition = (0,0)
        if self.labelposition == "left":
            barposition = (textimg.width + 5, baseimage.height//2 - self.img.height//2)
        elif self.labelposition == "top":
            barposition = (0, textimg.height + 5)
        elif self.labelposition == "inside":
            barposition = (0, baseimage.height //2 - textimg.height//2)

        baseimage.paste(self.img, barposition, self.img)
        barmask.paste(self.img, barposition, self.img)

        ## Layer Fill
        fillposition = [0,0,self.size[0],self.size[1]]
        percfill = 1 - (self.value / self.max)
        fillposition[0] = int(percfill * self.size[0])
        fillimage = self.fillimage.copy()
        fillimage = fillimage.crop(fillposition)

        baseimage.paste(fillimage, barposition, fillimage)

        ## Layer Text
        labelposition = (0,0)
        if self.labelposition == "inside":
            labelposition = (5, baseimage.height //2 - textimg.height//2)
        baseimage.paste(textimg, labelposition, textimg)
        
        ## Layer border
        baseimage.paste(self.borderimage, barposition, self.borderimage)

        return baseimage


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
    """ Creates a Sprite which moves around a canvas"""

    def valid_moves(self, engine: "engine.Engine", atlocation: "coordinates.Coordinate" = None):
        """ Checks which directions the sprite can move in """
        if atlocation is None: atlocation = self.location
        self.virtual = True
        for direction in self.cs.directions():
            with self.at(atlocation) as start:
                engine.move_sprite(self, direction = direction)
                if self.location != atlocation:
                    yield direction
        self.virtual = False

    def move(self, direction):
        """ Increment the sprite's frame in the given direction """
        direction = self.cs.normalize_direction(direction)
        ## Don't animation  virtual movement
        if self.virtual: return

        ## We are now using self.animations to "track" our direction
        if direction != self.animations.current_animation:
            self.animations.set_animation(direction)

        else:
            self.animations.cycle()

    @property
    def bbox(self):
        img = self.get_image()
        return [self.location[0], self.location[1], self.location[0]+img.width, self.location[1]+img.height]

class Pivotting2DSprite(MobileSprite): pass

