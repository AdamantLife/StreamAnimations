from StreamAnimations.canvases import CanvasBase
from StreamAnimations import sprite, utils
from PIL import Image

class Frame():
    def __init__(self, renderer: "GifRenderer", record_hitboxes:bool = False):
        self.renderer = renderer
        self.activesprites = []
        self.resolution = []
        self.record_hitboxes = record_hitboxes

    def move_sprite(self, sprite: sprite.Sprite, *args, **kw):
        self.renderer.canvas.move_sprite(sprite, *args, **kw)
        self.activesprites.append(sprite)
    
    def animate_idlesprites(self):
        self.renderer.canvas.animate_idlesprites([sprite for sprite in self.renderer.canvas.sprites if sprite not in self.activesprites])

    def record_frame(self):
        ## DEVNOTE- We save resolution as a tuple for each sprite because otherwise
        ## we'd need to copy the Sprite to avoid it being mutated by future frames
        self.resolution = [ (sprite.location, sprite.get_image(with_hitboxes = self.record_hitboxes), sprite.zindex) for sprite in self.renderer.canvas.sprites ]
    
    def __enter__(self):
        return self

    def __exit__(self, *exc):
        self.animate_idlesprites()
        self.record_frame()
        self.renderer.add_frame(self)

class GifRenderer():
    def default_sorter(*resolution):
        result = sorted(enumerate(resolution), key = lambda res: res[1][1], reverse=True)
        return [enum for enum, res in result]

    def __init__(self, canvas: CanvasBase, background: Image.Image = None, *, sorter = default_sorter):
        self.canvas = canvas
        self.frames = []
        if background and not isinstance(background, Image.Image):
            raise TypeError("background should an PIL.Image.Image object")
        if background and background.size != self.canvas.size:
            raise AttributeError("background size does not fit canvas size")
        self.background = background

        self.sorter = sorter

    def get_background(self):
        if not self.background: return Image.new("RGBA", self.canvas.size, color = (255, 255, 255, 255))
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

        spritelocations = [(location, zindex) for (location, image, zindex) in frame.resolution]

        ## Sorters should return sprite indices based on how close they are to
        ## the camera, but we draw them furthest away first (hence reveresed)
        for spriteindex in reversed(self.sorter(*spritelocations)):
            sprite = frame.resolution[spriteindex]
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
        self.render(frame = self.frames[0], scale = scale, background= background)\
            .save(output, save_all = True, append_images = [self.render(frame=frame, scale=scale) for frame in self.frames[1:]], duration = duration)

    def frame(self, *args, **kw)-> Frame:
        return Frame(self, *args, **kw)