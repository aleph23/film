import os
import sys

PART = sys.argv[1]; assert len(PART) == 4, "Invalid arg"
_PATH = sys.argv[2]; assert len(_PATH) > 0, "Invalid path"
PATH = f'{_PATH}/{PART}/frames'

def rename():
    all_ = os.listdir(PATH)
    all_.sort()
    for i, f in enumerate(all_):
        os.rename(f'{PATH}/{f}', f'{PATH}/{PART}_{str(i).zfill(4)}_0001.png')

rename()
