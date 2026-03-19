import numpy as np
import tifffile as tif

s1=r"/home/megha/arshveer/topographhy/dem1_slope.tif"

sl1=tif.imread(s1)
print(sl1.shape)
f=5
flat_mask=(sl1<=f)&(~np.isnan(sl1))
ind=np.where(flat_mask)
pix=list(zip(ind[0],ind[1]))
print(len(pix))
#now get rugged pixels around neighbouring flat pixels
r=15
rug_mask=(sl1>=r)&(~np.isnan(sl1))
indr=np.where(rug_mask)
rp=list(zip(indr[0],indr[1]))
print(len(rp))

#read the maps now to filter the pairings




