## Test Framework
import unittest
from StreamAnimations import sprite
## Test Target
from StreamAnimations.sprite import hitbox
## Test utilities
from StreamAnimations.tests import utils as testutils

## builtin
import pathlib
## 3rd Party
from PIL import Image, ImageChops

SAMPLEDIR = (pathlib.Path(__file__).parent / "samples").resolve()
RESULTSDIR = (SAMPLEDIR / "testresults").resolve()

class HitboxTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.HITBOXHEIGHT = 10
        self.sprite = testutils.load_testsprite()
        ## NOTE: Test images were created when default currentdirection was "Y"/"Down", so sprite may need to be updated
        self.sprite.animations.current_animation = "Y"

        self.desk = testutils.load_terrain_sprite()

        self.canvas = testutils.load_canvas()
    
    def test_create_rect_hitbox_image(self):
        """ Tests that create_rect_hitbox_image returns the expected mask """
        result = Image.open(RESULTSDIR / "create_rect.bmp").convert("1")

        testresult = hitbox.create_rect_hitbox_image(32, 10)

        self.assertIsNone(ImageChops.difference(testresult, result).getbbox())

class AnchorMixinTestCase(HitboxTestCase):
    def test_standardize_anchor(self):
        """ Makes sure that all anchor codes are standardized correctly """
        tests = [
            ("tl", "tl"), ## Top Left
            ("tc", "tc"), ## Top Center
            ( "t", "tc"), ## Top Center
            ("tr", "tr"), ## Top Right
            ("cl", "cl"), ## Center Left
            ( "l", "cl"), ## Center left
            ("lc", "cl"), ## Center Left
            ( "c", "cc"), ## Center
            ("cc", "cc"), ## Center
            (  "", "cc"), ## Center
            ("rc", "cr"), ## Center Right
            ( "r", "cr"), ## Center Right
            ("cr", "cr"), ## Center Right
            ("bl", "bl"), ## Bottom Left
            ("bc", "bc"), ## Bottom Center
            ( "b", "bc"), ## Bottom Center
            ("br", "br"), ## Bottom Right
        ]
        for (test, result) in tests:
            with self.subTest(test = test, result = result):
                self.assertEqual(hitbox.AnchorMixin.standardize_anchor(test), result)
        

    def test_topleft(self):
        """ Tests that the topleft function returns the appropriate top-left offset """
        tests = [
            ## Anchor, Spritelocation, Mask Size, Result

            ("tl", (0, 0), (32,10), ( 0, 0) ),
            ("tr", (0, 0), (32,10), ( 0, 0) ),
            ( "c", (0, 0), (32,10), ( 0,11) ),
            ("bl", (0, 0), (32,10), ( 0,22) ),
            ("br", (0, 0), (32,10), ( 0,22) ),

            ## The sprite's offset should effect the result linearly
            ## (compare to first 3 tests)
            ("tl", ( 5,  0), (32,10), (  5,  0) ),
            ("tr", ( 0,  5), (32,10), (  0,  5) ),
            ( "c", (-3, -3), (32,10), ( -3,  8) ),

            ## Changes to the mask's size effects the non-top/left of its corresponding axis
            ## i.e., changes to height effect vc and b, changes to width effect hc and r
            ("tl", (0, 0), (10, 5), (  0,  0) ),
            ("tr", (0, 0), (16, 5), ( 16,  0) ),
            ( "c", (0, 0), (30, 6), (  1, 13) ),
            ("bl", (0, 0), (10, 5), (  0, 27) ),
            ("br", (0, 0), (16, 5), ( 16, 27) ),
        ]

        ## The hitbox to test
        img = hitbox.create_rect_hitbox_image(32, 10)
        hb = hitbox.AnchoredHitbox(img)
        self.sprite.add_hitbox(hb)

        for (anchor, spritelocation, masksize, result) in tests:
            with self.subTest(anchor = anchor, spritelocation = spritelocation, masksize = masksize, result = result, hb = hb):

                self.sprite.location = spritelocation
                img = hitbox.create_rect_hitbox_image(*masksize)
                hb.image = img
                hb.anchor = anchor

                self.assertEqual(hb.topleft, result)

class MaskedHitboxTestCase(HitboxTestCase):
    def test_image(self):
        """ Tests that placing a rectangular mask at different points of the sprite results in different mask images """
        tests = [
            ## Anchor , resultimg
            ("tl", "mask_1.bmp"),
            ("l", "mask_2.bmp"),
            ("bl", "mask_3.bmp"),
        ]

        img = hitbox.create_rect_hitbox_image(32,10)
        hb = hitbox.MaskedHitbox(img)
        self.sprite.location = (0,0)
        self.sprite.add_hitbox(hb)
        
        for (anchor, result) in tests:
            with self.subTest(anchor = anchor, result = result):
                hb.anchor = anchor
                testresult = hb.image
                resultimg = Image.open(RESULTSDIR / result).convert("1")

                self.assertIsNone(ImageChops.difference(testresult,resultimg).getbbox())

    def test_image_special(self):
        """ Testing the mask with a special mask image """
        tests = [
            ## Anchor, resultimg
            ("tl", "mask2_1.bmp"),
            ("c", "mask2_2.bmp"),
            ("br", "mask2_3.bmp"),
        ]

        img = Image.open(SAMPLEDIR / "special_mask.bmp").convert("1")
        hb = hitbox.MaskedHitbox(img)
        self.sprite.location = (0,0)
        self.sprite.add_hitbox(hb)
        
        for (anchor, result) in tests:
            with self.subTest(anchor = anchor, result = result):
                hb.anchor = anchor
                testresult = hb.image
                resultimg = Image.open(RESULTSDIR / result).convert("1")

                self.assertIsNone(ImageChops.difference(testresult,resultimg).getbbox())