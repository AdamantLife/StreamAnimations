## Builtin
import itertools

class Coordinate():
    pass


class CoordinateSystem():

    """
    _AXES should be bi-directional (i.e.- "x", "y")
    _AXES negative direction is denoted as a lowercase string, positive is uppercase
    If the coordinate system does not use bi-directional axes, _DIRECTIONS should be
        supplied instead.
    """
    _AXES = None
    _DIRECTIONS = None
    _ALIASES = None
    
    @classmethod
    def axes(cls):
        return cls._AXES

    @classmethod
    def directions(cls):
        """ Returns cls._DIRECTIONS if supplied, otherwise returns the positive and negative
            direction of each axis of cls._AXES
        """
        if cls._DIRECTIONS: return cls._DIRECTIONS
        out = []
        for axis in cls.axes():
            out.append(axis)
            out.append(axis.upper())
        return out

    @classmethod
    def valid_direction(cls, direction):
        """ Makes sure that direction represents an axis or is an alias for a direction on an axis """
        if direction.lower() in cls.directions(): return
        if direction in cls._ALIASES: return
        raise ValueError(f"Invalid direction {direction}")

    @classmethod
    def normalize_direction(cls, direction):
        """ Makes sure the direction is valid and returns it in terms of positive/negative axis"""
        cls.valid_direction(direction)
        if direction.lower() in cls.axes(): return direction
        return cls._ALIASES[direction]

    @classmethod
    def determine_direction(cls, offset: tuple)->str:
        """ Given an offset, determine the direction in which the offset lies """
        out = ""
        for o,a in zip(offset, cls.axes()):
            if o > 0: out+= a.upper()
            elif o < 0: out+= a.lower()

        return out

    @classmethod
    def determine_offset(cls, direction: str, steplength:int = 1)-> tuple:
        """ Converts a direction to an offset """
        out = []
        direction = cls.normalize_direction(direction)

        for axis in cls.axes():
            if axis not in direction.lower(): out.append(0)
            elif axis in direction: out.append(-1*steplength)
            else: out.append(+1*steplength)
        return out

    @classmethod
    def determine_offset_coordinate(cls, direction: str, coordinate: tuple, steplength:int = 1)-> tuple:
        """ Modifies the provided coordinate by the result of determine_offset """
        off = cls.determine_offset(direction= direction, steplength = steplength)
        return tuple(a+b for (a,b) in zip(off, coordinate))

    @classmethod
    def calculate_offset(cls, target: tuple, relative_to: tuple, steplength:int = 1)-> tuple:
        """ Returns the offset of a target coordinate relative to another coordinate """
        out = []
        for a,b in zip(target,relative_to):
            if a > b: out.append(+1*steplength)
            elif a < b: out.append(-1*steplength)
            else: out.append(0)
        return tuple(out)

    @classmethod
    def is_adjacent(cls, a, b, steplength:int = 1):
        """ Returns whether a is adjacent to be (within offset {steplength} in only one axis and 0 in the rest)
                and b is not a.
        """
        return  sum( abs(axis) for axis in  [aaxis - baxis for aaxis,baxis in zip(a,b)]) == steplength

    @classmethod
    def convert_to_steplength(cls, coord, steplength:int):
        """ Convenience function to convert from an absolute pixel coordinate to a relative steplength coordinate """
        return [axis//steplength for axis in coord]
    @classmethod
    def convert_from_steplength(cls, coord, steplength:int):
        """ Convenience function to convert from a relative steplength coordinate to an absolute pixel coordinate """
        return [axis*steplength for axis in coord]
    @classmethod
    def round_to_steplength(cls, coord, steplength:int):
        """ Convenience function to round an absolute pixel coordinate down to an absolute coordinate that coincides with a relative coordinate """
        return cls.convert_from_steplength(cls.convert_to_steplength(coord, steplength=steplength), steplength= steplength)

def mixeddirection(coordinatesystem: CoordinateSystem):
    """ Updates a CoordinateSystem subclass' _DIRECTIONS attribute for all combinations of its axes """
    coordinatesystem._DIRECTIONS = []
    for i in range(len(coordinatesystem._AXES)+1):
        coordinatesystem._DIRECTIONS.extend(itertools.combinations(coordinatesystem._AXES, i))

    coordinatesystem.is_adjacent = classmethod(lambda cls, a, b: all(abs(axis) <= 1 for axis in [aaxis - baxis for aaxis,baxis in zip(a,b)] and a != b))
    
    
