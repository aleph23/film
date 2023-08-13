import os

PART = "L1S1"
PATH = f'~/Movies/{PART}/frames'

def rename():
    all_ = os.listdir(PATH)
    all_.sort()
    for i, f in enumerate(all_):
        os.rename(f'{PATH}/{f}', f'{PATH}/{PART}_{str(i).zfill(4)}_0001.png')

rename()
