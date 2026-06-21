import numpy as np
from pathlib import Path

def compute_shift(a_cube):
    mask=~np.isnan(a_cube)
    rows_valid=np.any(mask,axis=1)

    #counting nans from top
    top_nan=0
    for v in rows_valid:
        if v:
            break
        top_nan+=1
        print(top_nan)

    #counting nans from bottom
    bot_nan=0
    for v in rows_valid[::-1]:
        if v:
            break
        bot_nan+=1
        print(bot_nan)

    dy=bot_nan-top_nan
    return dy, mask

#def apply_shift(dy,mask):
    

extract=Path('/home/megha/Downloads/iirs_strips/extracted')
strips=[d for d in extract.iterdir() if d.is_dir()]

for strip in strips:
    print(strip)
    c=list(strip.glob('*aligned.npy'))
    c=c[0]
    cube=np.load(c)
    cube=cube[48,:,:]
    dy,mask=compute_shift(cube)
    print(dy)
    print("one strip done")