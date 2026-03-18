'''Parsing the xml file for timestamps and line exposure time,
and also finding the namespace for isda(line exposure)
'''
xml=r"/home/megha/arshveer/ch2_iir_nci_20250529T1233369467_d_img_d18/data/calibrated/20250529/ch2_iir_nci_20250529T1233369467_d_img_d18.xml"

import xml.etree.ElementTree as ET, os,csv
from datetime import datetime
from scipy.interpolate import interp1d
import numpy as np
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
line=line/1000 #convert to milliseconds

for axis in root.iter():
    tag=axis.tag.split("}")[-1]
    if tag=="Axis_Array":
        axisn=None
        dims=None
        for child in axis:
            tag=child.tag.split("}")[-1]
            if tag=="axis_name":
                axisn=child.text
            elif tag=="elements":
                dims=int(child.text)
        if axisn=="LINE":
            lines=dims
        elif axisn=="SAMPLE":
            samples=dims
print("Lines/Rows: ",lines)
print("Samples/Columns: ",samples)

start_time_st=root.find('.//isda:start_date_time',ns).text
print(start_time_st)
time=datetime.strptime(
    start_time_st,
    "%Y-%m-%dT%H:%M:%S.%fZ"
).timestamp()
print(time)
time_ar=np.zeros(lines)
for i in range(lines):
    t= time+line*i
    time_ar[i]=t

#initialize lists to hold the needed sensor values
angles=[]
#updated csv for reading the required angles
c=r"/home/megha/arshveer/ch2_iir_nci_20250529T1233369467_d_img_d18/miscellaneous/oat_updated.csv"
with open(c,"r") as f:
    reader=csv.reader(f)
    header=next(reader)
    a=header.index("Solar_Azimuth")
    z=header.index("Solar_Zenith_Angle")
    sz=header.index("Yaw_Nadir_Angle")
    sa=header.index("Sensor_Azimuth")
    #Perform interpolation now
    for line in reader:
        angles.append([float(line[a]),  #Solar Azimuth
                       float(line[z]),  #Solar Zenith
                       float(line[sz]),#Sensor Zenith
                       float(line[sa]) #Sensor Azimuth
                       ])

#Now perform interpolation:
#first on oat-time and angles-
angles=np.array(angles)
so_az=np.unwrap(np.radians(angles[:,0]))
so_ze=angles[:,1]
se_ze=angles[:,2]
se_az=np.unwrap(np.radians(angles[:,3]))
print(so_ze.shape)
#initialize oat time array
oat_time=time+np.arange(len(so_az))*0.512
#oat_time and angles as a function: angles as a function of time
func_so_az=interp1d(oat_time,so_az,kind="linear",fill_value="extrapolate")
func_so_ze=interp1d(oat_time,so_ze,kind="linear",fill_value="extrapolate")
func_se_ze=interp1d(oat_time,se_ze,kind="linear",fill_value="extrapolate")
func_se_az=interp1d(oat_time,se_az,kind="linear",fill_value="extrapolate")
#now interpolating/finding angles at hyperspectral cube time
sol_az=np.degrees(func_so_az(time_ar))
sol_ze=func_so_ze(time_ar)
sen_ze=func_se_ze(time_ar)
sen_az=np.degrees(func_se_az(time_ar))

print(sen_az.shape)

test=r"/home/megha/arshveer/ch2_iir_nci_20250529T1233369467_d_img_d18/miscellaneous/test.txt"
with open(test,"w") as f:
    for ang in sen_az:
        f.write(f"{float(ang)}\n")
    print("Done") 


    
