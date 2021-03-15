"""p2048: a python 2048 toy project"""

from . import *
import sys
import readchar
def repl():
    b = Board()
    b.initialize_board()
    print("play with zxcv or udlr")
    while (True):
        print(b)
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
        elif command in ('q'):
            print("bye!")
            sys.exit(0)
            
repl()
