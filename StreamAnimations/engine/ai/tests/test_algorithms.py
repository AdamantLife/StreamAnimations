## Test Target
from StreamAnimations.engine.ai import algorithms
## Test Framework
import unittest
## Utilities
from StreamAnimations.engine.ai.heuristics import distances

class AStarTestCase(unittest.TestCase):
    def adjacents2d(self, coord):
        """ Returns adjacent coordinates in 2d space with a distance of 1"""
        for dx,dy in [ (1,0), (0,1), (-1,0), (0, -1)]:
            yield (coord[0]+dx, coord[1]+dy), 1

    def test_returnstart(self):
        """ Tests that AStar, when start and stop coord are the same, returns the start cell """
        for startend in [ (0,0), (1,1), (-1,-1)]:
            with self.subTest(startend = startend):
                self.assertEqual(
                    list(algorithms.astar(start = startend, target = startend,
                                    adjacent = lambda *args: None,
                                    heuristic = lambda *args: 0)),
                    [startend,])

    def test_basic(self):
        """ Tests that astar will find the path between start and target points on a theoritcally infinite, unobstructed plane """
        for start,target, result in [
            ##  Start       Target      Result
            (   ( 0, 0),    ( 1, 1),    [ ( 0, 0), ( 0, 1), ( 1, 1)] ), 
            (   ( 0, 0),    ( 2, 2),    [ ( 0, 0), ( 0, 1), ( 0, 2), ( 1, 2), ( 2, 2)] ), 
            (   (-1,-1),    ( 0, 0),    [ (-1,-1), (-1, 0), ( 0, 0)] ),
            (   (-1,-1),    ( 2, 1),    [ (-1,-1), (-1, 0), (-1, 1), ( 0, 1), ( 1, 1), ( 2, 1)] )
        ]:
            with self.subTest(start = start, target = target, result = result):
                self.assertEqual(
                    list(algorithms.astar(start = start,
                        target = target,
                        adjacent= self.adjacents2d,
                        heuristic=distances.squaredistance
                        )),
                        result
                )