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
    """ResolutionRuleset objects apply transforms to boards

    They must not share game state with the board but rather peek and poke
    into the board state
    """
    def transform(self, board: 'Board', direction: 'Directions') -> "Board":
        """give transform of a board along a direction.

        Return None if the move is not legal, and the data array otherwise
        """
        return None


class BasicResolutionRuleset(ResolutionRuleset):
    def initialize_board(self, board, max_squares=2):
        """Initialize the board with a given square"""
        return self.add_random_value(board=board, count=max_squares)

    def add_random_value(self, board, possible_values=(None, None, None, 2, 2, 2, 4), count=1):
        """Add a random value to the board"""
        squares = count
        l = list(range(board.width * board.height))
        if len([a is None for a in board.values]) < count:
            print("cannot add random values, board too full")
            return False
        while squares > 0:
            board._random.shuffle(l)
            for pos in l:
                if board._values[pos] is not None:
                    continue
                c = board._random.choice(possible_values)
                if c is not None:
                    with board._lock:
                        board._values[pos] = c
                        squares -= 1
                if squares == 0:
                    break
            if squares == 0:
                break
        return True

    def legal_moves(self, board: 'Board'):
        """return the list of legal moves on the board"""
        out = {}
        for i in Directions:
            legal, _, scoregain = self.pre_transform(board, i)
            if legal:
                out[i] = scoregain
        return out


    def pre_transform(self, board: 'Board', direction: 'Directions'):
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
        plus_score = 0
        for nib in data:
            newnib, ps = self.transform_nib(nib)
            plus_score += ps
            if any(newnib[a] != nib[a] for a in range(len(nib))):
                legal = True
            newdata.append(newnib)
        if legal:
            return True, board.flatten_array(newdata, direction), plus_score
        return False, None, 0
                
    def transform(self, board: 'Board', direction: 'Directions'):
        legal, transformed, plus_score = self.pre_transform(board, direction)
        if legal: 
            board.values = transformed
            self.add_random_value(board, count=1)
            board.add_score(plus_score)
            
        return None
    

    def transform_nib(self, nib) -> 'array, score':
        # first we need to push all the items to the end of the list.
        # all the empty squares will be left on the beginning
        nnib = [a for a in nib if a is None] + [a for a in nib if a is not None]
        # now we merge identical elements from the end
        pos = len(nnib) - 1
        score = 0
        while pos > 0:
            if nnib[pos] and nnib[pos-1] == nnib[pos]:
                nnib[pos] *= 2
                nnib[pos-1] = None
                score += int(nnib[pos])
                
            pos -= 1
        
        # re-pack stuff
        nnib = [a for a in nnib if a is None] + [a for a in nnib if a is not None]
        return nnib, score


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
        
    def __init__(self, width=4, height=4, start_squares=2, resolution_ruleset: 'ResolutionRuleset'=None, seed=0):
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
        self._ruleset.initialize_board(self, start_squares)
        self._score = 0

    @property
    def score(self):
        return self._score

    def add_score(self, score):
        self._score += score
        
    def move(self, direction):
        self._ruleset.transform(self, direction)
    
    def get_possible_moves(self):
        m = self._ruleset.legal_moves(self)
        return m
    
    def up(self):
        return self.move(Directions.UP)

    def down(self):
        return self.move(Directions.DOWN)

    def left(self):
        return self.move(Directions.LEFT)

    def right(self):
        return self.move(Directions.RIGHT)

            
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
            s += lstr
            s += "\n" + "-" * len(lstr) + "\n"
        s += "Score: " + str(self.score) + "\n"
        return s
    

__all__ = ['Board', 'Directions', 'ResolutionRuleset', 'BasicResolutionRuleset']