import os,csv, numpy as np 
#os.system('cls')

widths=[
    8,6,4,28,
    20,20,20,20,20,20,
    12,12,12,
    56,56,56,
    14,14,14,14,14,14,
    12,12,
    1,9,9,9,
    10,5,9,9,
    16,16,16,41
]

header = [
    "Record_Type",
    "Physical_Record_Number",
    "Block_Length",
    "UTC_Time Year",
    "Month",
    "Day",
    "Hours",
    "Minutes",
    "Seconds",
    "Milliseconds",
    "Lunar_Pos_X_km",
    "Lunar_Pos_Y_km",
    "Lunar_Pos_Z_km",
    "Sat_Pos_X_km",
    "Sat_Pos_Y_km",
    "Sat_Pos_Z_km",
    "Sat_Vel_X_kms",
    "Sat_Vel_Y_kms",
    "Sat_Vel_Z_kms",
    "S/C Attitude - Inertial to Body Q1",
     "Q2", "Q3", "Q4",
    "Transformation Quaternion for Earth Fixed IAU frame Q1",
    "Q2", "Q3", "Q4",
    "Transformation Quaternion for Lunar Fixed IAU frame Q1",
    "Q2", "Q3", "Q4",
    "SubSatellite_Latitude_deg",
    "SubSatellite_Longitude_deg",
    "Solar_Azimuth",
    "Solar_Elevation",
    "Latitude_deg",
    "Longitude_deg",
    "Satellite_Altitude_km",
    "Roll_Velocity_Angle",
    "Eclipse_Status",
    "Emission_Angle",
    "Sun angle w.r.t. -ve Yaw (Phase_Angle)",
    "Yaw_Nadir_Angle",
    "Slant_Range_km",
    "Orbit_Number",
    "Solar_Zenith_Angle",
    "FoV_Velocity_Angle",
    "Yaw_X_Angle",
    "Roll_Y_Angle",
    "Pitch_Z_Angle",
    "Spare"
]



path=r"/home/megha/Downloads/iirs_strips/extracted/ch2_iir_nci_20230707T2126184264_d_img_d32/miscellaneous/calibrated/20230707/ch2_iir_nci_20230707T2126184264_d_img_d32.oat"
out=r"/home/megha/Downloads/iirs_strips/extracted/ch2_iir_nci_20230707T2126184264_d_img_d32/miscellaneous/oat.csv"

def parse_width(line,w):
    fields=[]
    s=0
    for wid in w:
        e=s+wid
        if(s==18):
            fields.extend(line[s:e].split())
        elif s in (202,258,314):
            fields.extend(line[s:e].split())
        else:
            fields.append(line[s:e].strip())
        s=e
    return fields


header[28]="lq2"
header[29]="lq3"
header[30]="lq4"
q1=header.index("Transformation Quaternion for Lunar Fixed IAU frame Q1")
lat=header.index("Latitude_deg")
lon=header.index("Longitude_deg")
x=header.index("Sat_Pos_X_km")
y=header.index("Sat_Pos_Y_km")
z=header.index("Sat_Pos_Z_km")

quart=[]
la=[]
lo=[]
pos=[]
data=[]

with open(path,"r") as f, open(out,"w", newline="") as out:
    writer=csv.writer(out)
    writer.writerow(header)
    for line in f:
        parsed=parse_width(line,widths)
        writer.writerow(parsed)
        data.append(parsed)
        la.append(
            float(parsed[lat])
        )
        lo.append(
            float(parsed[lon])
        )
        pos.append([
            float(parsed[x]),
            float(parsed[y]),
            float(parsed[z])
        ])
        quart.append([
            float(parsed[q1]),
            float(parsed[28]),
            float(parsed[29]),
            float(parsed[30])
        ])

la=np.array(la)
print(la.shape)
lo=np.array(lo)
pos=np.array(pos)
quart=np.array(quart)
data=np.array(data)
print(quart.shape)
print(pos.shape)
print("OAT converted to CSV")

# ==========================================================
# CONSTANTS
# ==========================================================
LUNAR_RADIUS_KM = 1737.4


# ==========================================================
# QUATERNION UTILITIES
# ==========================================================
def quat_rotate(q, v):
    """
    Rotate vector v using quaternion q = [qx, qy, qz, qw]
    """
    #now q is of size (N,4) and v of (N,3)

    q = np.asarray(q, dtype=float)
    v = np.asarray(v, dtype=float)

    q_xyz = q[:,:3]
    qw = q[:,3][:,None] #change qw shape from (,N)-rank 1 array to (N,1)-column vector

    t = 2.0 * np.cross(q_xyz, v)
    v_rot = v + qw * t + np.cross(q_xyz, t)

    return v_rot


# ==========================================================
# COORDINATE TRANSFORMS
# ==========================================================

def latlon_to_cartesian(lat_deg, lon_deg, R=LUNAR_RADIUS_KM):
    """
    Convert latitude/longitude to lunar-fixed Cartesian coordinates.
    """
    lat = np.deg2rad(lat_deg)
    lon = np.deg2rad(lon_deg)

    x = R * np.cos(lat) * np.cos(lon)
    y = R * np.cos(lat) * np.sin(lon)
    z = R * np.sin(lat)
#return statement should give array of N,3 - each row should be a vector from center of moon
    return np.column_stack((x, y, z))



# ==========================================================
# SENSOR AZIMUTH (METHOD-1)
# ==========================================================
def sensor_azimuth(sc_pos_lf, ground_lat, ground_lon):
    """
    Compute sensor azimuth angle (degrees clockwise from North).
    """
    # Ground point position
    rp = latlon_to_cartesian(ground_lat, ground_lon)

    # Look vector (spacecraft -> ground)
    v = rp - sc_pos_lf #both of same size (N,3)
    #norm should be computed for each row differently not globally
    v = v / np.linalg.norm(v,axis=1,keepdims=True)

    lat = np.deg2rad(ground_lat)
    lon = np.deg2rad(ground_lon)

    # Local East & North unit vectors
    #make east and north vectors of size (N,3) as well
    east = np.column_stack((
        -np.sin(lon),
         np.cos(lon),
         np.zeros_like(lon)
    ))

    north = np.column_stack((
        -np.sin(lat) * np.cos(lon),
        -np.sin(lat) * np.sin(lon),
         np.cos(lat)
    ))

    # Projections
    #matrix mul wont work for both vectors of size (N,3)
    vE = np.sum(v*east,axis=1)
    vN = np.sum(v*north,axis=1)

    az = np.degrees(np.arctan2(vE, vN))
    return (az + 360.0) % 360.0

'''
# ==========================================================
# EXAMPLE: ONE OAT RECORD
# ==========================================================
if __name__ == "__main__":

    # ------------------------------------------------------
    # INPUTS (replace with values from your OAT file)
    # ------------------------------------------------------

    # Satellite position in J2000 frame (km)
    sc_pos_j2000 = np.array([
       -60.993666,   # X
       1602.988713,   # Y
       925.944174    # Z
    ])

    # Quaternion: Inertial -> Lunar Fixed (Q1 Q2 Q3 Q4)
    q_if = np.array([
        0.1489578952,   # qx
       -0.1311606428,   # qy
        0.5999980604,   # qz
        0.7749908120    # qw
    ])

    # Ground observation point (from OAT)
    ground_lat = 7.24220918   # degrees
    ground_lon = 15.59204831   # degrees

    # ------------------------------------------------------
    # PROCESSING
    # ------------------------------------------------------

    # Rotate spacecraft position into lunar-fixed frame
    sc_pos_lf = quat_rotate(q_if, sc_pos_j2000)

    # Compute sensor azimuth
    az = sensor_azimuth(sc_pos_lf, ground_lat, ground_lon)

    # ------------------------------------------------------
    # OUTPUT
    # ------------------------------------------------------
    print("==========================================")
    print("Sensor Azimuth Computation")
    print("==========================================")
    print(f"Ground lat, lon      : {ground_lat:.4f}, {ground_lon:.4f}")
    print(f"Sensor azimuth (deg) : {az:.3f}")
'''

   

<<<<<<< HEAD
o=r"D:\ch2_iir_nci_20210720T2333026105_d_img_d32\miscellaneous\oat_updated.csv"
=======
o=r"/home/megha/Downloads/iirs_strips/extracted/ch2_iir_nci_20230707T2126184264_d_img_d32/miscellaneous/oat_updated.csv"
>>>>>>> 1bd4b2cb1f54dcad0db143cfd80e89f0ce732798

sc=quat_rotate(quart,pos)
#sc of size (N,3)
header.append("Sensor_Azimuth")
se_az=sensor_azimuth(sc,la,lo)
data=np.column_stack((data,se_az))
with open(o, "w", newline="") as f:
    writer=csv.writer(f)
    writer.writerow(header)
    writer.writerows(data)










