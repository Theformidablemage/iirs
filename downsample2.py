import pandas as pd, numpy as np
import rasterio
from rasterio.windows import from_bounds
from rasterio.warp import transform
from rasterio.transform import from_origin
from rasterio.enums import Resampling
from geometry import interpolate_latlon
from read_qub import parse_pds5_spectrum_xml, read_qub

wac=r"/home/megha/arshveer/Lunar_LRO_LROC-WAC_Mosaic_global_100m_June2013 (1).tif"

coord=r"/home/megha/Downloads/iirs_strips/extracted/ch2_iir_nci_20230707T2126184264_d_img_d32/geometry/calibrated/20230707/ch2_iir_nci_20230707T2126184264_g_grd_d32.csv"
'''
now perform interpolation for lat and long and get exact lat, long for each pixel
and use them to get dem coordinates
'''
def crop_dem(wac_path,coord_path):
    xml=r"/home/megha/Downloads/iirs_strips/extracted/ch2_iir_nci_20230707T2126184264_d_img_d32/data/calibrated/20230707/ch2_iir_nci_20230707T2126184264_d_img_d32.xml"
    qub=r"/home/megha/Downloads/iirs_strips/extracted/ch2_iir_nci_20230707T2126184264_d_img_d32/data/calibrated/20230707/ch2_iir_nci_20230707T2126184264_d_img_d32.qub"
    meta=parse_pds5_spectrum_xml(xml)
    cube=read_qub(qub,meta,skip_bands=0)
    b,l,s=cube.shape
    lat,lon=interpolate_latlon(coord_path,l,s)
    lon=((lon+180)%360)-180
    R=1737400
    lon_rad=np.deg2rad(lon)
    lat_rad=np.deg2rad(lat)
    with rasterio.open(wac_path) as src:
        #convert 
        c=src.crs
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
        print(dem_resampled.shape)
        x=xs[0,0]
        y=ys[0,0]
        px=((xs[0,-1]-xs[0,0])/(xs.shape[1]-1))
        py=((ys[-1, 0] - ys[0, 0]) / (ys.shape[0] - 1))
        transform=from_origin(x,y,px,abs(py))
        output=r"/home/megha/arshveer/dem3.tif"
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
            #save iirs as tif and then downsample it
            o=r"/home/megha/arshveer/iirs3.tif"
            with rasterio.open(
                o,
                'w',
                driver='GTiff',
                height=cube.shape[1],
                width=cube.shape[2],
                count=cube.shape[0],
                dtype=cube.dtype,
                crs=c,
                transform=transform
            ) as dst:
                dst.write(cube)
        
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

def downsample(ip,ou,tar=1500):
    with rasterio.open(ip) as src:
        res_x,res_y=src.res
        print("res: ",res_x,res_y)
        scale_x=tar/res_x
        scale_y=tar/res_y
        new_width=int(src.width/scale_x)
        new_height=int(src.height/scale_y)
        new_transform=src.transform*src.transform.scale(
            (src.width/new_width),
            (src.height/new_height)                                         
        )
        data=src.read(
            out_shape=(
                src.count,
                new_height,
                new_width
            ),
            resampling=Resampling.average
        )
        #write downsampled tif file
        with rasterio.open(
            ou,
            'w',
            driver='GTiff',
            height=new_height,
            width=new_width,
            count=src.count,
            dtype=data.dtype,
            crs=src.crs,
            transform=new_transform
        ) as dst:
            dst.write(data)
            print(data.shape)
    return data

crop_dem(wac,coord) 
ip=r"/home/megha/arshveer/dem3.tif"
ou=r"/home/megha/arshveer/dem3_downsample.tif"

downsample(ip,ou,tar=1500)
      