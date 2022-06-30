## Test Framework
from cgi import test
import unittest
## Test Target
from StreamAnimations import canvases
## Test Utilities
from StreamAnimations.tests import utils as testutils
## This Module
from StreamAnimations.engine import Event

class CanvasTestCase(unittest.TestCase):
    def test_add_listener(self):
        """ Tests that adding a listener to the canvas properly adds the callback to the canvas' events list """
        canvas = canvases.CanvasBase((0,0), 0)
        
        funcA  = lambda e: None
        def func2(event): pass

        ## movement is a standard event
        canvas.add_listener("movement", funcA)
        ## foobar is not a normal event, but it is not an error to add it to canvasbase
        canvas.add_listener("foobar", func2)

        ## Cannot use assertdictcontains
        self.assertIn(funcA, canvas.events['movement'])
        self.assertIn(func2, canvas.events['foobar'])

    def test_trigger_event(self):
        """ Tests that trigger_event calls the correct callbacks for the given event and passes them the correct object"""
        testresults = {"testA": None, "testZ": None}

        def callback(event):
            testresults["testA"] = event

        canvas = canvases.CanvasBase((0,0),0)
        canvas.add_listener("myevent", callback)
        
        event = Event(canvas, None, 0,0,0,0,0,0)
        for result in canvas.trigger_event("myevent", event): pass

        for (key, expected) in [
            ("testA", event),
            ("testZ", None)
            ]:
            self.assertEqual(testresults[key], expected)

class PopulatedCanvasTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.canvas = testutils.load_canvas()
        self.sprite = testutils.load_testsprite(hitboxes=[testutils.create_sprite_hitbox(),])
        self.desk = testutils.load_terrain_sprite(hitboxes=[testutils.create_terrain_hitbox(),])
        self.canvas.add_sprite(self.sprite, location = (0,0))
        self.canvas.add_sprite(self.desk, location = (0,0))

    def test_movementcallback(self):
        """ Tests that the canvas properly calls registered callbacks and supplies them with the expected Event """
        testresults = {"callbackA":None}

        self.canvas.add_listener("movement", lambda e: testresults.__setitem__("callbackA", e))

        self.canvas.move_sprite(self.sprite, "down")

        self.assertIsNotNone(testresults["callbackA"])
        
        expectedEvent = Event(self.canvas, self.sprite, x = 0, y = 0, z = 0, dx = 0, dy = testutils.STEPLENGTH,dz = None, extra = {})
        for (key, result) in expectedEvent.__dict__.items():
            self.assertEqual( getattr(testresults["callbackA"], key), result)