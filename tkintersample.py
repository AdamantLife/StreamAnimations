## This Module
from StreamAnimations import utils, sprite
from StreamAnimations.sprite import hitbox
from StreamAnimations.canvases import SinglePageCanvas
from StreamAnimations.engine import utils as engineutils
from StreamAnimations.systems import twodimensional

## Renderer
from StreamAnimations.engine.renderers.tkinter import TkinterCanvas

## Buitlin
import tkinter as tk

## Builtin
import pathlib
import random

ROOT = pathlib.Path(__file__).resolve().parent
SAMPLEDIR = (ROOT / "samples").resolve()
SPRITESIZE = 32
CANVASSIZE = 1920, 1080
BASEHEIGHT = 10
FRAMERATE = 16


def load_walk():
    up, down, right = utils.import_spritesheet((SAMPLEDIR / "Walk Up.png").resolve()), \
        utils.import_spritesheet((SAMPLEDIR / "Walk Down.png").resolve()), \
            utils.import_spritesheet((SAMPLEDIR / "Walk Right.png"))
    directions = dict(up = utils.split_spritesheet(up, SPRITESIZE, SPRITESIZE),
        down = utils.split_spritesheet(down, SPRITESIZE, SPRITESIZE),
        right = utils.split_spritesheet(right, SPRITESIZE, SPRITESIZE)
        )
    directions["left"] = utils.mirror_sprite(directions['right'])

    return directions

def load_printer():
    frames = []
    for zlevel in range(1,6):
        sheet = utils.import_spritesheet( (SAMPLEDIR / f"Prusa Z{zlevel}.png").resolve())
        frames.extend(utils.split_spritesheet(sheet, SPRITESIZE, SPRITESIZE))
    return {"idle": frames}

def load_desk():
    return {"idle":utils.split_spritesheet(utils.import_spritesheet( (SAMPLEDIR / "Desk-1.png").resolve()), SPRITESIZE, 45)}

def load_desk_text():
    return {"idle": utils.split_spritesheet(utils.import_spritesheet( (SAMPLEDIR / "stream.png").resolve() ), SPRITESIZE, 21)}

walk = load_walk()
me = twodimensional.Sprite2D(directionalsprites= walk, hitboxes = [], animations = {"idle":[walk['down'][0],]})
mehitbox = hitbox.MaskedHitbox(hitbox.create_rect_hitbox_image(me.get_image().width, BASEHEIGHT),anchor="bl")
me.add_hitbox(mehitbox)

printer = sprite.StationarySprite(animations=load_printer())
printerhitbox = hitbox.MaskedHitbox(hitbox.create_rect_hitbox_image(printer.get_image().width, BASEHEIGHT//2), anchor="bl")
printer.add_hitbox(printerhitbox)
desk = sprite.StationarySprite(animations= load_desk())
deskhitbox = hitbox.MaskedHitbox(hitbox.create_rect_hitbox_image(desk.get_image().width, BASEHEIGHT),anchor="bl")
desk.add_hitbox(deskhitbox)
monitortext = sprite.CosmeticSprite(animations= load_desk_text(), offset = (12,12), parent = desk)

canvas = SinglePageCanvas(CANVASSIZE, SPRITESIZE // 4)
canvas.add_listener("movement", engineutils.collision_stop_rule)

canvas.add_sprite(me, (50, 70))
canvas.add_sprite(printer, (80,80))
canvas.add_sprite(monitortext)
canvas.add_sprite(desk, (50, 50))

path = ["right","right","right","right","right", "up", "up", "up", "up","left","left","left","left","left"]


def movecallback():
    if path: canvas.move_sprite(me, path.pop(0))
    if(printer.animations.is_last_frame()): printer.animations.pause()
    idles = []
    for sprite in canvas.sprites:
        if sprite != me:
            idles.append(sprite)
    canvas.animate_idlesprites(idles)
    renderer.render(scale = renderer.scale, background = renderer.background)
    root.after(1000//FRAMERATE, movecallback)

root = tk.Tk()
tkcanvas = tk.Canvas(root, width= CANVASSIZE[0], height = CANVASSIZE[1])
tkcanvas.pack()
renderer = TkinterCanvas(canvas, tkcanvas, framerate=FRAMERATE, scale = 5)
renderer.render(scale = renderer.scale, background = renderer.background)
root.after(1000//FRAMERATE, movecallback)
root.mainloop()