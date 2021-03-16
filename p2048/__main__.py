"""p2048: a python 2048 toy project"""

from . import *
import sys
import readchar
import random
random.seed()
def repl():
    b = Board()
    print("""play with arrows/zxcv and
            p: print board
            s: start a new game with a random seed
            q: quit game""")
    while (True):
        print(b)
        lm = b.get_possible_moves()
        if len(lm) == 0:
            print("no possible moves left. game over :( press s for a new game")
        else:
            print("Possible moves", lm)
        command = readchar.readkey()
        if command in (readchar.key.UP, 'c'):
            b.up()
        elif command in (readchar.key.DOWN, "x"):
            b.down()
        elif command in (readchar.key.LEFT, "c"):
            b.left()
        elif command in (readchar.key.RIGHT, "v"):
            b.right()
        elif command in ('p'):
            print(b)
        elif command in ('s'):
            seed = random.randint(0, sys.maxsize)
            print("New game using seed", seed)
            b = Board(seed=seed)
            print("enjoy")
        elif command in ('q'):
            print("bye!")
            sys.exit(0)
            
repl()
