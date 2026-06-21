import numpy as np
import tifffile as tif
from pathlib import Path
from chopping2 import chop
import rasterio
from downsample2 import downsample

extract=Path('/home/megha/Downloads/iirs_strips/extracted')
strips=[d for d in extract.iterdir() if d.is_dir()]
dem=r"/home/megha/arshveer/Lunar_LRO_LOLA_Global_LDEM_118m_Mar2014.tif"
ip=r"/home/megha/arshveer/dem1.tif"
op=r"/home/megha/Downloads/iirs_strips/extracted/dem1_downsample.tif"
sp=r"/home/megha/arshveer/topographhy/dem1_aspect.tif"
#with rasterio.open(dem) as src:
    #res_x,res_y=src.res

for strip in strips:
    if strip.stem=="ch2_iir_nci_20250529T1233369467_d_img_d18":
        geo=list(strip.glob('lat_lon.npy'))
        geo=geo[0]
        lat_lon=np.load(geo)
        lat=lat_lon[0]
        lon=lat_lon[1]
        #d=chop(lat,lon,dem)
        #d=downsample(ip,op,1500)
        with rasterio.open(op) as src:
            res_x,res_y=src.res
            d=src.read(1)
        dz_dy,dz_dx=np.gradient(np.nan_to_num(d),res_y,res_x)
        slope=np.degrees(np.arctan(np.sqrt(dz_dy**2 + dz_dx**2)))
        aspect_rad= np.arctan2(-dz_dx,dz_dy)
        aspect_deg=np.degrees(aspect_rad)
        aspect=(aspect_deg +360)%360

        mask=np.isnan(d)
        slope[mask]=np.nan
        aspect[mask]=np.nan

        s=extract/"downsampleslope.npy"
        a=strip/"aspect.npy"
        print("Saving files")
        #np.save(s,slope)
        #np.save(a,aspect)
        ss=tif.imread(sp)
        print("my slope", slope.shape)
        print("sachana slope",ss.shape)
        for i in range(50):
            for j in range(15):
                print("Ar. Slope: ",aspect[i][j],"\t\t","Sa. Slope: ",ss[i][j])
        print("Ar. slope max",np.max(aspect),"\t\t","Sa. slope max", np.max(ss))
        print("Ar. slope min",np.min(aspect),"\t\t","Sa. slope min", np.min(ss))       