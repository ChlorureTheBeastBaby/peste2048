"""p2048: a python 2048 toy project"""

from . import *
import sys
def repl():
    b = Board()
    b.initialize_board()
    print("play with zxcv or udlr")
    while (True):
        command, *a = input("(u,d,l,r,p,q) >").split(" ")
        command = command.lower()
        if command in ("u", "c"):
            b.up()
            print(b)
        elif command in ("d", "x"):
            b.down()
            print(b)
        elif command in ("l", "z"):
            b.left()
            print(b)
        elif command in ("r", "v"):
            b.right()
            print(b)
        elif command in ('p'):
            print(b)
        elif command in ('q'):
            print(b)
            print("bye!")
            sys.exit(0)
            
repl()