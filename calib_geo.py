from pathlib import Path
import re



def geo_path(name,path):
    match=re.search(r"\d{8}T\d+", name)
    if not match:
        raise ValueError("Calibrated file missing")
    c_id=match.group(0)
    calibrated=path/"calibrated"
    file=list(calibrated.glob(f"*{c_id}*"))
    f=file[0]
    geo=f/"geometry"
    g=list(geo.rglob("*.csv"))
    coords=g[0]

    return coords