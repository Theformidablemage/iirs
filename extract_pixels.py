import numpy as np

def extract_pairs_with_coords(
    slope,
    Fe_map, Mg_map, Al_map,
    radiance_cube,
    lat_map,
    k=10,
    T_flat=5,
    T_rugged=15,
    W_thresh=0.02
):
    
    H, W = slope.shape

    flat_mask   = (slope < T_flat) & (~np.isnan(slope))
    rugged_mask = (slope > T_rugged) & (~np.isnan(slope))

    used_rugged = np.zeros_like(slope, dtype=bool)

    pairs_X = []
    pairs_Y = []

    rugged_lat_list = []
    #rugged_lon_list = []

    rugged_row=[]
    rugged_col=[]

    flat_row = []
    flat_col = []
    max_rug=50

    flat_indices = np.where(flat_mask)

    for idx in range(len(flat_indices[0])):
        i = flat_indices[0][idx]
        j = flat_indices[1][idx]

        fe_flat = Fe_map[i, j]
        mg_flat = Mg_map[i, j]
        al_flat = Al_map[i, j]

        if np.isnan(fe_flat) or np.isnan(mg_flat) or np.isnan(al_flat):
            continue

        row_min = max(0, i - k)
        row_max = min(H, i + k + 1)
        col_min = max(0, j - k)
        col_max = min(W, j + k + 1)

        rugc=0
        for m in range(row_min, row_max):
            for n in range(col_min, col_max):
                if rugc>max_rug:
                    break
                if not rugged_mask[m, n]:
                    continue

                if used_rugged[m, n]:
                    continue

                fe_r = Fe_map[m, n]
                mg_r = Mg_map[m, n]
                al_r = Al_map[m, n]

                if np.isnan(fe_r) or np.isnan(mg_r) or np.isnan(al_r):
                    continue
                
                fe_diff = abs(fe_r - fe_flat) / (fe_flat + 1e-8)
                mg_diff = abs(mg_r - mg_flat) / (mg_flat + 1e-8)
                al_diff = abs(al_r - al_flat) / (al_flat + 1e-8)

                if (fe_diff <= W_thresh and
                    mg_diff <= W_thresh and
                    al_diff <= W_thresh):

                    rugged_spec = radiance_cube[:, m, n]
                    flat_spec   = radiance_cube[:, i, j]

                    pairs_X.append(rugged_spec)
                    pairs_Y.append(flat_spec)

            # store coordinates
                    rugged_lat_list.append(lat_map[m, n])
                    #rugged_lon_list.append(lon_map[m, n])

                    rugged_row.append(m)
                    rugged_col.append(n)

                    flat_row.append(i)
                    flat_col.append(j)

                    used_rugged[m, n] = True
                    rugc+=1
            if rugc>max_rug:
                break
                   

    return (
        np.array(pairs_X),
        np.array(pairs_Y),
        np.array(rugged_lat_list),
        np.array(rugged_row),
        np.array(rugged_col),
        np.array(flat_row),
        np.array(flat_col)
    )




