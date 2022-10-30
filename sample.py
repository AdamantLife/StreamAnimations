## This module
from StreamAnimations import utils, sprite
from StreamAnimations.sprite import hitbox
from StreamAnimations.canvases import SinglePageCanvas
from StreamAnimations.engine.renderers.gif import GifRenderer
from StreamAnimations.engine import utils as engineutils
from StreamAnimations.systems import twodimensional

## Builtin
import pathlib
import random

ROOT = pathlib.Path(__file__).resolve().parent
OUTDIR = ( ROOT / "output").resolve()
OUTDIR.mkdir(exist_ok = True)
SAMPLEDIR = (ROOT / "samples").resolve()
SPRITESIZE = 32
CANVASSIZE = 384, 216
BASEHEIGHT = 10

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
monitortext = sprite.CosmeticSprite(animations= load_desk_text(), offset = (12, 12), parent = desk)

canvas = SinglePageCanvas(CANVASSIZE, SPRITESIZE // 4)
canvas.add_listener("movement", engineutils.collision_stop_rule)

canvas.add_sprite(me, (50, 70))
canvas.add_sprite(printer, (80,80))
canvas.add_sprite(monitortext, (0,0))
canvas.add_sprite(desk, (50, 50))


## ANIMATION
renderer = GifRenderer(canvas, sorter= twodimensional.twod_sprite_sorter)
with renderer.frame(): pass

path = ["right","right","right","right","right", "up", "up", "up", "up","left","left","left","left","left"]

for i in range(100):
    with renderer.frame(record_hitboxes = True) as frame:
        #frame.move_sprite(me, random.choice(twodimensional.TwoDimensional_4Way.directions()))
        if path: frame.move_sprite(me, path.pop(0))
        if(printer.animations.is_last_frame()): printer.animations.pause()

renderer.save((OUTDIR / "map2.gif"), 10, scale = 5)