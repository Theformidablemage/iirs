from read_qub1 import parse_xml, read_qub
from pathlib import Path
from scipy.io import loadmat
from calib_geo import geo_path
from geometry import interpolate_latlon
from maps_preprocessing import lookup_map_values
import numpy as np
import spectral
from extract_pixels import extract_pairs_with_coords
from preprocess import preprocess_data
from model import build_topographic_model
from sklearn.model_selection import (
    train_test_split
)
from tensorflow.keras.layers import (
    Input,
    Dense,
    Concatenate
)

from tensorflow.keras.models import Model



extracted=Path("/home/megha/Downloads/iirs_strips/extracted/extract_new")
derived=extracted/"derived"

iron=r"/home/megha/172.16.9.46:8000/Global20ppd_MLR_LPGRS_Fe.mat"
Al=r"/home/megha/172.16.9.46:8000/Global20ppd_MLR_CLASS_Al.mat"
Mg=r"/home/megha/172.16.9.46:8000/Global20ppd_MLR_CLASS_Mg.mat"

strips=[d for d in derived.iterdir() if d.is_dir()]

all_rug = []
all_fl  = []

all_rug_lat = []

all_slope = []
all_aspect = []

all_solar_az = []
all_solar_ze = []

all_sensor_az = []
all_sensor_ze = []


for strip in strips:
    name=strip.stem
    print(name)
    #print(strip.name)
    cal=geo_path(name,extracted)
    data=strip/"data"
    x=list(data.rglob("*.xml"))
    xml=x[0]
    q=list(data.rglob("*rdn*.qub"))
    qub=q[0]
    meta=parse_xml(xml)
    iirs=read_qub(qub,meta,skip_bands=[(28,34),(68,75),(161,256)])
    b,h,w=iirs.shape
    print(iirs.shape)
    lat,lon=interpolate_latlon(cal,h,w)
    i=loadmat(iron)
    fe=i['Fe']
    fe[fe>25]=np.nan
    m=loadmat(Mg)
    mg=m['Mg']
    a=loadmat(Al)
    al=a['Al']
    al[al<0]=np.nan
    fe_map=lookup_map_values(fe,lat,lon,-75,75,0,360)
    al_map=lookup_map_values(al*100,lat,lon,-85,85,0,360)
    mg_map=lookup_map_values(mg*100,lat,lon,-85,85,0,360)
    s=list(data.rglob("*obs*.hdr"))
    s=s[0]
    img=spectral.open_image(s)
    data=img.load()
    slope=data[:,:,7]
    slope=slope.squeeze(axis=2)
    print(slope.shape)
    rug,fl,rug_lat,rug_r,rug_c,fl_r,fl_c=extract_pairs_with_coords(slope,fe_map,mg_map,al_map,iirs,lat,10,5,15,0.02)
    print(rug.shape,fl.shape,rug_lat.shape,rug_r.shape,rug_c.shape,fl_r.shape,fl_c.shape)
    s1=data[:,:,0]
    s2=data[:,:,1]
    i1=data[:,:,2]
    i2=data[:,:,3]
    a=data[:,:,8]
    s_az=s1.squeeze(axis=2)
    s_ze=s2.squeeze(axis=2)
    i_az=i1.squeeze(axis=2)
    i_ze=i2.squeeze(axis=2)
    asp=a.squeeze(axis=2)
    s_az=s_az[rug_r,rug_c]
    s_ze=s_ze[rug_r,rug_c]
    i_az=i_az[rug_r,rug_c]
    i_ze=i_ze[rug_r,rug_c]
    asp=asp[rug_r,rug_c]
    sl=slope[rug_r,rug_c]
    print(s_az.shape)
    all_rug.append(rug)
    all_fl.append(fl)
    all_rug_lat.append(rug_lat)
    all_slope.append(sl)
    print(sl.shape)
    all_aspect.append(asp)
    all_solar_az.append(s_az)
    all_solar_ze.append(s_ze)
    all_sensor_az.append(i_az)
    all_sensor_ze.append(i_ze)
    


X_spectral = np.concatenate(
    all_rug,
    axis=0
)

Y_flat = np.concatenate(
    all_fl,
    axis=0
)

lat = np.concatenate(
    all_rug_lat
)

slope = np.concatenate(
    all_slope
)

aspect = np.concatenate(
    all_aspect
)

solar_azimuth = np.concatenate(
    all_solar_az
)

solar_zenith = np.concatenate(
    all_solar_ze
)

sensor_azimuth = np.concatenate(
    all_sensor_az
)

sensor_zenith = np.concatenate(
    all_sensor_ze
)

rug_norm,fl_norm,rug_geo,sp_min,sp_max,T_min,T_max= preprocess_data(X_spectral,Y_flat,lat,slope,aspect,solar_zenith,solar_azimuth,sensor_zenith,sensor_azimuth)

#np.savez(

  #  "scaling_parameters.npz",

  #  spectral_min=sp_min,
  #  spectral_max=sp_max,

  #  T_min=T_min,
   # T_max=T_max

#)
print("Scaling parameters saved")
topo_model=build_topographic_model(148,9)
(

    X_spec_train,
    X_spec_test,

    X_geo_train,
    X_geo_test,

    Y_train,
    Y_test

) = train_test_split(

    rug_norm,
    rug_geo,
    fl_norm,

    test_size=0.2,

    random_state=42

)

history = topo_model.fit(

    [

        X_spec_train,
        X_geo_train

    ],

    Y_train,

    epochs=50,

    batch_size=32,

    validation_split=0.1

)


#topo_model.save(
   # "topographic_correction_model"
#)

print("Model saved.")


loss, mae = topo_model.evaluate(

    [

        X_spec_test,
        X_geo_test

    ],

    Y_test

)

print("\nTest MSE:", loss)
print("Test MAE:", mae)
