import pandas as pd, numpy as np
import rasterio
from rasterio.windows import from_bounds
from rasterio.warp import transform
from rasterio.transform import from_origin
from geometry import interpolate_latlon

wac=r"/home/megha/arshveer/Lunar_LRO_LOLA_Global_LDEM_118m_Mar2014.tif"

coord=r"/home/megha/arshveer/ch2_iir_nci_20211218T0038037745_d_img_hw1/geometry/calibrated/20211218/ch2_iir_nci_20211218T0038037745_g_grd_hw1.csv"
'''
now perform interpolation for lat and long and get exact lat, long for each pixel
and use them to get dem coordinates
'''
def crop_dem(wac_path,coord_path):
    lat,lon=interpolate_latlon(coord_path,8673,250)
    lon=((lon+180)%360)-180
    R=1737400
    lon_rad=np.deg2rad(lon)
    lat_rad=np.deg2rad(lat)
    with rasterio.open(wac_path) as src:
        #convert 
        print("CRS:",src.crs)
#convert lat-lon to projected coordinates
        xs=R*lon_rad
        ys=R*lat_rad
        rows,cols=rasterio.transform.rowcol(src.transform,xs,ys)
        rows=np.array(rows)
        cols=np.array(cols)
        rows=rows.reshape(xs.shape)
        cols=cols.reshape(xs.shape)
        dem_resampled=np.full(xs.shape,np.nan)
        valid=(
            (rows>=0)&(rows<src.height)&
            (cols>=0)&(cols<src.width)
        )
        dem_band=src.read(1)
        dem_resampled[valid]=dem_band[rows[valid],cols[valid]]

        x=xs[0,0]
        y=ys[0,0]
        px=(xs[0,-1]-xs[0,0]/(xs.shape[1]-1))
        py=((ys[-1, 0] - ys[0, 0]) / (ys.shape[0] - 1))
        transform=from_origin(x,y,px,abs(py))
        output=r"/home/megha/arshveer/dem2.tif"
        with rasterio.open(
            output,
            'w',
            driver='GTiff',
            height=dem_resampled.shape[0],
            width=dem_resampled.shape[1],
            count=1,
            dtype=dem_resampled.dtype,
            crs=src.crs,
            transform=transform,
            ) as dst:
            dst.write(dem_resampled, 1)
    return dem_resampled
'''
        x_min,x_max=min(xs),max(xs)
        y_min,y_max=min(ys),max(ys)
        print("long: ",x_min,x_max)
        print("lat: ",y_min,y_max)
        x_m=0.1*(x_max-x_min)
        y_m=0.1*(y_max-y_min)
        x_min-=x_m
        x_max+=x_m
        y_min-=y_m
        y_max+=y_m
        print("Projected bounds: ",x_max,x_min,y_max,y_min)
'''
crop_dem(wac,coord) 
        