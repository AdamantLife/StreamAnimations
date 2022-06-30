## This module
from StreamAnimations import utils, sprite
from StreamAnimations.sprite import hitbox
from StreamAnimations.canvases import gif
from StreamAnimations.engine import utils as engineutils

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
    return frames

def load_desk():
    return utils.split_spritesheet(utils.import_spritesheet( (SAMPLEDIR / "Desk-1.png").resolve()), SPRITESIZE, 45)

def load_desk_text():
    return utils.split_spritesheet(utils.import_spritesheet( (SAMPLEDIR / "stream.png").resolve() ), SPRITESIZE, 21)

me = sprite.Sprite2D(cardinalsprites= load_walk(), hitboxes = [])
mehitbox = hitbox.MaskedHitbox(hitbox.create_rect_hitbox_image(me.get_image().width, BASEHEIGHT),anchor="bl")
me.hitboxes.append(mehitbox)

printer = sprite.StationarySprite(representation=load_printer())
desk = sprite.StationarySprite(representation= load_desk())
deskhitbox = hitbox.MaskedHitbox(hitbox.create_rect_hitbox_image(desk.get_image().width, BASEHEIGHT),anchor="bl")
monitortext = sprite.CosmeticSprite(idleanimations= load_desk_text(), offset = (12, 12), parent = desk)

canvas = gif.SinglePageCanvas(CANVASSIZE, SPRITESIZE // 4)
canvas.add_sprite(me, (50, 50), zindex=500)
canvas.add_sprite(printer, (80,80))
canvas.add_sprite(monitortext, (0,0))
canvas.add_sprite(desk, (50, 50), zindex=-1)
canvas.add_listener("movement", engineutils.collision_stop_rule)

## ANIMATION
startframe = canvas.frame()
startframe.record_frame()
canvas.add_frame(startframe)

for i in range(100):
    with canvas.frame() as frame:
        frame.move_sprite(me, random.choice(sprite.Sprite2D.CARDINALS))
        frame.move_sprite(printer, offset = (0,0))

canvas.save((OUTDIR / "map2.gif"), 10, scale = 5)