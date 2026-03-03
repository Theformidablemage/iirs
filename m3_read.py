'''
print("here")

import spectral,matplotlib.pyplot as plt

hdr=r"/home/megha/172.16.9.47:8000/fmReflCalibTotal_single.hdr"

img=spectral.open_image(hdr)
data=img.load()

print(data.shape)
print(data.dtype)
print("done")

plt.imshow(data[:,:,70], cmap="gray")
plt.show()
'''
p=r"/home/megha/172.16.9.47:8000/fmReflCalibTotal_single.img"
import rasterio
src = rasterio.open(p)
print(src.crs)
print(src.transform) 


import h5py,matplotlib.pyplot as plt, numpy as np

mat_file = r"/home/megha/172.16.9.47:8000/fmReflCalibTotal_single.mat"
with h5py.File(mat_file,'r') as f:
    root = f['fmReflCalibTotal_single']
    print(root.shape)
    print(root.dtype)
    data=root[:]
    print(np.isnan(data).sum())
    print(data.shape)
    print(np.nanmin(data), np.nanmax(data))
    plt.plot(np.sum(np.isnan(data[:,:,0]), axis=1))