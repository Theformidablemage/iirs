from pathlib import Path
import zipfile
from geometry import interpolate_latlon
from read_qub1 import parse_xml, read_qub
import numpy as np

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

for strip in strips:
    files=get_required_files(strip)
    xml,qub,geo=files
    #print(xml)
    meta=parse_xml(xml)
    cube=read_qub(qub,meta,skip_bands=[(28,34),(68,75),(161,256)])
    out=extract/f"{strip.name}_cube.npy"
    out.parent.mkdir(parents=True,exist_ok=True)
    np.save(out,cube)
    del cube
