import numpy as np
import napari
from skimage.transform import ProjectiveTransform, warp
import tifffile as tiff
from read_qub import parse_pds5_spectrum_xml, read_qub
from wac_chop import crop_dem


def register_images(iirs_cube_path, dem_path):
    # =========================
    # LOAD IIRS DATA
    # =========================
    xml=r"/home/megha/arshveer/ch2_iir_nci_20250529T1233369467_d_img_d18/data/calibrated/20250529/ch2_iir_nci_20250529T1233369467_d_img_d18.xml"
    qub=r"/home/megha/arshveer/ch2_iir_nci_20250529T1233369467_d_img_d18/data/calibrated/20250529/ch2_iir_nci_20250529T1233369467_d_img_d18.qub"
    meta=parse_pds5_spectrum_xml(xml)
    cube=read_qub(qub,meta,skip_bands=0)

    # Load IIRS cube (assumed .npy: shape = [bands, H, W])
   
  
    print("reading done")
    
    wac=r"/home/megha/arshveer/Lunar_LRO_LROC-WAC_Mosaic_global_100m_June2013 (1).tif"
    coord=r"/home/megha/arshveer/ch2_iir_nci_20250529T1233369467_d_img_d18/geometry/calibrated/20250529/ch2_iir_nci_20250529T1233369467_g_grd_d18.csv"
    
    # Load DEM (.tif)
    dem_norm = crop_dem(wac,coord)
    
    print(cube.shape)
    # Normalize for display
    #qiirs_norm = cube[]
    #dem_norm = (dem - np.min(dem)) / (np.max(dem) - np.min(dem))
    # =========================
    # OPEN NAPARI VIEWER
    # =========================
    iirs_norm=cube[48,:,:]
    print("starting viewer")
    viewer = napari.Viewer()

    viewer.add_image(iirs_norm, name="IIRS (to align)", colormap="terrain", opacity=1)
    viewer.add_image(dem_norm, name="DEM (reference)", colormap="terrain", opacity=0.6)

    print("\n👉 Instructions:")
    print("1. Add POINTS layer for IIRS → click points on IIRS image")
    print("2. Add POINTS layer for DEM → click corresponding points")
    print("3. Minimum 4 points required")
    print("4. Close viewer window when done\n")

    napari.run()

    # =========================
    # GET POINTS
    # =========================

    pts_iirs = viewer.layers["Points"].data
    pts_dem = viewer.layers["Points [1]"].data

    print("IIRS points:", pts_iirs.shape)
    print("DEM points:", pts_dem.shape)

    if len(pts_iirs) < 4:
        raise ValueError("At least 4 points required!")

    # =========================
    # COMPUTE TRANSFORM
    # =========================

    tform = ProjectiveTransform()
    tform.estimate(pts_iirs, pts_dem)

    # =========================
    # WARP IIRS
    # =========================
    bands,h,w=cube.shape
    h1,w1=dem_norm.shape #target
    al_cube=np.zeros((bands,h1,w1), dtype=np.float32)
    for b in range(bands):
        al_cube[b]=warp(
            cube[b],
            inverse_map=tform.inverse,
            output_shape=(h1,w1), 
            preserve_range=True
        )

    # =========================
    # SAVE OUTPUTS
    # =========================

    np.save("iirs1_aligned.npy", al_cube)
    np.save("projective_transform.npy", tform.params)

    print("Saved: dem_aligned.npy")
    print("Saved: projective_transform.npy")

    # =========================
    # SHOW RESULT
    # =========================

    #aligned_norm = (aligned - np.min(aligned)) / (np.max(aligned) - np.min(aligned))
    aligned_norm=al_cube[48]
    viewer = napari.Viewer()
    viewer.add_image(dem_norm, name="WAC", colormap="terrain")
    viewer.add_image(aligned_norm, name="IIRS", colormap="terrain", opacity=0.6)

    napari.run()


# =========================
# RUN
# =========================

register_images("iirs_cube.npy", "dem.npy")