from scipy.io import loadmat
import numpy as np
from skimage.transform import resize
from pathlib import Path
from maps_preprocessing import lookup_map_values
from chopping2 import chop
import napari

fe=r"/home/megha/172.16.9.46:8000/Global20ppd_MLR_LPGRS_Fe.mat"
mg=r"/home/megha/172.16.9.46:8000/Global20ppd_MLR_CLASS_Mg.mat"
al=r"/home/megha/172.16.9.46:8000/Global20ppd_MLR_CLASS_Al.mat"

dem=r"/home/megha/arshveer/Lunar_LRO_LOLA_Global_LDEM_118m_Mar2014.tif"
omat=r"/home/megha/Downloads/Lunar_Kaguya_MIMap_MineralDeconv_OpticalMaturityIndex_50N50S.tif"
extract=Path('/home/megha/Downloads/iirs_strips/extracted')
strips=[d for d in extract.iterdir() if d.is_dir()]
data=loadmat(fe)
d_i=data['Fe']
'''
data=loadmat(iron)
#print(data.keys())
#g=data['__version__']
#print(g)
for name, path in paths.items():
    mat=loadmat(path)
    print(name,mat.keys())
    data=mat[name]
    op=f"{name}.tif"
    with rasterio.open(
        op,
        "w",
        driver="GTiff",
        height=data.shape[0],
        width=data.shape[1],
        count=1,
        dtype=data.dtype
    ) as dst:
        dst.write(data, 1)

    print(f"{name} saved")
'''

def downscale(cube,lat,lon,cur_res,tar_res):
    b,h,w=cube.shape
    scale=tar_res/cur_res
    new_h=int(h/scale)
    new_w=int(w/scale)
    cube_n=resize(
        cube,
        (b,new_h,new_w),
        order=1,
        anti_aliasing=True,
        preserve_range=True
    )
    lat_n=resize(
        lat,
        (new_h,new_w),
        order=1,
        anti_aliasing=True,
        preserve_range=True
    )
    lon_n=resize(
        lon,
        (new_h,new_w),
        order=1,
        anti_aliasing=True,
        preserve_range=True
    )
    return cube_n,lat_n,lon_n



for strip in strips:
    if strip.stem == "ch2_iir_nci_20250529T1233369467_d_img_d18" or strip.stem == "ch2_iir_nci_20211218T0038037745_d_img_hw1":
        continue  
    print(strip)
    geo=list(strip.glob('lat_lon.npy'))
    c=list(strip.glob('*aligned.npy'))
    geo=geo[0]
    c=c[0]
    cube=np.load(c)
    lat_lon=np.load(geo)
    lat=lat_lon[0]
    lon=lat_lon[1]
    #v=np.unique(lat,axis=1)
    #print(v)
    cube,lat,lon=downscale(cube,lat,lon,80,140)
    i=lookup_map_values(d_i,lat,lon,-75,75,0,360)#arrays of maps corresponding to the particular iirs strip
    m=lookup_map_values(d_m,lat,lon,-85,85,0,360)
    a=lookup_map_values(d_a,lat,lon,-85,85,0,360)                    
    #o=chop(lat,lon,omat)                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  
    d=chop(lat,lon,dem)
    iirs=cube[48,:,:]
    viewer=napari.Viewer()
    viewer.add_image(iirs,name="IIRSd",colormap="terrain",opacity=1)
    viewer.add_image(d,name="DEMd",colormap="terrain", opacity=0.6)
    napari.run()
