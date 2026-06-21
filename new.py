import numpy as np
import napari
import spectral as sp
from chop3 import chop
from read_qub1 import parse_xml,read_qub
import matplotlib.pyplot as plt

wac=r"/home/megha/arshveer/Lunar_LRO_LROC-WAC_Mosaic_global_100m_June2013 (1).tif"
hdr=r"/home/megha/Downloads/iirs_strips/ch2_iir_ndi_20230707T2126184264_d_rfl_n18_srd/data/derived/20230707/ch2_iir_ndi_20230707T2126184264_d_loc_n18_ard.hdr"
h2=r"/home/megha/Downloads/iirs_strips/ch2_iir_ndi_20230420T0648107017_d_rfl_d32_srd/data/derived/20230420/ch2_iir_ndi_20230420T0648107017_d_loc_d32_ard.hdr"
#iirs=r"/home/megha/Downloads/iirs_strips/extracted/ch2_iir_nci_20230707T2126184264_d_img_d32/ch2_iir_nci_20230707T2126184264_d_img_d32_aligned.npy"
#geo=r"/home/megha/Downloads/iirs_strips/extracted/ch2_iir_nci_20230707T2126184264_d_img_d32/lat_lon.npy"
xml=r"/home/megha/Downloads/iirs_strips/ch2_iir_ndi_20230707T2126184264_d_rfl_n18_srd/data/derived/20230707/ch2_iir_ndi_20230707T2126184264_d_rfl_n18_srd.xml"
i=r"/home/megha/Downloads/iirs_strips/ch2_iir_ndi_20230707T2126184264_d_rfl_n18_srd/data/derived/20230707/ch2_iir_ndi_20230707T2126184264_d_rdn_n18_ard.qub"
x2=r"/home/megha/Downloads/iirs_strips/ch2_iir_ndi_20230420T0648107017_d_rfl_d32_srd/data/derived/20230420/ch2_iir_ndi_20230420T0648107017_d_rfl_d32_srd.xml"
i2=r"/home/megha/Downloads/iirs_strips/ch2_iir_ndi_20230420T0648107017_d_rfl_d32_srd/data/derived/20230420/ch2_iir_ndi_20230420T0648107017_d_rdn_d32_ard.qub"
img=sp.open_image(h2)
coord=img.load()
print(coord.shape)
long=coord[:,:,0]
lat=coord[:,:,1]
long=long.squeeze(axis=2)
lat=lat.squeeze(axis=2)
print(long.shape,lat.shape)
#meta=parse_xml(xml)
#c=read_qub(i,meta,skip_bands=[(28,34),(68,75),(161,256)])
#c=c[48,:,:]
der_x=r"/home/megha/Downloads/iirs_strips/extracted/ch2_iir_nci_20230420T0648107017_d_img_d32/data/calibrated/20230420/ch2_iir_nci_20230420T0648107017_d_img_d32.xml"
qub=r"/home/megha/Downloads/iirs_strips/extracted/ch2_iir_nci_20230420T0648107017_d_img_d32/data/calibrated/20230420/ch2_iir_nci_20230420T0648107017_d_img_d32.qub"
#cal=np.load(der)
#cl=cal[48,:,:]
#meta=parse_xml(der_x)
#cal=read_qub(qub,meta,skip_bands=0)
meta=parse_xml(x2)
c1=read_qub(i2,meta,skip_bands=0)
cube=c1[48,:,:]
#c=c[200:800,50:200]
#lat=lat[200:800,50:200]
#long=long[200:800,50:200]
#lat_long=np.load(geo)
#lat=lat_long[0,:,:]
#long=lat_long[1,:,:]
#c=np.load(iirs)
#c=c[48,:,:]
#print(c.shape)
#print(np.nanmin(lat),np.nanmax(lat))
#print(np.nanmin(long), np.nanmax(long))
#print(lat[0,:100])
#print(long[0,:100])
w=chop(cube,lat,long,wac)
viewer=napari.Viewer()
viewer.add_image(cube,name="IIRS_derived",colormap="terrain",opacity=1)
viewer.add_image(w,name="Wac",colormap="terrain",opacity=0.6)
napari.run()
'''
b,r,c=cal.shape
b=np.arange(b)
cal1=cal[:,2000,200]
c1=c1[:,2000,200]
plt.figure()
plt.plot(b,cal1,color='red',label='Spectrum of a pixel from calibrated file')
plt.xlabel("Bands")
plt.ylabel("Radiance")
plt.title("Comparing spectrum from derived and calibrated files of same pixel")
plt.legend()
plt.show()

plt.figure()
plt.plot(b,c1,color='green',label='Spectrum of a pixel from derived file')
plt.xlabel("Bands")
plt.ylabel("Radiance")
plt.title("Derived")
plt.show()

angles=r"/home/megha/Downloads/iirs_strips/ch2_iir_ndi_20230707T2126184264_d_rfl_n18_srd/data/derived/20230707/ch2_iir_ndi_20230707T2126184264_d_obs_n18_ard.hdr"

data=sp.open_image(angles)
a=data.load()
az=a[:,:,0]
print("Across entire array:",np.nanmax(az),np.nanmin(az))
print(az.shape)
az=az.squeeze(axis=2)
#print("Row: ",az[50,:])
#print("Column: ",az[:,50])
#print("Along columns:",np.nanmax(az,axis=0),np.nanmin(az,axis=0))
#print("Along rows:",np.nanmax(az,axis=1),np.nanmin(az,axis=1))
'''