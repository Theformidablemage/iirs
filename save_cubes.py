from pathlib import Path
import zipfile
from geometry import interpolate_latlon
from read_qub1 import parse_xml, read_qub
import numpy as np
import napari
from chopping2 import chop
from skimage.transform import SimilarityTransform,warp
import rasterio
R=1737400
source= Path('/home/megha/Downloads/iirs_strips')
extract=Path('/home/megha/Downloads/iirs_strips/extracted')
'''
extract.mkdir(parents=True,exist_ok=True)

for zip_path in source.glob('*.zip'):
    output=extract/zip_path.stem
    output.mkdir(exist_ok=True)
    with zipfile.ZipFile(zip_path,'r') as file:
        file.extractall(output)
        print(f"Extracted:{zip_path.name}")
'''
strips=[d for d in extract.iterdir() if d.is_dir()]      

def get_required_files(strip_path):
    data=strip_path/"data"
    geometry=strip_path/"geometry"
    print(data)

    if not data.exists() or not geometry.exists():
        raise LookupError("Data or geometry do not exist")
    xml=list(data.rglob('*.xml'))
    qub=list(data.rglob('*.qub'))
    geo=list(geometry.rglob('*.csv'))

    return xml[0],qub[0],geo[0]

def process_strips(strip):

    wac=r'/home/megha/arshveer/Lunar_LRO_LROC-WAC_Mosaic_global_100m_June2013 (1).tif'
    files=get_required_files(strip)
    xml,qub,geo=files
    #print(xml)
    meta=parse_xml(xml)
    cube=read_qub(qub,meta,skip_bands=[(28,34),(68,75),(161,256)])
    bands,lines,sample=cube.shape
    lat,lon=interpolate_latlon(geo,lines,sample)
    wac_norm=chop(cube,lat,lon,wac)
    iirs_norm=cube[48,:,:]

    
   
    '''
    viewer=napari.Viewer()
    print("Starting Viewer")
    '''
    #out=extract/f"{strip.name}_cube.npy"
    #out.parent.mkdir(parents=True,exist_ok=True)
    #np.save(out,cube)
    '''
    viewer.add_image(iirs_norm,name="IIRS image",colormap="terrain",opacity=1)
    viewer.add_image(wac_norm,name="WAC",colormap="terrain",opacity=0.5)
    viewer = napari.Viewer()
    '''
# -------------------------
# ADD IMAGES
# -------------------------
  
    viewer=napari.Viewer()
    viewer.add_image(iirs_norm, name="IIRS", colormap="terrain")
    viewer.add_image(wac_norm, name="WAC", colormap="terrain", opacity=0.5)

# -------------------------
# ADD POINT LAYERS
# -------------------------
    pts_iirs = viewer.add_points(name="IIRS_points", face_color="red", size=8)
    pts_wac = viewer.add_points(name="WAC_points", face_color="blue", size=8)
    pts_iirs.mode = "add"
    pts_wac.mode = "add"
    print("\n Instructions:")
    print("1. Click crater in IIRS (red points)")
    print("2. Click SAME crater in WAC (blue points)")
    print("3. Check terminal for lat/lon shift\n")
      
    iirs_pts=[]
    wac_pts=[]
    last_idx=-1
# -------------------------
# COMPUTE SHIFT 
# -------------------------
    def compute_shift(event):
    # need at least one point in both
        nonlocal last_idx
        print("EVENt triggered")
        if len(pts_iirs.data) == 0 or len(pts_wac.data) == 0:
             return

    # take latest points
        #r_iirs, c_iirs = pts_iirs.data[-1]
        #r_wac, c_wac = pts_wac.data[-1]

        idx=len(pts_wac.data)-1
        if idx==last_idx:
             return
        last_idx=idx
        if idx>=len(pts_iirs.data):
             print("Click iirs points")
             return
        r_iirs, c_iirs = pts_iirs.data[idx]
        r_wac, c_wac = pts_wac.data[idx]
        print(f"Pairing index: {idx}")

        r_iirs, c_iirs = int(r_iirs), int(c_iirs)
        r_wac, c_wac = int(r_wac), int(c_wac)

    # -------------------------
    # IIRS lat/lon
    # -------------------------
        if r_iirs >= lat.shape[0] or c_iirs >= lat.shape[1]:
                print("IIRS click out of bounds")
                return

        if r_wac >= lat.shape[0] or c_wac >= lat.shape[1]:
                 print("WAC click out of bounds")
                 return

        lat_iirs = lat[r_iirs, c_iirs]
        lon_iirs = lon[r_iirs, c_iirs]

        lat_wac = lat[r_wac, c_wac] 
        lon_wac = lon[r_wac, c_wac]
        
      


    # -------------------------
    # PRINT RESULTS
    # -------------------------
        print("\n New Point Pair")
        print(f"IIRS Pixel: ({r_iirs}, {c_iirs})")
        print(f"WAC  Pixel: ({r_wac}, {c_wac})")

        print(f"IIRS → Lat: {lat_iirs:.6f}, Lon: {lon_iirs:.6f}")
        print(f"WAC  → Lat: {lat_wac:.6f}, Lon: {lon_wac:.6f}")

        print(f"shift Lat: {lat_iirs - lat_wac:.6f}")
        print(f"shift Lon: {lon_iirs - lon_wac:.6f}")
        iirs_pts.append([c_iirs,r_iirs])
        wac_pts.append([c_wac,r_wac])

# -------------------------
# CONNECT EVENTS
# -------------------------
    #pts_iirs.events.data.connect(compute_shift)
    pts_wac.events.data.connect(compute_shift)

    napari.run()

    print("Now computing transform")
    iirs_pts_ar=np.array(iirs_pts)
    wac_pts_ar=np.array(wac_pts)

    if len(iirs_pts_ar)<4:
         raise ValueError("Points less than 4")
    tform=SimilarityTransform()
    tform.estimate(iirs_pts_ar,wac_pts_ar)
    print("Tranformation matrix:\n",tform.params)
    h_out,w_out=wac_norm.shape
    co_cube=np.zeros((bands,h_out,w_out),dtype=np.float32)
    #warping full cube

    for b in range(bands):
         co_cube[b]=warp(
              cube[b],
              inverse_map=tform.inverse,
              output_shape=(h_out,w_out),
              preserve_range=True,
              cval=np.nan
         )

    lat_new=warp(
         lat,
         inverse_map=tform.inverse,
         output_shape=(h_out,w_out),
         preserve_range=True,
         cval=np.nan
    )
    lon_new=warp(
         lon,
         inverse_map=tform.inverse,
         output_shape=(h_out,w_out),
         preserve_range=True,
         cval=np.nan
    )
    lat_lon=np.stack([lat_new,lon_new],axis=0)
    print("Lat new:",lat_new[60,60])
    print("Lon new:",lon_new[60,60])
    print("lat:",lat_new[200,100])
    print("lon:",lon_new[200,100])
    
   
    out_cube=extract/f"{strip.name}_aligned.npy"
    out_coord=extract/f"{strip.name}_lat_lon.npy"

    np.save(out_cube,co_cube)
    np.save(out_coord,lat_lon)
    viewer=napari.Viewer()
    viewer.add_image(wac_norm,name="WAC",colormap="terrain")
    viewer.add_image(co_cube[48],name="Aligned IIRS",colormap="terrain")

    napari.run()
    del cube

for strip in strips:
    if strip.stem == "ch2_iir_nci_20230701T1834098296_d_img_d32" or strip.stem == "ch2_iir_nci_20230707T2120194723_d_img_d32" :
        #continue
        process_strips(strip)


    

