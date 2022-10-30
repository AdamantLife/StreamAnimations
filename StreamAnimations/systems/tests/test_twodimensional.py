## Test Framework
import unittest
## Test Target
from StreamAnimations.systems import twodimensional

class TwoDimensionalCase(unittest.TestCase):
    """ General tests for the module """

    def test_twod_sprite_sorter(self):
        """ General test of the twod_sprite_sorter """
        tests = [
                ## Positios to Sort
            ([  (   (0,0),  0), (   (0,1),  0), (   (0,2),  0),                 ],  [2,1,0]),
            ([  (   (0,0),  0), (   (0,1),  1), (   (0,2),  2),                 ],  [2,1,0]),
            ([  (   (5,5),  0), (   (8,8),  0), (   (0,2),  0),                 ],  [1,0,2]),
            ([  (   (0,5),  0), (   (0,5),  1), (   (0,2),  2),                 ],  [2,1,0]),
            ([  (   (0,5),  0), (   (0,5),  1), (   (0,2),  1),                 ],  [1,2,0]),
            ([  (   (0,5),  0), (   (0,5),  1), (   (0,2),  2), ((10, 10), -1)  ],  [2,1,0]),
            
        ]

        for (test, result) in tests:
            with self.subTest(test = test, result = result):
                self.assertListEqual(twodimensional.twod_sprite_sorter(*test), result)