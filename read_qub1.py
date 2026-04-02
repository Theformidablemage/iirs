import xml.etree.ElementTree as et
import numpy as np

def st(tag):
    return tag.split('}',1)[-1]

def byte_order(data_type):
    if "MSB" in data_type:
        return "MSB"
    if "LSB" in data_type:
        return "LSB"
    return "MSB"

def parse_xml(xml):
    tree=et.parse(xml)
    root=tree.getroot()

    array=None

    for elem in root.iter():
        if st(elem.tag)=="Array_3D_Spectrum":
            array=elem
            break
    if array is None:
        raise ValueError("Array 3D spectrum is empty")
    axes=int(array.find(".//{*}axes").text)

    axis_el=[]
    axis_na=[]

    for axis in array.findall(".//{*}Axis_Array"):
        axis_na.append(axis.find(".//{*}axis_name").text)
        axis_el.append(int(axis.find(".//{*}elements").text))

    data_type=array.find(".//{*}data_type").text
    byte=byte_order(data_type)
    offset=int(array.find(".//{*}offset").text)

    return{
        "axes":axes,
        "axis_names":axis_na,
        "axis_elements":axis_el,
        "data_type":data_type,
        "byte_order":byte,
        "offset": offset
    }

def pds_to_numpy(pdstype):
    mapping={
        "IEEE754LSBSingle": "<f4",
    }
    if pdstype not in mapping:
        raise ValueError(f"Unsupported PDS data type: {pdstype}")
    return np.dtype(mapping[pdstype])

def read_qub(qub_file,meta,skip_bands):
    dtype=pds_to_numpy(meta["data_type"])

    bands,lines,samples=meta["axis_elements"]
    bytes_per_band=lines*samples*dtype.itemsize

    if not skip_bands:
        with open(qub_file,"rb") as f:
            f.seek(meta["offset"])
            count=bands*lines*samples
            data=np.fromfile(f,dtype=dtype,count=count)
        return data.reshape((bands,lines,samples))
    
    skip_bands=sorted(skip_bands)
    read=[]
    prev_end=0
    
    for start,end in skip_bands:
        if prev_end<start:
            read.append((prev_end,start))
        prev_end=end
    if prev_end<bands:
        read.append((prev_end,bands))

    cubes=[]
    print(read)
    with open(qub_file,"rb") as f:
        for start,end in read:
            f.seek(meta["offset"]+start*bytes_per_band)
            num_bands=end-start
            count=num_bands*lines*samples
            data=np.fromfile(f,dtype=dtype,count=count)
            cube_part=data.reshape(num_bands,lines,samples)
            cubes.append(cube_part)
    return np.concatenate(cubes,axis=0)


s=[(28,34),(68,75),(161,256)]

qub=r"/home/megha/arshveer/ch2_iir_nci_20211218T0038037745_d_img_hw1/data/calibrated/20211218/ch2_iir_nci_20211218T0038037745_d_img_hw1.qub"
xml=r"/home/megha/arshveer/ch2_iir_nci_20211218T0038037745_d_img_hw1/data/calibrated/20211218/ch2_iir_nci_20211218T0038037745_d_img_hw1.xml"
meta=parse_xml(xml)
cube=read_qub(qub,meta,s)
print(cube.shape)


