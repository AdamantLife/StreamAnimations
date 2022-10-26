from StreamAnimations.canvases import CanvasBase, SinglePageCanvas
from StreamAnimations import sprite, utils
from StreamAnimations.engine import utils as engineutils
from PIL import Image

class Frame():
    def __init__(self, canvas: CanvasBase, record_hitboxes:bool = False):
        self.canvas = canvas
        self.activesprites = []
        self.resolution = []
        self.record_hitboxes = record_hitboxes

    def move_sprite(self, sprite: sprite.Sprite, *args, **kw):
        self.canvas.move_sprite(sprite, *args, **kw)
        self.activesprites.append(sprite)
    
    def animate_idlesprites(self):
        self.canvas.animate_idlesprites([sprite for sprite in self.canvas.sprites if sprite not in self.activesprites])

    def record_frame(self):
        self.resolution = [ (sprite.location, sprite.get_image(with_hitboxes = self.record_hitboxes), sprite.zindex) for sprite in self.canvas.sprites ]
    
    def __enter__(self):
        return self

    def __exit__(self, *exc):
        self.animate_idlesprites()
        self.record_frame()
        self.canvas.add_frame(self)

class Canvas(CanvasBase):
    def __init__(self, size, steplength, background: Image.Image = None, *args, **kw):
        super().__init__(size, steplength, *args, **kw)
        self.frames = []
        if background and not isinstance(background, Image.Image):
            raise TypeError("background should an PIL.Image.Image object")
        if background and background.size != self.size:
            raise AttributeError("background size does not fit canvas size")
        self.background = background

    def get_background(self):
        if not self.background: return Image.new("RGBA", self.size, color = (255, 255, 255, 255))
        return self.background

    def add_frame(self, frame: Frame):
        """ Add the given Frame Instance to the frames list"""
        self.frames.append(frame)

    def render(self, frame: Frame, scale:int = 1, background: Image.Image = None):
        """ Composite an image of all sprites visible on the canvas """
        if background is None:
            bg = self.get_background()
            bg = utils.scale_image(bg, scale)
        else:
            bg = background.copy()

        for sprite in sorted(frame.resolution, key = lambda sprite: sprite[2]):
            [location, image, zindex] = sprite
            if location == None: continue
            sp = utils.scale_image(image, scale)
            bg.paste(sp, (location[0]*scale, location[1]*scale), sp)
        return bg
                    
    def save(self, output: str, framerate: int, scale: int = 1)-> None:
        """ Output Canvas to gif file """
        if not self.frames:
            raise AttributeError("No frames created: Gif would be empty")
        duration = 1000//framerate
        background = utils.scale_image(self.get_background(), scale)
        self.render(self.frames[0], scale = scale, background= background)\
            .save(output, save_all = True, append_images = [self.render(frame, scale) for frame in self.frames[1:]], duration = duration)

    def frame(self, *args, **kw)-> Frame:
        return Frame(self, *args, **kw)

class SinglePageCanvas(Canvas, SinglePageCanvas):
    def __init__(self, size, steplength, background: Image.Image = None, *args, **kw):
        super().__init__(size, steplength, background, *args, **kw)
        self.attach_singlepage()