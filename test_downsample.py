import tifffile as tiff
import rasterio
from rasterio.plot import show
import numpy as np
import napari
from geometry import interpolate_latlon
from chopping2 import chop

iirs=r"//home/megha/Downloads/iirs_strips/extracted/ch2_iir_nci_20230707T2126184264_d_img_d32/ch2_iir_nci_20230707T2126184264_d_img_d32_cube.npy"
wac=r"/home/megha/arshveer/Lunar_LRO_LROC-WAC_Mosaic_global_100m_June2013 (1).tif"
geo=r"/home/megha/Downloads/iirs_strips/extracted/ch2_iir_nci_20230707T2126184264_d_img_d32/geometry/calibrated/20230707/ch2_iir_nci_20230707T2126184264_g_grd_d32.csv"
cube=np.load(iirs)
i=cube[48,:,:]
h,w=i.shape
lat,lon=interpolate_latlon(geo,h,w)
d=chop(lat,lon,wac)
viewer=napari.Viewer()

viewer.add_image(i,name="IIRS_calibrated",colormap="terrain",opacity=1)
viewer.add_image(d,name="WAC",colormap="terrain", opacity=0.6)
napari.run()
'''
s1=r"/home/megha/arshveer/topographhy/dem1_aspect.tif"
with rasterio.open(s1) as f:
    show(f)
'''