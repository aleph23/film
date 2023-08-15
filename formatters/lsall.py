import os
import sys

PART = sys.argv[1]; assert len(PART) == 4, "Invalid arg"

def lsall(_dir):
    all_ = os.listdir(_dir)
    all_.sort()
    for f in all_:
        print(f)

lsall(f'../../Movies/{PART}/frames')
