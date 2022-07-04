## This Module
from StreamAnimations.engine import Event
from StreamAnimations import sprite,utils
from StreamAnimations.sprite import hitbox
## 3rd Part
from PIL import Image, ImageChops


def find_nearby_sprites(targetsprite, othersprites) -> list:
    """ Check for overlapping bbox and return a list of overlapped boxes """
    if not targetsprite.hitboxes: return 
    tbboxes = targetsprite.hitboxes
    for sprite in othersprites:
        if sprite is not targetsprite:
            if sprite.hitboxes:
                for hitbox in sprite.hitboxes:
                    for tbbox in tbboxes:
                        if utils.check_boundingbox_overlap(tbbox.bbox, hitbox.bbox):
                            yield (tbbox, hitbox)

def find_collisions(hitbox1: hitbox.Hitbox, hitbox2: hitbox.Hitbox):
    result = utils.find_overlap_of_images(hitbox1.image, hitbox2.image, bbox1= hitbox1.bbox, bbox2= hitbox2.bbox)
    return bool(result.getbbox())


def collision_stop_rule(event: Event):
    """ Movement Event Rule which prevents Collisions """
    targetsprite = event.sprite
    canvas = event.canvas
    targetx, targety = event.x + event.dx, event.y + event.dy
    with targetsprite.at( (targetx, targety) ):
        for (hitbox, hurtbox) in find_nearby_sprites(targetsprite, canvas.sprites):
            if find_collisions(hitbox, hurtbox):
                return False