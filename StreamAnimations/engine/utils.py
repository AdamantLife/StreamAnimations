## This Module
from StreamAnimations.engine import Event
from StreamAnimations import utils
## 3rd Part
from PIL import Image, ImageChops


def check_overlap(hitbox1, hitbox2)-> bool:
    box1, box2 = hitbox1.bbox, hitbox2.bbox
    bx0, by0, bx1, by1 = box2
    for [x,y] in [
        (box1[0], box1[1]), ## tl
        (box1[2], box1[1]), ## tr
        (box1[0], box1[3]), ## bl
        (box1[2], box1[3]), ## br
        ]:
        if bx1 > x > bx0 and by1 > y > by0:
            return True
    return False

def find_nearby_sprites(targetsprite, othersprites) -> list:
    """ Check for overlapping bbox and return a list of overlapped boxes """
    if not targetsprite.hitboxes: return 
    tbboxes = targetsprite.hitboxes
    for sprite in othersprites:
        if sprite is not targetsprite:
            if sprite.hitboxes:
                for hitbox in sprite.hitboxes:
                    for tbbox in tbboxes:
                        if check_overlap(tbbox, hitbox):
                            yield (tbbox, hitbox)

def find_collisions(hitbox1, hitbox2):
    result = utils.find_overlap_of_images(hitbox1.image, hitbox2.image)
    result.show()
    print(">>>", result.getbbox())
    return bool(result.getbbox())


def collision_stop_rule(event: Event):
    """ Movement Event Rule which prevents Collisions """
    sprite = event.sprite
    canvas = event.canvas
    for (hitbox, hurtbox) in find_nearby_sprites(sprite, canvas.sprites):
        if find_collisions(hitbox, hurtbox):
            return False