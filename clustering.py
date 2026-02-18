import numpy as np
from sklearn.cluster import KMeans
import matplotlib.pyplot as plt

def clustering_pipeline(
        ref_cube,
        wavelengths,
        mask=None,
        n_clusters=4,       
):
    #prep for clustering
    wavelengths=wavelengths[77:-2]
    band_mask=wavelengths<3300
    wave_new=wavelengths[band_mask]
    B,H,W=ref_cube.shape
    spectra=ref_cube.reshape(B,-1).T
    spectra=spectra[:,band_mask]

#new good mask
    #finite=np.mean(np.isfinite(spectra),axis=1)
    #good=finite>0.5
#doesnt work as well: there are nan values during clustering
    
   #  becomes the old good mask---- good=np.all(np.isfinite(spectra),axis=1)
#checking good for debugging
   # finite=np.mean(np.isfinite(spectra),axis=1)
    #print("Min finite fraction:", finite.min())
    #print("Mean finite fraction:",finite.mean())
    #print("No. pixels that are 100% valid:",np.sum(finite==1))
#Results no pixel is 100% valid so we change the good mask

#plot for invalid pixels per band
    invalid=np.sum(~np.isfinite(spectra),axis=0)
    plt.figure()
    plt.plot(wave_new,invalid)
    plt.xlabel("Wavelength")
    plt.ylabel("Number of invalid pixels")
    plt.title("Invalid pixels per band")
    plt.show()

    if mask is not None:
        good&= mask.reshape(-1)

    prep= spectra[good]

#clustering
    kmeans=KMeans(
        n_clusters=n_clusters,
        random_state=0,
        n_init=10
    )
    labels=kmeans.fit_predict(prep)

    centers=kmeans.cluster_centers_

#labels to images

    cluster_map= np.full(H*W, -1)
    cluster_map[good]=labels

    cluster_img=cluster_map.reshape(H,W)

#plotting

    for i in range(n_clusters):
        cluster_spectra=prep[labels==i]
        plt.figure(figsize=(6,4))

        for spec in cluster_spectra:
            plt.plot(wave_new,spec,color='gray',alpha=0.1)

        plt.plot(
            wave_new,
            centers[i],
            color='red',
            linewidth=2,
            label=f"Cluster{i}mean"
        )
        plt.xlabel("Wavelength(nm)")
        plt.ylabel("Reflectance")
        plt.title(f"All pixels spectra for cluster {i} (N={cluster_spectra.shape[0]})")
        plt.legend()
        plt.tight_layout()
        plt.show()


    
    plt.figure()
    for i, spec in enumerate(centers):
        plt.plot(wave_new, spec,label=f"Cluster{i}") 

    plt.xlabel("Wavelength in nano m")
    plt.ylabel("Reflectance")
    plt.title("Mean spectra per cluster")
    plt.legend()
    plt.show()
    

    return cluster_img, labels, centers


