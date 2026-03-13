'''Parsing the xml file for timestamps and line exposure time,
and also finding the namespace for isda(line exposure)
'''
xml=r"/home/megha/arshveer/ch2_iir_nci_20250529T1233369467_d_img_d18/data/calibrated/20250529/ch2_iir_nci_20250529T1233369467_d_img_d18.xml"

import xml.etree.ElementTree as ET
from datetime import datetime

tree=ET.parse(xml)
root=tree.getroot()
namespace=root.tag
#print(namespace)

for elem in root.iter():
   if "start_date_time" in elem.tag:
        print(elem.tag)

start_time_st=root.find('.//start_date_time').text
time=datetime.strptime(
    start_time_st,
    "%Y%m%dT%H:%M:%S.%fZ"
).timestamp()
print(time)
