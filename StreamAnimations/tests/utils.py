## This Module
from StreamAnimations import utils, sprite, canvases
from StreamAnimations.sprite import hitbox
## Builtin
import pathlib

SAMPLEDIR = (pathlib.Path(__file__).parent / "samples").resolve()
SPRITESIZE = 32
STEPLENGTH = SPRITESIZE // 4

def load_testsprite(hitboxes = None)-> sprite.Sprite2D:
    up, down, right = utils.import_spritesheet((SAMPLEDIR / "Walk Up.png").resolve()), \
        utils.import_spritesheet((SAMPLEDIR / "Walk Down.png").resolve()), \
            utils.import_spritesheet((SAMPLEDIR / "Walk Right.png"))
    directions = dict(up = utils.split_spritesheet(up, SPRITESIZE, SPRITESIZE),
        down = utils.split_spritesheet(down, SPRITESIZE, SPRITESIZE),
        right = utils.split_spritesheet(right, SPRITESIZE, SPRITESIZE)
        )
    directions["left"] = utils.mirror_sprite(directions['right'])

    sp = sprite.Sprite2D(cardinalsprites= directions, hitboxes = [])
    if hitboxes:
        for hb in hitboxes:
            sp.add_hitbox(hb)
    return sp

def load_terrain_sprite(hitboxes = None)->sprite.StationarySprite:
    img = utils.split_spritesheet(utils.import_spritesheet( (SAMPLEDIR / "Desk-1.png").resolve()), SPRITESIZE, 45)
    desk= sprite.StationarySprite(representation= img)
    if hitboxes:
        for hb in hitboxes:
            desk.add_hitbox(hb)
    return desk

def load_canvas(size = (500, 500), steplength = STEPLENGTH)-> canvases.CanvasBase:
    return canvases.CanvasBase(size = size, steplength= steplength)

def create_sprite_hitbox():
    return hitbox.MaskedHitbox(image = hitbox.create_rect_hitbox_image(32,10), anchor = "bl")

def create_terrain_hitbox():
    return hitbox.MaskedHitbox(image = hitbox.create_rect_hitbox_image(45,10), anchor = "bl")