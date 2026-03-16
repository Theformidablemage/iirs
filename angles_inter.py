'''Parsing the xml file for timestamps and line exposure time,
and also finding the namespace for isda(line exposure)
'''
xml=r"D:\ch2_iir_nci_20210720T2333026105_d_img_d32\data\calibrated\20210720\ch2_iir_nci_20210720T2333026105_d_img_d32.xml"

import xml.etree.ElementTree as ET, os,csv
from datetime import datetime
os.system('cls')
tree=ET.parse(xml)
root=tree.getroot()
#namespace=root.tag
#print(namespace)
ns={'isda':'http://pds.nasa.gov/pds4/pds/v1'}   #namespace uri stored in dict coz every element has it before its name

for elem in root.iter():
   tag=(elem.tag).split("}")[-1]
   if "line_exposure_duration"==tag:
        line=float(elem.text)
        print(line)


start_time_st=root.find('.//isda:start_date_time',ns).text
print(start_time_st)
time=datetime.strptime(
    start_time_st,
    "%Y-%m-%dT%H:%M:%S.%fZ"
).timestamp()
print(time)

#updated csv for reading the required angles
c=r"D:\ch2_iir_nci_20210720T2333026105_d_img_d32\oat1.csv"
with open(c,"r") as f:
    header=csv.reader(c)
    a=header.index("Solar_Azimuth")
    z=header.index("Solar_Zenith_Angle")
    sz=header.index("Yaw_Nadir_Angle")
    sa=header
    for line in f:
        az=

