import tifffile as tiff
import rasterio
from rasterio.plot import show
import numpy as np
import napari

iirs=r"/home/megha/arshveer/iirs1_downsample.tif"
dem=r"/home/megha/arshveer/dem1_downsample.tif"

i=tiff.imread(iirs)
d=tiff.imread(dem)
print(i.shape)
i=i[:,:,48]
print(i.shape)
print(d.shape)
viewer=napari.Viewer()
viewer.add_image(i,name="IIRSd",colormap="terrain",opacity=1)
viewer.add_image(d,name="DEMd",colormap="terrain", opacity=0.6)
napari.run()
'''
s1=r"/home/megha/arshveer/topographhy/dem1_aspect.tif"
with rasterio.open(s1) as f:
    show(f)
'''