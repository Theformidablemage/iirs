import numpy as np
from scipy.io import loadmat
import tifffile as tif
from read_qub import parse_pds5_spectrum_xml, read_qub
from geometry import interpolate_latlon
from maps_preprocessing import lookup_map_values
from extract_pixels import extract_pairs_with_coords

iron=r"/home/megha/172.16.9.46:8000/Global20ppd_MLR_LPGRS_Fe.mat"
Al=r"/home/megha/172.16.9.46:8000/Global20ppd_MLR_CLASS_Al.mat"
Mg=r"/home/megha/172.16.9.46:8000/Global20ppd_MLR_CLASS_Mg.mat"
xml=r"/home/megha/arshveer/ch2_iir_nci_20211218T0038037745_d_img_hw1/data/calibrated/20211218/ch2_iir_nci_20211218T0038037745_d_img_hw1.xml"
qub=r"/home/megha/arshveer/ch2_iir_nci_20211218T0038037745_d_img_hw1/data/calibrated/20211218/ch2_iir_nci_20211218T0038037745_d_img_hw1.qub"
coord=r"/home/megha/arshveer/ch2_iir_nci_20211218T0038037745_d_img_hw1/geometry/calibrated/20211218/ch2_iir_nci_20211218T0038037745_g_grd_hw1.csv"
s=r"/home/megha/arshveer/topographhy/dem2_slope.tif"
i=loadmat(iron)
fe=i['Fe']
fe[fe>25]=np.nan
m=loadmat(Mg)
mg=m['Mg']
a=loadmat(Al)
al=a['Al']
al[al<0]=np.nan
slope=tif.imread(s)
meta=parse_pds5_spectrum_xml(xml)
cube=read_qub(qub,meta,skip_bands=0)
b,h,w=cube.shape
lat_grid,lon_grid=interpolate_latlon(coord,h,w)
fe_map=lookup_map_values(fe,lat_grid,lon_grid,-75,75,0,360)
al_map=lookup_map_values(al*100,lat_grid,lon_grid,-85,85,0,360)
mg_map=lookup_map_values(mg*100,lat_grid,lon_grid,-85,85,0,360)
rug,flat,rug_lat,rug_lon,flat_lat,flat_lon=extract_pairs_with_coords(slope,fe_map,mg_map,al_map,cube,lat_grid,lon_grid,7,5,15,0.0014)
print(rug.shape)
print(flat.shape)
