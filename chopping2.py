import numpy as np
import rasterio
from skimage.transform import resize


def chop(lat,lon,wac):
    R=1737400
    lon=((lon+180)%360)-180
    lat_rad=np.deg2rad(lat)
    lon_rad=np.deg2rad(lon)
    xs=R*lon_rad
    ys=R*lat_rad
  
    h,w=xs.shape
    #valid_geo= (
    #    ~np.isnan(xs)&
    #    ~np.isnan(ys)
    #)
    #xs=xs[valid_geo]
    #ys=ys[valid_geo]
    with rasterio.open(wac,'r') as src:
        print("CRS",src.crs)
        rows,cols=rasterio.transform.rowcol(src.transform,xs,ys)
        rows=np.array(rows)
        cols=np.array(cols)
        rows=rows.reshape(xs.shape)
        cols=cols.reshape(xs.shape)
        dem_resampled=np.full((h,w),np.nan)
        #temp=np.full(xs.shape,np.nan)
        valid=(
            (rows>=0)&(rows<src.height)&
            (cols>=0)&(cols<src.width)
        )
        
        
        dem_band=src.read(1)
        dem_resampled[valid]=dem_band[rows[valid],cols[valid]]
        #dem_resampled[valid_geo]=temp
        print("WAC shape: ",dem_resampled.shape)
    return dem_resampled

