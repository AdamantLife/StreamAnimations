## Test Framework
import unittest
from StreamAnimations import sprite
## Target Module
from StreamAnimations.engine import utils
## Test Helper functions
from StreamAnimations.tests import utils as testutils

## This Moudle
from StreamAnimations.sprite import hitbox

class EngineUtils(unittest.TestCase):
    def setUp(self) -> None:
        self.HITBOXHEIGHT = 10

        spritehitbox = hitbox.MaskedHitbox(hitbox.create_rect_hitbox_image(testutils.SPRITESIZE, self.HITBOXHEIGHT),anchor="bl")
        self.sprite = testutils.load_testsprite(hitboxes = [spritehitbox,])

        self.desk = testutils.load_terrain_sprite()
        deskhitbox = hitbox.MaskedHitbox(hitbox.create_rect_hitbox_image(self.desk.get_image().width, self.HITBOXHEIGHT),anchor="bl")
        self.desk.add_hitbox(deskhitbox)

        self.canvas = testutils.load_canvas()

class EngineUtilsTestCase(EngineUtils):
    def setUp(self) -> None:
        return super().setUp()

    def test_find_nearby_sprites(self):
        """ Tests that find_nearby_sprites finds overlapping hitbox boundingboxes """
        ## Note: results are 1 or 0 because the sprites in question only have 1 hitbox
        tests = [
            ## spritelocation,    desklocation,    result
            ((  0,  0),    (  0,  0),  1), ## Sprites aligned in top-left corner, bounding boxes overlapping in same place
            ((  0,  0),    (  5,  0),  1), ## desk offset from origin by less than hitbox width means it should still be overlapping
            ((  0,  0),    (  0,  5),  1), ## desk offset from origin by less than hitbox height means it should still be overlapping
            (( 45,  0),    (  0,  0),  0), ## sprite offset by more than desk hitbox width means it's not overlapping
            ((  0, 10),    (  0,  0),  0), ## sprite offset by more than desk hitbox height means it's not overlapping
            (( 45, 10),    (  0,  0),  0), ## both offsets from above, still not overlapping
            ((100,100),    (  0,  0),  0), ## sprite no where near desk
            ((  0,  0),    (-77,  0),  0), ## negative-offset example; desk is shifted left to not overlap
        ]
        
        for (spritelocation, desklocation, result) in tests:
            with self.subTest(spritelocation = spritelocation, desklocation = desklocation, result = result):
                self.sprite.location = spritelocation
                self.desk.location = desklocation

                ## At (0,0), the base of the sprites (where their hitboxes overlap) are overlapping
                bboxes = list(utils.find_nearby_sprites(self.sprite, [self.desk,]))
                self.assertEqual(len(bboxes), result)

                ## The reciprocal should also be true
                bboxes = list(utils.find_nearby_sprites(self.desk, [self.sprite,]))
                self.assertEqual(len(bboxes), result)

    def test_find_collisions(self):
        """ Checks collisions between sprites with hitboxes """
        tests = [
            ## sprite location, desk location, result/collision
            ( ( 0, 0),                    ( 0, 0),                    True ), ## Desk and Sprite are same height with bottom-aligned hitboxes, so boxes should overlap and find_collisions should return True
            ( ( 0, 0),                    ( 0, self.HITBOXHEIGHT),    False), ## Desk's hitbox is below Sprite's hitbox
            ( ( 0, self.HITBOXHEIGHT),    ( 0, 0),                    False), ## Sprite's hitbox is below Desk's hitbox
        ]
        for (spriteloc, deskloc, result) in tests:
            with self.subTest(spriteloc = spriteloc, deskloc = deskloc, result = result):
                self.sprite.location = spriteloc
                self.desk.location = deskloc

                testresult = utils.find_collisions(self.sprite.hitboxes[0], self.desk.hitboxes[0])
                self.assertEqual(testresult, result)

class EngineUtilsRulesTestCase(EngineUtils):
    def setUp(self) -> None:
        return super().setUp()

    def test_collision_stop_rule(self)-> None:
        """ Tests that a sprite cannot move into another sprite """

        self.canvas.add_listener("movement", utils.collision_stop_rule)

        self.canvas.add_sprite(self.desk, (250, 250))
        ## Sprite is placed so that it's base is directly below the desk's base
        spritestartlocation = (250, 250+self.HITBOXHEIGHT)
        self.canvas.add_sprite(self.sprite, spritestartlocation)

        ## Make sure that the sprites are where they are at
        self.assertEqual(self.desk.location, (250,250))
        self.assertEqual(self.sprite.location, spritestartlocation)
        ## Try moving up, through desk
        self.canvas.move_sprite(self.sprite, "up")
        ## sprite shouldn't have moved
        self.assertEqual(self.sprite.location, spritestartlocation)

        ## Make sure sprite can move, period
        targetlocation = (250+testutils.STEPLENGTH, 250+self.HITBOXHEIGHT)
        self.canvas.move_sprite(self.sprite, "right")
        self.assertEqual(self.sprite.location, targetlocation)

        self.sprite.location = (250,250+self.HITBOXHEIGHT)
        targetlocation = (250, 250+self.HITBOXHEIGHT+testutils.STEPLENGTH)
        self.canvas.move_sprite(self.sprite, "down")
        self.assertEqual(self.sprite.location, targetlocation)