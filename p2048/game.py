"""p2048 game classes"""

from enum import Enum
import threading
import random

class Directions(Enum):
    RIGHT = 0
    UP = 1
    LEFT = 2
    DOWN = 3

class ResolutionRuleset(object):
    def transformed(self, board: 'Board', direction: 'Directions') -> "Board":
        """give transform of a board along a direction.

        Return None if the move is not legal, and the data array otherwise
        """
        return None


class BasicResolutionRuleset(ResolutionRuleset):
    def transformed(self, board: 'Board', direction: 'Directions'):
        legal = False
        if direction is Directions.DOWN:
            data = board.as_column_array(False)
        elif direction is Directions.UP:
            data = board.as_column_array(True)
        elif direction is Directions.RIGHT:
            data = board.as_line_array(False)
        elif direction is Directions.LEFT:
            data = board.as_line_array(True)
        else:
            raise RuntimeError('wrong direction')
        newdata = []
        for nib in data:
            newnib = self.transform_nib(nib)
            if any(newnib[a] != nib[a] for a in range(len(nib))):
                legal = True
            newdata.append(newnib)

        if legal:
            return board.flatten_array(newdata, direction)
        return None
    

    def transform_nib(self, nib) -> 'array':
        # first we need to push all the items to the end of the list.
        # all the empty squares will be left on the beginning
        nnib = [a for a in nib if a is None] + [a for a in nib if a is not None]
        # now we merge identical elements from the end
        pos = len(nnib) - 1
        while pos > 0:
            if nnib[pos] and nnib[pos-1] == nnib[pos]:
                nnib[pos] *= 2
                nnib[pos-1] = None
            pos -= 1
        
        # re-pack stuff
        nnib = [a for a in nnib if a is None] + [a for a in nnib if a is not None]
        return nnib
class Board(object):
    """A Board has a width, a height, a ResolutionRuleset, a random seed
    
    Initialization is part of the board mechanics and so is adding a next item
    """
    @property
    def values(self):
        return list(self._values)

    @values.setter
    def values(self, newval):
        with self._lock:
            for i, v in enumerate(newval):
                self._values[i] = v
        
    def __init__(self, width=4, height=4, resolution_ruleset: 'ResolutionRuleset'=None, seed=0):
        self._width = width
        self._height = height
        if not resolution_ruleset:
            resolution_ruleset = BasicResolutionRuleset()
        self._ruleset = resolution_ruleset
        self._seed = 0
        self._values = [None] * width * height
        self._random = random.Random()
        self._random.seed(seed)
        self._lock = threading.RLock()

    def move(self, direction):
        nextary = self._ruleset.transformed(self, direction)
        if not nextary:
            print("Illegal move {}".format(direction))
            return None
        self.values = nextary
        self.add_random_value()
    
    def up(self):
        return self.move(Directions.UP)

    def down(self):
        return self.move(Directions.DOWN)

    def left(self):
        return self.move(Directions.LEFT)

    def right(self):
        return self.move(Directions.RIGHT)

    def initialize_board(self, max_squares=2):
        """Initialize the board with a given square"""
        l = list(range(self.width * self.height))
        squares = max_squares
        while squares > 0:
            self._random.shuffle(l)
            for pos in l:
                c = self._random.choice([None, None, None, 2, 2, 2, 4])
                if c is not None:
                    with self._lock:
                        self._values[pos] = c
                        squares -= 1
                if squares == 0:
                    break
            if squares == 0:
                break
            
    def add_random_value(self, possible_values=(2, 4), count=1):
        """Add a random value to the board"""
        squares = count
        l = list(range(self.width * self.height))
        if not any(a is None for a in self.values):
            print("cannot add random value, board full")
            return
        while squares > 0:
            self._random.shuffle(l)
            for pos in l:
                if self._values[pos] is not None:
                    continue
                c = self._random.choice([None, None, None, 2, 2, 2, 4])
                if c is not None:
                    with self._lock:
                        self._values[pos] = c
                        squares -= 1
                if squares == 0:
                    break
            if squares == 0:
                break
                
    @property
    def height(self):
        return self._height
    
    @property
    def width(self):
        return self._width

    def flatten_array(self, data: '[]', direction: 'Directions') -> []:
        if direction is Directions.RIGHT:
            o = []
            for line in data:
                for item in line:
                    o.append(item)
        elif direction is Directions.LEFT:
            o = []
            for line in data:
                for item in reversed(line):
                    o.append(item)
        elif direction is Directions.DOWN:
            o = [None] * (self.width * self.height)
            for cn, column in enumerate(data):
                for ln, item in enumerate(column):
                    o[ln * self.width + cn] = item
        elif direction is Directions.UP:
            o = [None] * (self.width * self.height)
            for cn, column in enumerate(data):
                for ln, item in enumerate(reversed(column)):
                    o[ln * self.width + cn] = item
        else:
            raise RuntimeError("Bad direction")
        return o

    def as_line_array(self, reverse=False) -> []:
        """return the board represented as an array of lines
        [
            1   2   3   4
            5   6   7   8
            9   A   B   C
            D   E   F   0
        ]
        will be returned as 
        [
            [ 1 2 3 4 ],
            [ 5 6 7 8 ],
            [ 9 A B C ],
            [ D E F 0 ]
        ]
        
        each line will be reversed if reverse is True
        """
        # note: maybe use np.reshape if we find numpy useful for this project
        o = []
        for h in range(self.height):
            l = []
            for w in range(self.width):
                l.append(self._values[h * self.width + w])
            if reverse:
                l.reverse()
            o.append(l)
        return o

    def as_column_array(self, reverse=False) -> []:
        """return the board represented as an array of columns
        [
            1   2   3   4
            5   6   7   8
            9   A   B   C
            D   E   F   0
        ]
        will be returned as 
        [
            [ 1 5 9 D ],
            [ 2 6 A E ],
            [ 3 7 B F ],
            [ 4 8 C 0 ]
        ]

        each column will be reversed if reverse is True
        """
        o = []
        for w in range(self.width):
            c = []
            for h in range(self.height):
                c.append(self._values[w + h * self.width])
            if reverse:
                c.reverse()
            o.append(c)
        return o
    def format_square(self, number):
        if number is None:
            return "  --  "
        if number > 99999:
            raise RuntimeError("as of now we don't support grids with values larger than 5 numbers - aesthetics!")
        if number > 9999:
            return " {}".format(number)
        if number > 999:
            return " {} ".format(number)
        if number > 99:
            return "  {} ".format(number)
        if number > 9:
            return "  {}  ".format(number)
        return "   {}  ".format(number)

    def __str__(self):
        s = ""
        grid = self.as_line_array()
        for l in grid:
            lstr = "|".join([self.format_square(i) for i in l])
            s += lstr + "\n"
        return s
    

__all__ = ['Board', 'Directions', 'ResolutionRuleset', 'BasicResolutionRuleset']