import numpy as np
import pandas as pd
from pathlib import Path
from chopping2 import chop
import napari
from geometry import interpolate_latlon

extract=Path('/home/megha/Downloads/iirs_strips/extracted')
strips=[d for d in extract.iterdir() if d.is_dir() ]
dem=r"/home/megha/arshveer/Lunar_LRO_LOLA_Global_LDEM_118m_Mar2014.tif"
wac=r'/home/megha/arshveer/Lunar_LRO_LROC-WAC_Mosaic_global_100m_June2013 (1).tif'
'''
def get_files(strip_path):
    geo=strip_path/"geometry"
    coord=list(geo.rglob('*.csv'))
    return coord[0]

for strip in strips:
    coord=get_files(strip)
    c=pd.read_csv(coord,usecols=[0,1])
    long=c.iloc[:,0].values
    lat=c.iloc[:,1].values
    print("Max Lat :",np.max(lat),"\t\tMin Lat :",np.min(lat))
    print("Max Lon :",np.max(long),"\t\tMin Lon :",np.min(long))
'''
for strip in strips:
    if strip.stem=="ch2_iir_nci_20250529T1233369467_d_img_d18" or strip.stem== "ch2_iir_nci_20211218T0038037745_d_img_hw1":
        continue
    print(strip)
    
    cube=list(strip.glob('*aligned.npy'))
    #c=list(strip.glob('*cube.npy'))
    print("Aligned:",cube)
    cube=cube[0]
    cube=np.load(cube)
    i=cube[48,:,:]
    h,w=i.shape[-2:]
    print(h,w)
    geo=list(strip.glob('*lat_lon.npy'))
    geo=geo[0]
    lat_lon=np.load(geo)
    lat=lat_lon[0]
    lon=lat_lon[1]
    #geo=strip/"geometry"
    #csv=list(geo.rglob('*.csv'))
    #csv=csv[0]
    #lat,lon=interpolate_latlon(csv,h,w)
    #print("Org. lat :",lat.shape)
    #np.savetxt(s, lat, fmt="%.6f")
    #d=chop(lat,lon,dem)
    #lat[np.isnan(i)]=np.nan
    #lon[np.isnan(i)]=np.nan
    w=chop(lat,lon,wac)
    #lat_lon=np.stack([lat,lon],axis=0)
    #path=strip/"lat_lon.npy"
    #np.save(path,lat_lon)
    viewer=napari.Viewer()
    viewer.add_image(i,name="IIRSd",colormap="terrain",opacity=1)
    viewer.add_image(w,name="wac",colormap="terrain", opacity=0.6)
    napari.run()
    '''
    for i in range(200):
       for j in range(100):
          print(lat[i,j])
    '''


