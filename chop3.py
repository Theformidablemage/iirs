import numpy as np
import rasterio
from rasterio.windows import Window
from skimage.transform import resize


def chop(cube, lat, lon, wac):

    # -------------------------------------------------
    # GET IIRS SHAPE
    # -------------------------------------------------
    lines, samples = cube.shape

    # -------------------------------------------------
    # GET ONLY 4 CORNER COORDINATES
    # -------------------------------------------------
    corners_lat = np.array([
        lat[0, 0],
        lat[0, -1],
        lat[-1, 0],
        lat[-1, -1]
    ])

    corners_lon = np.array([
        lon[0, 0],
        lon[0, -1],
        lon[-1, 0],
        lon[-1, -1]
    ])
    corners_lon = ((corners_lon + 180) % 360) - 180
    # -------------------------------------------------
    # COMPUTE BOUNDING BOX
    # -------------------------------------------------
    lat_min = np.min(corners_lat)
    lat_max = np.max(corners_lat)

    lon_min = np.min(corners_lon)
    lon_max = np.max(corners_lon)
    org_lat=lat_max-lat_min
    org_lon=lon_max-lon_min
    print("Org lat: ",org_lat)
    print("Org Long: ",org_lon)
    lat_min-=1
    lat_max+=1
    lon_min-=1
    lon_max+=1
   
    new_lat=lat_max-lat_min
    new_lon=lon_max-lon_min
    print("New lat: ",new_lat)
    print("New Long: ",new_lon)
    print("Lat range:", lat_min, lat_max)
    print("Lon range:", lon_min, lon_max)
    scale_y= new_lat/org_lat
    scale_x=new_lon/org_lon
    print("Y(LAT):",scale_y)
    print("X(LONG):",scale_x)
    new_lines=int(scale_y*lines)
    new_samples=int(scale_x*samples)
    print(new_lines,new_samples)
    # -------------------------------------------------
    # CONVERT TO MOON PROJECTED COORDINATES
    # -------------------------------------------------
    R = 1737400

    x_min = R * np.deg2rad(lon_min)
    x_max = R * np.deg2rad(lon_max)

    y_min = R * np.deg2rad(lat_min)
    y_max = R * np.deg2rad(lat_max)

    # -------------------------------------------------
    # OPEN WAC
    # -------------------------------------------------
    with rasterio.open(wac, 'r') as src:

        print("CRS:", src.crs)

        # ---------------------------------------------
        # MAP COORDS -> PIXELS
        # ---------------------------------------------
        row_min, col_min = rasterio.transform.rowcol(
            src.transform,
            x_min,
            y_max
        )

        row_max, col_max = rasterio.transform.rowcol(
            src.transform,
            x_max,
            y_min
        )
       
        # ---------------------------------------------
        # ENSURE CORRECT ORDER
        # ---------------------------------------------
        row1 = min(row_min, row_max)
        row2 = max(row_min, row_max)

        col1 = min(col_min, col_max)
        col2 = max(col_min, col_max)

        #print("Rows:", row1, row2)
        #print("Cols:", col1, col2)



        
        # ---------------------------------------------
        # CREATE WINDOW
        # ---------------------------------------------
        window = Window(
            col1,
            row1,
            col2 - col1,
            row2 - row1
        )

        # ---------------------------------------------
        # READ WAC CROP
        # ---------------------------------------------
        wac_crop = src.read(1, window=window)

        print("Original WAC crop shape:", wac_crop.shape)

    # -------------------------------------------------
    # RESIZE TO IIRS SIZE
    # -------------------------------------------------
    wac_resized = resize(
        wac_crop,
       (new_lines, new_samples),
        preserve_range=True
    ).astype(np.float32)

    print("Final resized WAC shape:", wac_resized.shape)

    return wac_resized