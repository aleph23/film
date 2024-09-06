import os
import sys

PART = sys.argv[1]; assert len(PART) #== 4, "Invalid arg"
_PATH = sys.argv[2]; assert len(_PATH) # > 0, "Invalid path"
PATH = f'{_PATH}/{PART}/frames'

def lsall(_dir):
    all_ = os.listdir(_dir)
    all_.sort()
    for f in all_:
        print(f)

lsall(PATH)
