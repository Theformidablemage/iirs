from pathlib import Path
import zipfile
from read_qub1 import parse_xml, read_qub
import spectral as sp
import napari
from chop3 import chop

source=Path('/home/megha/Downloads/iirs_strips')
extract=Path('/home/megha/Downloads/iirs_strips/extracted/extract_new')
wac=r"/home/megha/arshveer/Lunar_LRO_LROC-WAC_Mosaic_global_100m_June2013 (1).tif"
'''
extract.mkdir(parents=True,exist_ok=True)

for zip_path in source.glob('*.zip'):
    out=extract/zip_path.stem
    out.mkdir(exist_ok=True)
    with zipfile.ZipFile(zip_path,'r') as file:
        file.extractall(out)
        print(f"Extracted: {zip_path.name}")
'''

strips= [d for d in extract.iterdir() if d.is_dir()]

for strip in strips:
    if strip.stem =="ch2_iir_ndi_20250601T0907397518_d_rfl_d18_srd" or strip.stem=="ch2_iir_ndi_20240125T0622468260_d_rfl_d18_srd" or strip.stem=="ch2_iir_ndi_20250802T1145049652_d_rfl_d18_srd" or strip.stem=="ch2_iir_ndi_20230707T2126184264_d_rfl_n18_srd" or strip.stem=="ch2_iir_ndi_20230420T0648107017_d_rfl_d32_srd":  
      continue
    print(strip.stem)
    data=strip/"data"
    coord=list(data.rglob('*loc*.hdr'))
    coord=coord[0]
    img=sp.open_image(coord)
    geo=img.load()
    long=geo[:,:,0]
    lat=geo[:,:,1]
    long=long.squeeze(axis=2)
    lat=lat.squeeze(axis=2)
    x=list(data.rglob('*.xml'))
    xml=x[0]
    q=list(data.rglob('*rdn*.qub'))
    qub=q[0]
    meta=parse_xml(xml)
    cube=read_qub(qub,meta,skip_bands=0)
    c=cube[48,:,:]
    print(c.shape)
    w=chop(c,lat,long,wac)
    viewer=napari.Viewer()
    viewer.add_image(c,name="IIRS_derived",colormap="terrain",opacity=1)
    viewer.add_image(w,name="Wac",colormap="terrain",opacity=0.6)
    napari.run()

    