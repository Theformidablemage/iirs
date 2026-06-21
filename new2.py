import napari
import numpy as np
from chop3 import chop
import spectral as sp
from read_qub1 import parse_xml, read_qub
from scipy.interpolate import RBFInterpolator
import rasterio
#from chopping2 import chop
# -----------------------------------
# YOUR IMAGES
# -----------------------------------
# iirs_norm  -> IIRS strip
# wac_norm   -> cropped WAC
wac=r"/home/megha/arshveer/Lunar_LRO_LROC-WAC_Mosaic_global_100m_June2013 (1).tif"
hdr=r"/home/megha/Downloads/iirs_strips/ch2_iir_ndi_20230707T2126184264_d_rfl_n18_srd/data/derived/20230707/ch2_iir_ndi_20230707T2126184264_d_loc_n18_ard.hdr"
xml=r"/home/megha/Downloads/iirs_strips/ch2_iir_ndi_20230707T2126184264_d_rfl_n18_srd/data/derived/20230707/ch2_iir_ndi_20230707T2126184264_d_rfl_n18_srd.xml"
i=r"/home/megha/Downloads/iirs_strips/ch2_iir_ndi_20230707T2126184264_d_rfl_n18_srd/data/derived/20230707/ch2_iir_ndi_20230707T2126184264_d_rdn_n18_ard.qub"
geo=r"/home/megha/Downloads/iirs_strips/extracted/ch2_iir_nci_20230420T0648107017_d_img_d32/geometry/calibrated/20230420/ch2_iir_nci_20230420T0648107017_g_grd_d32.csv"
img=sp.open_image(hdr)
coord=img.load()
print(coord.shape)
long=coord[:,:,0]
lat=coord[:,:,1]
long=long.squeeze(axis=2)
lat=lat.squeeze(axis=2)
meta=parse_xml(xml)
c1=read_qub(i,meta,skip_bands=0)
cube=c1[48,:,:]
h,w=cube.shape
#lat,long=interpolate_latlon(geo,h,w)
wac_norm=chop(cube,lat,long,wac)

w_t=[0,w+100]
viewer = napari.Viewer()
with rasterio.open(wac) as src:

    wac_img = src.read(1)

    transform = src.transform
    crs = src.crs

    print("WAC CRS:")
    print(crs)
# -----------------------------------
# ADD WAC
# fixed reference image
# -----------------------------------
viewer.add_image(
    wac_norm,
    name="WAC",
    colormap="terrain",
    translate=w_t
)

# -----------------------------------
# ADD IIRS
# movable overlay
# -----------------------------------
iirs_layer = viewer.add_image(
    cube,
    name="IIRS",
    colormap="gray",
    opacity=0.5
)


# ============================================================
# DISPLAY SIDE-BY-SIDE
# ============================================================


# ============================================================
# POINT LAYERS
# ============================================================

pts_iirs = viewer.add_points(
    name="IIRS_points",
    face_color="red",
    size=10
)

pts_wac = viewer.add_points(
    name="WAC_points",
    face_color="blue",
    size=10
)

pts_iirs.mode = "add"
pts_wac.mode = "add"

print("\nInstructions:")
print("1. Click point in IIRS")
print("2. Click SAME point in WAC")
print("3. Repeat for ~20-40 points")
print("4. Close napari when done\n")

# ============================================================
# POINT COLLECTION
# ============================================================

last_idx = -1

iirs_pts = []
wac_pts = []

def collect_points(event):

    global last_idx

    if len(pts_iirs.data) == 0:
        return

    if len(pts_wac.data) == 0:
        return

    idx = len(pts_wac.data) - 1

    if idx == last_idx:
        return

    last_idx = idx

    if idx >= len(pts_iirs.data):

        print("Click matching IIRS point first")
        return

    # napari gives [row,col]

    r_iirs, c_iirs = pts_iirs.data[idx]

    r_wac_shifted, c_wac_shifted = pts_wac.data[idx]

    # remove display translation
    r_wac = r_wac_shifted
    c_wac = c_wac_shifted - w_t[1]

    print("\nPoint Pair:", idx)

    print(f"IIRS : row={r_iirs:.2f}, col={c_iirs:.2f}")
    print(f"WAC  : row={r_wac:.2f}, col={c_wac:.2f}")

    iirs_pts.append([c_iirs, r_iirs])
    wac_pts.append([c_wac, r_wac])

pts_wac.events.data.connect(collect_points)

napari.run()

# ============================================================
# ARRAYS
# ============================================================

iirs_pts = np.array(iirs_pts)
wac_pts = np.array(wac_pts)

print("\nCollected points:")
print(iirs_pts.shape)
print(wac_pts.shape)

if len(iirs_pts) < 6:
    raise ValueError("Need more points")

# ============================================================
# WAC PIXELS -> PROJECTED COORDS
# ============================================================

wac_cols = wac_pts[:, 0]
wac_rows = wac_pts[:, 1]

with rasterio.open(wac) as src:

    wac_x, wac_y = rasterio.transform.xy(
        transform,
        wac_rows,
        wac_cols,
        offset='center'
    )

wac_x = np.array(wac_x)
wac_y = np.array(wac_y)

# ============================================================
# TPS FIT
# ============================================================

print("\nFitting TPS model...")

tps_x = RBFInterpolator(
    iirs_pts,
    wac_x,
    kernel='thin_plate_spline'
)

tps_y = RBFInterpolator(
    iirs_pts,
    wac_y,
    kernel='thin_plate_spline'
)

# ============================================================
# PREDICT GEOLOCATION
# ============================================================

h, w = cube.shape

cols_grid, rows_grid = np.meshgrid(
    np.arange(w),
    np.arange(h)
)

query_pts = np.column_stack([
    cols_grid.ravel(),
    rows_grid.ravel()
])

print("Predicting coordinates...")

pred_x = tps_x(query_pts).reshape(h, w)
pred_y = tps_y(query_pts).reshape(h, w)

# ============================================================
# XY -> LAT/LON
# ============================================================

R = 1737400.0

lon_rad = pred_x / R
lat_rad = pred_y / R

lon_new = np.rad2deg(lon_rad)
lat_new = np.rad2deg(lat_rad)

lon_new = lon_new % 360

# ============================================================
# SAVE
# ============================================================

np.save("lat_corrected.npy", lat_new)
np.save("lon_corrected.npy", lon_new)

print("\nSaved corrected lat/lon")

# ============================================================
# REPROJECT WAC TO NEW IIRS GEOLOCATION
# ============================================================

with rasterio.open(wac) as src:

    rows_new, cols_new = rasterio.transform.rowcol(
        src.transform,
        pred_x,
        pred_y
    )

    rows_new = np.array(rows_new).reshape(h, w)
    cols_new = np.array(cols_new).reshape(h, w)


    valid = (
        (rows_new >= 0) &
        (rows_new < src.height) &
        (cols_new >= 0) &
        (cols_new < src.width)
    )

    reproj = np.full((h, w), np.nan)

    band = src.read(1)

    reproj[valid] = band[
        rows_new[valid],
        cols_new[valid]
    ]

# ============================================================
# OVERLAY VERIFICATION
# ============================================================

viewer = napari.Viewer()

viewer.add_image(
    cube,
    name="IIRS",
    colormap="terrain"
)

viewer.add_image(
    reproj,
    name="WAC_reprojected",
    colormap="terrain",
    opacity=0.5
)

napari.run()
# -----------------------------------
# ENABLE MANUAL MOVE
# -----------------------------------
#iirs_layer.mode = "transform"
'''
print("\nInstructions:")
print("1. Select IIRS layer")
print("2. Press transform tool")
print("3. Drag image until craters overlap")
print("4. Close napari window")
print()
'''

'''
# -----------------------------------
# GET FINAL TRANSFORM
# -----------------------------------
print("\nFINAL VALUES")

print("Translation:")
print(iirs_layer.translate)

print("\nRotation:")
print(iirs_layer.rotate)

print("\nScale:")
print(iirs_layer.scale)

print("\nAffine:")
print(iirs_layer.affine.affine_matrix)
'''