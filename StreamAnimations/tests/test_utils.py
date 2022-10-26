## Test Framework
import unittest
## Test Target
from StreamAnimations import utils
## Test Helper Functions
from StreamAnimations.tests import utils as testutils

## This Module
from StreamAnimations.sprite import hitbox
## Builtin
import pathlib
## Third Party
from PIL import Image, ImageChops


class UtilsTestCase(unittest.TestCase):
    """ Covers tests that do not require additional setup """

    def test_offset_boundingbox(self):
        """ Tests that a bounding box is appropriately shifted by x and y delta """
        tests = [
            ( (  0,  0 ,  0,  0),    0,    0,    (  0,  0,  0,  0)),
            ( (  0,  0 ,  0,  0),    1,    0,    (  1,  0,  1,  0)),
            ( (  0,  0 ,  0,  0),    0,    1,    (  0,  1,  0,  1)),
            ( (  0,  0 ,  0,  0),    1,    1,    (  1,  1,  1,  1)),
            ( ( -3, -3 ,  1,  1),    1,    1,    ( -2, -2,  2,  2)),
        ]
        for (bbox, deltax, deltay, result) in tests:
            with self.subTest(bbox = bbox, deltax = deltax, deltay = deltay, result = result):
                self.assertEqual(utils.offset_boundingbox(bbox, deltax, deltay), result)

    def test_find_overall_boundingbox(self):
        """ Tests that the minimum bounding box required to encompass two given bounding boxes is returned """
        tests = [
            ( (  0,  0,  0,  0),    (  0,  0,  0,  0),  (  0,  0,  0,  0)), ## 0-width/height boxes returns 0-width/height boxes
            ( (  0,  0,  0,  0),    (  0,  0,  1,  1),  (  0,  0,  1,  1)), ## Both boxes have the same upper-left, second box extends furthest
            ( (  0,  0,  1,  1),    (  0,  0,  0,  0),  (  0,  0,  1,  1)), ## Both boxes have the same upper-left, first box extends furthest
            ( ( -1, -1,  0,  0),    (  0,  0,  1,  1),  ( -1, -1,  1,  1)), ## Box 1 offset -1 and is 1 width/height, Box 2 is same width/height from origin
            ( ( -1, -1,  2,  2),    (  0,  0,  1,  1),  ( -1, -1,  2,  2)), ## Box 1 fully encompasses Box 2
            ( (  0,  0,  1,  1),    ( -1, -1,  2,  2),  ( -1, -1,  2,  2)), ## Box 2 fully encompasses Box 1
            ( (  0,  0,  1,  1),    (  1,  1,  2,  2),  (  0,  0,  2,  2)), ## Box 1 and Box 2 are not overlapping (touching at corner)
            ( (  0,  0,  1,  1),    (  0,  1,  1,  2),  (  0,  0,  1,  2)), ## Box 1 and Box 2 are not overlapping (touching along bottom edge)
            ( (  0,  0,  1,  1),    (  1,  0,  2,  1),  (  0,  0,  2,  1)), ## Box 1 and Box 2 are not overlapping (touching along right edge)
            ( (  0,  0,  1,  1),    (  0,  1,  1,  2),  (  0,  0,  1,  2)), ## Box 1 and Box 2 are not overlapping (touching along bottom edge)
            ( (  0,  0,  1,  1),    (  1,  2,  2,  3),  (  0,  0,  2,  3)), ## Box 1 and Box 2 are not overlapping (and not touching in any way)
        ]
        for (bbox1, bbox2, result) in tests:
            with self.subTest(bbox1 = bbox1, bbox2 = bbox2, result = result):
                self.assertEqual(utils.find_overall_boundingbox(bbox1, bbox2), result)

class UtilsSpriteTestCase(unittest.TestCase):
    """ Tests which require Sprites/Canvas to be loaded """
    def setUp(self) -> None:
        self.HITBOXHEIGHT = 10

        spritehitbox = hitbox.MaskedHitbox(hitbox.create_rect_hitbox_image(testutils.SPRITESIZE, self.HITBOXHEIGHT))
        self.sprite = testutils.load_testsprite(hitboxes = [spritehitbox,])
        ## NOTE: Test images were created when default currentdirection was "Y"/"Down", so sprite may need to be updated
        self.sprite.currentdirection = "Y"

        self.desk = testutils.load_terrain_sprite()
        deskhitbox = hitbox.MaskedHitbox(hitbox.create_rect_hitbox_image(self.desk.get_image().width, self.HITBOXHEIGHT))
        self.desk.add_hitbox(deskhitbox)

        self.canvas = testutils.load_canvas()

    def test_opaque_mask(self):
        """ Tests that the result of opaque_mask matches expected image """
        tests = [
            (self.sprite.get_image(),    "opaque_mask_1.bmp"), 
            (self.desk.get_image(),      "opaque_mask_2.bmp"),
        ]
        for (testimage, resultimage) in tests:
            with self.subTest(testimage = testimage, resultimage = resultimage):
                testresult = utils.opaque_mask(testimage)
                result = Image.open( (testutils.SAMPLEDIR / "testresults") / resultimage).convert("1")

                self.assertIsNone(ImageChops.difference(testresult, result).getbbox())

    def test_find_overlap_of_images_nobbox(self):
        """ Tests that find_overlap_of_images works with no bboxes provided.
        
            Note that not providing bboxes anchors both sprites by their top-left corner
        """
        ## Removing hitboxes
        self.sprite.hitboxes = []
        self.desk.hitboxes = []

        tests = [
            (self.sprite.get_image(), self.sprite.get_image(),    (  8,  0,  24,  32)),
            (self.sprite.get_image(), self.desk.get_image(),      (  8,  8,  24,  32)),
        ]
        for (image1, image2, result) in tests:
            with self.subTest(image1 = image1, image2 = image2, result = result):
                image1, image2 = utils.opaque_mask(image1), utils.opaque_mask(image2)
                r = utils.find_overlap_of_images(image1, image2, bbox1 = None, bbox2 = None)
                self.assertEqual(r.getbbox(), result)

    def test_find_overlap_of_images_bbox(self):
        """ Tests that find_overlap_of_images works with bboxes provided """
        ## Removing hitboxes
        self.sprite.hitboxes = []
        self.desk.hitboxes = []

        tests = [
            ## image1,    image2,    result,    bbox1,    bbox2
            (self.sprite.get_image(), self.sprite.get_image(),    (  8,  0,  24,  32),    (0, 0, 32, 32),    (0, 0, 32, 32)), ## Same as test_find_overlap_of_images_nobbox subtest 1
            (self.sprite.get_image(), self.desk.get_image(),      (  8,  8,  24,  32),    (0, 0, 32, 32),    (0, 0, 45, 32)), ## Same as test_find_overlap_of_images_nobbox subtest 2
            
            (self.sprite.get_image(), self.sprite.get_image(),    (  18,  11,  24,  22),    (0, 0, 32, 32),    (10, 0, 42, 32)), ## Sprite 2 offset to right
            (self.sprite.get_image(), self.sprite.get_image(),    (  8,  11,  14,  22),    (0, 0, 32, 32),    (-10, 0, 22, 32)), ## Sprite 2 offset to left
            (self.sprite.get_image(), self.sprite.get_image(),    None,    (0, 0, 32, 32),    (32, 32, 64, 64)), ## Sprites do not overlap at all

            (self.sprite.get_image(), self.desk.get_image(),    (  14,  10,  24,  32),    (0, 0, 32, 32),    (10, 0, 55, 32)), ## Sprite 2 offset to right
            (self.sprite.get_image(), self.desk.get_image(),    (  8,  8,  24,  29),    (0, 0, 32, 32),    (-10, 0, 35, 32)), ## Sprite 2 offset to left
            (self.sprite.get_image(), self.desk.get_image(),    None,    (0, 0, 32, 32),    (32, 32, 77, 64)), ## Sprites do not overlap at all
        ]

        for (image1, image2, result, bbox1, bbox2) in tests:
            with self.subTest(image1 = image1, image2 = image2, result = result, bbox1 = bbox1, bbox2 = bbox2):
                image1, image2 = utils.opaque_mask(image1), utils.opaque_mask(image2)
                self.assertEqual(utils.find_overlap_of_images(image1, image2, bbox1 = bbox1, bbox2 = bbox2).getbbox(), result)

    # def test_find_overlap_of_images_nobbox_with_hitboxes(self):
    #     """ Tests that find_overlap_of_images works with nobboxes provided and hitboxes"""
    #     tests = [
    #         (self.sprite.get_image(), self.sprite.get_image(),    (  8,  0,  24,  32)),
    #         (self.sprite.get_image(), self.desk.get_image(),      (  8,  8,  24,  32)),
    #     ]
    #     for (image1, image2, result) in tests:
    #         with self.subTest(image1 = image1, image2 = image2, result = result):
    #             image1, image2 = utils.opaque_mask(image1), utils.opaque_mask(image2)
    #             r = utils.find_overlap_of_images(image1, image2, bbox1 = None, bbox2 = None)
    #             self.assertEqual(r.getbbox(), result)

    # def test_find_overlap_of_images_bbox_with_hitboxes(self):
    #     """ Tests that find_overlap_of_images works with bboxes provided and hitboxes"""
    #     tests = [
            
    #     ]
    #     for (image1, image2, result) in tests:
    #         with self.subTest(image1 = image1, image2 = image2, result = result):
    #             image1, image2 = utils.opaque_mask(image1), utils.opaque_mask(image2)
    #             self.assertEqual(utils.find_overlap_of_images(image1, image2, bbox1 = None, bbox2 = None), result)
    