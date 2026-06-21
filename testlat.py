import csv,numpy as np

path=r"/home/megha/Downloads/iirs_strips/extracted/ch2_iir_nci_20230618T0455491197_d_img_n18/miscellaneous/oat_updated.csv"
o=r"/home/megha/Downloads/iirs_strips/extracted/ch2_iir_nci_20230618T0455491197_d_img_n18/geometry"
def new_lat(in_p,out_p,lines,samples):  
  lat=[]
  lon=[]
  with open(path,"r") as file,open(o,"w",newline="") as out:
    reader=csv.reader(file)
    header=next(reader)
    lati=header.index('Latitude_deg')
    loni=header.index('Longitude_deg')
    for row in reader:
        lat.append(float(row[lati]))
        lon.append(float(row[loni]))

  lat=np.array(lat)
  lon=np.array(lon)
  h=["Longitude","Latitude","Pixel","Scan"]
  writer=csv.writer(out)
  writer.writerow(h)
  oat=39.706115188
  N=len(lat)
  exp=53.060
  time=np.arange




