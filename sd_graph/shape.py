# A textual notation for identifying formations -- primarily used for
# file naming.

# The notation described by Rich Reel at
# https://www.all8.com/sd/calling/fasr.htm is agnostic to individual
# dancer position.  The names of our SVG formation files need names
# that are very specific about where each dancer is.


class Shape (object):
    '''Shape represents the shape of a Formation.
    Shape has to do with the locations where dancers stand.
    This is the F in FASR but without considering direction.
    A subclass is defined to recognize each possible shape.'''

    # We might want some useful canonical ordering for PATTERN.
    PATTERN = None

    def __init__(self, formation, where):
        self.formation = formation
        self.where = where

    @classmethod
    def match(cls, formation):
        '''match determines if this subclass of Shape fits the formation.'''
        pattern = cls.PATTERN
        if pattern == None:
            return False
        where = {}
        for d in formation.dancers:
            key = (d.x, d.y)
            if key in pattern:
                where[key] = d
            else:
                return False
        return cls(formation, where)

    @classmethod
    def identify(cls, formation):
        '''identify determines which subclasses of Shape the formation
        conforms to and returns instances of those subclasses.'''
        found = []
        def walk(c):
            r = c.match(formation)
            if r:
                found.append(r)
            for sc in c.__subclasses__():
                walk(sc)
        walk(cls)
        return found

    def __str__(self):
        s = ''
        s += self.__class__.FILE_PREFIX
        for p in self.__class__.PATTERN:
            d = self.where[p]
            s += '_%d%s%d' % (d.couple_number, d.gender, d.direction)
        return s


class CircleOfEight (Shape):
    FILE_PREFIX = 'c'
    PATTERN = ((2, 0), (1, 0),
               (0, 1), (0, 2),
               (1, 3), (2, 3),
               (3, 2), (3, 1))


class HorizontalLineOfEight (Shape):
    FILE_PREFIX = 'h8'
    PATTERN = ((0, 0), (1, 0), (2, 0), (3, 0),
               (4, 0), (5, 0), (6, 0), (7, 0))


class VerticalLineOfEight (Shape):
    FILE_PREFIX = 'v8'
    PATTERN = ((0, 0), (0, 1), (0, 2), (0, 3),
               (0, 4), (0, 5), (0, 6), (0, 7))


class HorizontalLinesOfFour (Shape):
    FILE_PREFIX = 'h4'
    PATTERN = ((3, 0), (2, 0), (1, 0), (0, 0),
               (0, 1), (1, 1), (2, 1), (3, 1))


class VerticalLinesOfFour (Shape):
    FILE_PREFIX = 'v4'
    PATTERN = ((0, 0), (0, 1), (0, 2), (0, 3),
               (1, 3), (1, 2), (1, 1), (1, 0))


class HorizontalTag (Shape):
    FILE_PREFIX = 'ht'
    PATTERN = ((1, 0), (2, 0),
               (0, 1), (1, 1), (2, 1), (3, 1),
               (2, 2), (1, 2))
    

class VerticalTag (Shape):
    FILE_PREFIX = 'vt'
    PATTERN = ((0, 1), (0, 2),
               (1, 0), (1, 1), (1, 2), (1, 3),
               (3, 2), (3, 1))

