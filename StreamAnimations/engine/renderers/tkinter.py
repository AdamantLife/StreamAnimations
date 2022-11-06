## This module
from StreamAnimations import utils

## Builtin
import tkinter as tk

## 3rd Party
from PIL import ImageTk

class TkinterCanvas():

    def __init__(self, canvas: "canvases.CanvasBase", tkcanvas:tk.Canvas, framerate: int, scale: float = 1.0, background: "PIL.Image" = None):
        self.canvas = canvas
        self.tkcanvas = tkcanvas
        self.framerate = framerate
        self.callback = None
        self.scale = scale
        self.background = background
        if self.background:
            self.background = ImageTk.PhotoImage(self.background)
            self.tkcanvas.create_image(0, 0, anchor= "nw", image = self.background)
        """Collects information on sprites displayed, their canvas
            id, where they are on the canvas, and their current animation
            in order to determine blotting
        """
        self.sprites = dict()


    @property
    def fpsdelay(self):
        """ Converts framerate to milliseconds/frame """
        return 1000//self.framerate

    def begin_animationloop(self):
        """ Starts a new animation_loop """
        self.callback = True
        self.animation_loop()

    def animation_loop(self):
        """ Renders the canvas changes to the TK Canvas and creates a new interval callback """
        self.render(scale= self.scale, background = self.background)
        if self.callback:
            self.callback = self.tkcanvas.after(self.fpsdelay, self.animation_loop)

    def cancel_animationloop(self):
        """ Cancels the next queued animation loop """
        self.tkcanvas.after_cancel(self.callback)
        self.callback = None

    def add_sprite(self, sprite: "sprites.Sprite", scale:float = None):
        """ Adds a sprite to the canvas and creates an entry for it in self.sprites """
        if scale is None: scale = self.scale

        ## Create PhotoImage at scale of the sprite
        image = sprite.get_image(scale = scale)
        photo = ImageTk.PhotoImage(image)

        _id = self.tkcanvas.create_image(sprite.location[0]*scale, sprite.location[1]*scale, image = photo, anchor = "nw")

        self.sprites[sprite] = dict(id = _id, photo=photo, location = sprite.location, animation = sprite.animations.current_loop(), image = sprite.get_image(), zindex = sprite.zindex*100_000+sprite.location[1])

    def remove_sprite(self, sprite: "sprites.Sprite"):
        """ Removes a sprite from the canvas and from self.sprites """
        self.canvas.delete(self.sprites[sprite]['id'])
        del self.sprites[sprite]

    def set_sprite_animation(self, sprite: "sprites.Sprite", scale:float = None):
        """ Changes the image for the sprite currently displayed on the canvas """
        if scale is None: scale = self.scale
        ## Create PhotoImage at scale of the sprite
        image = sprite.get_image(scale = scale)
        photo = ImageTk.PhotoImage(image)
        
        ## Update the sprite's image on the TK Canvas
        self.tkcanvas.itemconfigure(self.sprites[sprite]['id'], image = photo)

        ## Update animation information for the sprite
        update = dict(photo=photo, animation = sprite.animations.current_loop(), image = image)
        self.sprites[sprite].update(update)


    def set_sprite_location(self, sprite: "sprites.Sprite", scale:float = None):
        """ Moves the sprite on the TK canvas to match it's canvas location """
        if scale is None: scale = self.scale

        olocation  = self.sprites[sprite]['location']
        dx, dy = sprite.location[0] - olocation[0], sprite.location[1] - olocation[1]
        self.tkcanvas.move(self.sprites[sprite]['id'], dx*scale, dy*scale)
        if(dy != 0):
            self.sprites[sprite]['zindex'] = sprite.zindex*100_000+sprite.location[1]

        self.sprites[sprite]['location'] = sprite.location
        
    def render(self, scale: float = None, background: "PIL.Image" = None):
        """ Renders all changes in sprites to the TK Canvas """
        if scale is None: scale = self.scale

        ## Keeps track of any missing sprites
        missingsprites = list(self.sprites)

        ## For each sprite determine whether or not it has changed
        for sprite in self.canvas.sprites:
            ## Sprite added
            if sprite not in self.sprites:
                self.add_sprite(sprite)
            else:
                ## Sprite is still on canvas, so remove from missingsprites
                missingsprites.remove(sprite)

                ## Sprite removed
                if sprite.zindex < 0:
                    self.remove_sprite(sprite) 

                else:
                    ssp = self.sprites[sprite]
                    ## Sprite has moved
                    if ssp['location'] != sprite.location:
                        self.set_sprite_location(sprite, scale = scale)

                    ## Sprite's animation has changed
                    if ssp['animation'] != sprite.animations.current_loop() or ssp['image'] != sprite.get_image():
                        self.set_sprite_animation(sprite)

        ## This sprite is no longer in canvas.sprites
        for sprite in missingsprites:
            self.remove_sprite(sprite)

        sprites = sorted(self.sprites.values(), key = lambda sprite: sprite['zindex'])
        while len(sprites) > 1:
            sprite = sprites.pop()
            self.tkcanvas.tag_raise(sprite['id'], sprites[0]['id'])