import numpy as np

def lookup_map_values(map_data, lat_map, lon_map,
                      lat_min=-75, lat_max=75,
                      lon_min=0, lon_max=360):
    """
    Map lat/lon grids → corresponding values from map_data
    
    Parameters:
        map_data : (Hm, Wm) global map (Fe/Mg/Al)
        lat_map  : (H, W) IIRS latitude grid
        lon_map  : (H, W) IIRS longitude grid
    
    Returns:
        value_map : (H, W) values aligned with IIRS grid
    """

    Hm, Wm = map_data.shape

    # Normalize longitude
    lon_map = lon_map % 360

    # Convert lat/lon → indices (vectorized)
    row = (((lat_max - lat_map) / (lat_max - lat_min) )* Hm).astype(int)
    col = (((lon_map - lon_min) / (lon_max - lon_min) )* Wm).astype(int)

    # Clip indices
    row = np.clip(row, 0, Hm - 1)
    col = np.clip(col, 0, Wm - 1)

    # Extract values
    value_map = map_data[row, col]

    return value_map
