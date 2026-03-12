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
    '''

from scipy.io import loadmat
import matplotlib.pyplot as plt

iron=r"/home/megha/172.16.9.46:8000/Global20ppd_MLR_LPGRS_Fe.mat"
al=r"/home/megha/172.16.9.46:8000/Global20ppd_MLR_CLASS_Al.mat"
mg=r"/home/megha/172.16.9.46:8000/Global20ppd_MLR_CLASS_Mg.mat"
data=loadmat(iron)
print(data.keys())
Fe=data['Fe']
print(Fe.dtype)
print(Fe.shape)

plt.imshow(Fe,cmap="jet", vmin=0, vmax=13)
plt.colorbar()
plt.show()