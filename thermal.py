import numpy as np

def thermal_corrector_np(
    cube,
    wavelengths,
    emissivity=0.95,
    save_path=None
):
    """
    Vectorized thermal correction using Planck physics
    """
    # Physical constants
 
    c = 3.0e8
    h = 6.626e-34
    k = 1.38e-23

    # Remove noisy bands
  
    rad = cube* 0.01          # (B, H, W)
    B,H,W=rad.shape
    rad[rad <= 0] = np.nan

    #wavelengths = wavelengths[77:-2] # (B,)
    wavelengths=wavelengths*1e-9
   
    # Thermal window (4.5–4.874 µm)
   
    lmbL, lmbU = 4.5e-6, 4.874e-6
    idx = np.where((wavelengths >= lmbL) & (wavelengths <= lmbU))[0]

    if idx.size == 0:
        raise ValueError("No bands found in thermal window")

    
    # Extract thermal-window radiance
 

    print("Cube bands:", cube.shape[0])
    print("Wavelengths shape:", wavelengths.shape)
    print("Wavelength min/max (µm):", wavelengths.min()*1e6, wavelengths.max()*1e6)
    print("Thermal window indices:", idx)
    


    rad_tw = rad[idx]                          # (Nt, H, W)
    lambda_tw = wavelengths[idx][:, None, None]  # (Nt, 1, 1)

    #Plotting to check for bad bands and bad pixels
    import matplotlib.pyplot as plt

    #neg_mask = rad_tw < 0
    #zero_mask = rad_tw == 0
    nan_mask = ~np.isfinite(rad_tw)

    #neg_count = np.sum(neg_mask, axis=(1, 2))
    #zero_count = np.sum(zero_mask, axis=(1, 2))
    nan_count = np.sum(nan_mask, axis=(1, 2))

    band=idx

    
    plt.figure()

    #plt.scatter(band, neg_count, label="negative", s=10)
    #plt.scatter(band, zero_count, label="zero", s=10)
    plt.scatter(band, nan_count, label="nan", s=10)

    plt.xlabel("Band number")
    plt.ylabel("Pixel count")
    plt.title("Invalid pixels per thermal band")
    plt.legend()
    plt.show()


    all_nan_pixels = np.all(~np.isfinite(rad_tw), axis=0)

    print("Total pixels:", H * W)
    print("Pixels with ALL thermal bands invalid:",
      np.sum(all_nan_pixels))
    print("Fraction:",
      np.mean(all_nan_pixels))


    plt.imshow(all_nan_pixels)
    plt.title("Pixels with all thermal bands invalid")
    plt.colorbar()
    plt.show()

    print("All-invalid pixels:", np.sum(all_nan_pixels))



    #valid = rad_tw > 0
    valid = np.isfinite(rad_tw)

    print("Thermal radiance min/max:",
      np.nanmin(rad_tw), np.nanmax(rad_tw))

   
    # Invert Planck → Temperature
  
    q = np.where(
        valid,
        np.log(
            (emissivity * 2 * h * c**2) /
            (rad_tw * lambda_tw**5) + 1
        ),
        np.nan
    )

    T = np.where(
        valid,
        (h * c) / (lambda_tw * k * q),
        np.nan
    )

    plt.figure(figsize=(6,6))
    plt.imshow(all_nan_pixels.T, aspect='auto')
    plt.title("Pixels with all thermal bands invalid")
    plt.colorbar()
    plt.show()



    # Mean temperature per pixel
    #temperature_map = np.nanmean(T, axis=0)   # (H, W)

    temperature_map = np.full((H, W), np.nan)

    valid_pix = np.any(np.isfinite(T), axis=0)
    temperature_map[valid_pix] = np.nanmean(T[:, valid_pix], axis=0)


    # Forward Planck → thermal radiance
    
    wl_3d = wavelengths[:, None, None]         # (B, 1, 1)
    T_3d = temperature_map[None, :, :]         # (1, H, W)

    thermal_rad = (
        (2 * h * c**2) / (wl_3d**5)
    ) / (
        np.exp(h * c / (wl_3d * k * T_3d)) - 1
    )

    
    # Thermal correction

    corrected_cube = rad.copy()
    corrected_cube -= emissivity * thermal_rad
    corrected_cube[corrected_cube < 0] = 0

    # Save output
    """
     if save_path is not None:  
        np.savez_compressed(
            save_path,
            corrected_cube=corrected_cube.astype(np.float32),
            temperature_map=temperature_map.astype(np.float32),
            wavelengths=wavelengths.astype(np.float64),
            emissivity=emissivity   
        )
    """    
    
    print("done")
    return corrected_cube, temperature_map
