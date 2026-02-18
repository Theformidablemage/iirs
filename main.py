from read_qub import parse_pds5_spectrum_xml, read_qub
from thermal import thermal_corrector_np
from geometry import interpolate_latlon
from conversion import convert_refl
from clustering import clustering_pipeline
import numpy as np
import os

os.system('cls')
extract_folder = r"D:\ch2_iir_nci_20210720T2333026105_d_img_d32"  #Apollo data
data_dir = os.path.join(extract_folder, "data")

xml_file, qub_file = None, None

for root, _, files in os.walk(data_dir):
    for f in files:
        if f.endswith(".xml") and xml_file is None:
            xml_file = os.path.join(root, f)
        elif f.endswith(".qub") and qub_file is None:
            qub_file = os.path.join(root, f)

meta = parse_pds5_spectrum_xml(xml_file)
cube = read_qub(qub_file, meta, skip_bands=77)
cube=cube[:-2]
bands,lines,samples=cube.shape

print(cube.min())

geometry_csv=r"D:\ch2_iir_nci_20210720T2333026105_d_img_d32\geometry\calibrated\20210720\ch2_iir_nci_20210720T2333026105_g_grd_d32.csv"

lat_grid,lon_grid=interpolate_latlon(geometry_csv,lines,samples)
polar=lat_grid<=-60

#for clustering for a subset of data to match with prabhakar
H,W=polar.shape

size=30
half=size//2
center_h,center_w=H//2,W//2
wind_mask=np.zeros((H,W),dtype=bool)
wind_mask[
    center_h - half:center_h + half,
    center_w - half:center_w + half

]=True
combined_mask=polar  #only polar mask for mission data
#-------------

wavelengths = np.loadtxt(r"D:\Downloads\Solar.txt",usecols=0)
print(wavelengths.shape)
corrected_cube,temperature_map = thermal_corrector_np(
    cube,
    wavelengths,
    emissivity=0.95,
    save_path=r"D:/new_pipeline/new.npz"
)
#new lat-long mask for apollo data to compare results
lat_mask=(lat_grid>=-10)&(lat_grid<=-8)
lon_mask=(lon_grid>=15)&(lon_grid<=17)
cor_mask=lat_mask&lon_mask



ref_cube=convert_refl(corrected_cube,
                      path_solarflux=r"D:\Downloads\Solar.txt",
                      mask=cor_mask,
                      save_path=r"ref.npz"
)

cluster_img,labels,centers=clustering_pipeline(ref_cube,wavelengths,mask=None,n_clusters=4)