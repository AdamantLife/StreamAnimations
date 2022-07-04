## Test Framework
from hashlib import new
import unittest
## Test Target
from StreamAnimations import sprite

class StartlocationTestCase(unittest.TestCase):
    """ Unittests for the startlocation class """
    def test_setinitial(self):
        """ Makes sure the class properly records the Sprite's initial location regardless of if it changes """
        s = sprite.Sprite()
        
        start = sprite.startlocation(s)
        self.assertEqual(start._initial_location, None)
        s.location = (0,0)
        self.assertEqual(start._initial_location, None)

        start = sprite.startlocation(s)
        self.assertEqual(start._initial_location, (0,0))
        s.location = (1,1)
        self.assertEqual(start._initial_location, (0,0))
        s.location = None
        self.assertEqual(start._initial_location, (0,0))

    def test_setlocation(self):
        """ Tests that the initialization function changes the sprite's location if supplied """
        s = sprite.Sprite()
        ## Sanity check
        self.assertEqual(s.location, None)
        
        start = sprite.startlocation(s, (0,0))
        self.assertEqual(start._initial_location, None)
        self.assertEqual(s.location, (0,0))

    def test_revert(self):
        """ Tests that the revert method restores the previous location of the sprite """
        s = sprite.Sprite()
        
        start = sprite.startlocation(s)
        s.location = (10,10)
        ## Sanity Check
        self.assertEqual(s.location, (10,10))
        start.revert()
        self.assertEqual(s.location, None)
    
    def test_context(self):
        """ Tests that startlocation can be used as a context manager to automatically set and revert the sprite's location """
        s = sprite.Sprite()

        with sprite.startlocation(s):
            s.location = (10,10)
            ## Sanity check
            self.assertEqual(s.location, (10,10))
        
        self.assertEqual(s.location, None)

        ## DEV-NOTE: There is no need to test "with sl(mysprite, startlocation) because this is effectively covered by test_setlocation "

    def test_context_exc(self):
        """ Makes sure the location is still set even when an exception is raised (this should never fail as there
                should be no way to set sl._initial_location to a value that would in-turn raise an exception
        """
        s = sprite.Sprite()
        s.location = (10,10)
        ## We don't want the exception to propagate
        try:
            with sprite.startlocation(s, (33,33)):
                raise Exception()
        except: pass

        self.assertEqual(s.location, (10,10))

class SpriteTestCase(unittest.TestCase):
    def test_location_None(self):
        """ Tests that None is a valid location for Sprite """
        s = sprite.Sprite()
        ## Will raise errors instead of failing test
        s.location = None
        self.assertEqual(s.location, None)

    def test_at_context(self):
        """ Tests that the .at() method can be used as a context to manager to return a sprite to its original position after changing it. """

        s = sprite.Sprite()
        s.location = (0,0)
        with s.at(None):
            ## Sanity Check; this is covered in the startlocation unittests
            self.assertEqual(s.location, None)
        
        self.assertEqual(s.location, (0,0))