import numpy as np, pandas as pd
from scipy.interpolate import griddata

def interpolate_latlon(geometry_csv, lines, samples):
    """
    Interpolates latitude and longitude onto full image grid

    Parameters
    ----------
    geometry_csv : str
        Path to geometry CSV file
    lines : int
        Number of image lines
    samples : int
        Number of image samples

    Returns
    -------
    lat_grid : (lines, samples) ndarray
    lon_grid : (lines, samples) ndarray
    """

    geo = pd.read_csv(geometry_csv)

    pixels = geo["Pixel"].values     # sample index
    scans  = geo["Scan"].values      # line index
    lats   = geo["Latitude"].values
    lons   = geo["Longitude"].values

    

    grid_lines, grid_samples = np.mgrid[
        0:lines,
        0:samples
    ]

    known_points = np.column_stack((scans, pixels))

    lat_grid = griddata(
        known_points,
        lats,
        (grid_lines, grid_samples),
        method="linear"
    )

    lon_grid = griddata(
        known_points,
        lons,
        (grid_lines, grid_samples),
        method="linear"
    )
    #print(lat_grid)

    return lat_grid, lon_grid