import os

def lsall(_dir):
    all_ = os.listdir(_dir)
    all_.sort()
    for f in all_:
        print(f)

lsall("~/Movies/L1S1/frames")
