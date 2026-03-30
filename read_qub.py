import xml.etree.ElementTree as ET


def strip_ns(tag):
    return tag.split('}', 1)[-1]

def infer_byte_order(data_type):
    if "MSB" in data_type:
        return "MSB"
    if "LSB" in data_type:
        return "LSB"
    return "MSB"  

def parse_pds5_spectrum_xml(xml_file):
    tree = ET.parse(xml_file)
    root = tree.getroot()

    array = None
    for elem in root.iter():
        if strip_ns(elem.tag) == "Array_3D_Spectrum":
            array = elem
            break

    if array is None:
        raise ValueError("Array_3D_Spectrum not found in XML")

    axes = int(array.find(".//{*}axes").text)

    axis_elements = []
    axis_names = []

    for axis in array.findall(".//{*}Axis_Array"):
        axis_elements.append(int(axis.find(".//{*}elements").text))
        axis_names.append(axis.find(".//{*}axis_name").text)

    data_type = array.find(".//{*}data_type").text
    byte_order = infer_byte_order(data_type)

    offset_elem = array.find(".//{*}offset")
    offset = int(offset_elem.text) if offset_elem is not None else 0

    return {
        "axes": axes,
        "axis_names": axis_names,
        "dimensions": axis_elements,
        "data_type": data_type,
        "byte_order": byte_order,
        "offset": offset
    }




import numpy as np

def pds_dtype_to_numpy(pds_type):
    mapping = {
        # Integers
        "UnsignedByte": "u1",
        "SignedByte": "i1",

        "UnsignedLSB2": "<u2",
        "SignedLSB2": "<i2",
        "UnsignedMSB2": ">u2",
        "SignedMSB2": ">i2",

        "UnsignedLSB4": "<u4",
        "SignedLSB4": "<i4",
        "UnsignedMSB4": ">u4",
        "SignedMSB4": ">i4",

        # Floats 
        "IEEE754LSBSingle": "<f4",
        "IEEE754MSBSingle": ">f4",
        "IEEE754LSBDouble": "<f8",
        "IEEE754MSBDouble": ">f8",

        # Older aliases 
        "IEEE754LSB4": "<f4",
        "IEEE754MSB4": ">f4"
    }

    if pds_type not in mapping:
        raise ValueError(f"Unsupported PDS data type: {pds_type}")

    return np.dtype(mapping[pds_type])

'''def read_qub(qub_file, meta):
    dtype = pds_dtype_to_numpy(meta["data_type"])

    with open(qub_file, "rb") as f:
        f.seek(meta["offset"])
        data = np.fromfile(f, dtype=dtype)

    cube = data.reshape(meta["dimensions"])
    return cube'''

def read_qub(qub_file, meta, skip_bands=0):
    dtype = pds_dtype_to_numpy(meta["data_type"])

    bands, lines, samples = meta["dimensions"]
    bytes_per_band = lines * samples * dtype.itemsize

    with open(qub_file, "rb") as f:
        f.seek(meta["offset"] + skip_bands * bytes_per_band)

        remaining_bands = bands - skip_bands
        count = remaining_bands * lines * samples

        data = np.fromfile(f, dtype=dtype, count=count)

    cube = data.reshape((remaining_bands, lines, samples))
    return cube
