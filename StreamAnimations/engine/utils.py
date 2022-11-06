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


def collision_callback_rule(callback):
    """ Returns a function which checks for collisions, triggers the provided
        callback with the collision as part of the Event, and returns the result
        of the callback

        The callback should accept the movement Event as a parameter. The hitbox
            that was involved in the collision is set as event.collisionhitbox.
    """
    def rule(event: Event):
        targetsprite = event.sprite
        canvas = event.canvas
        targetx, targety = event.x + event.dx, event.y + event.dy
        with targetsprite.at( (targetx, targety) ):
            for (hitbox, hurtbox) in find_nearby_sprites(targetsprite, [sprite for sprite in canvas.sprites if sprite.zindex > -1]):
                if find_collisions(hitbox, hurtbox):
                    event.collisionhitbox = hurtbox
                    return callback(event)
    return rule

""" When a collision is detected, False is always returned (the move is canceled) """
collision_stop_rule = collision_callback_rule(lambda event: False)