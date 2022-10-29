import math

def squaredistance(pointa,pointb):
    """ Returns the sum of the absolute difference across all axes between two points """
    return sum(abs(a-b) for a,b in zip(pointa,pointb))

def lineardistance(pointa,pointb):
    """ Returns the cartesian distance betwen two points """
    return (abs(pointa[0] - pointb[0])**2 + abs(pointa[1] - pointb[1])**2)**.05