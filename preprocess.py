import numpy as np
import tensorflow as tf




# =========================================================
# 2. ANGLE ENCODING FUNCTION
# =========================================================

def encode_angle(angle_deg):

    """
    Converts angle into sin/cos encoding.

    Input
    -----
    angle_deg : (N,)

    Output
    ------
    (N,2)
    """

    angle_rad = np.radians(angle_deg)

    return np.column_stack([

        np.sin(angle_rad),
        np.cos(angle_rad)

    ])


# =========================================================
# 3. TOPOGRAPHIC FACTOR
# =========================================================

def compute_T_factor(
    lat,
    slope,
    aspect
):

    """
    Computes topographic factor.

    Inputs
    ------
    lat    : (N,)
    slope  : (N,)
    aspect : (N,)

    Output
    ------
    T : (N,)
    """

    lat_rad    = np.radians(lat)
    slope_rad  = np.radians(slope)
    aspect_rad = np.radians(aspect)

    T = (

        np.sin(lat_rad)
        *
        np.sin(slope_rad)
        *
        (np.cos(aspect_rad) + 1)

    )

    return T


# =========================================================
# 4. MIN-MAX NORMALIZATION
# =========================================================

def minmax_normalize(
    x,
    xmin=None,
    xmax=None
):

    """
    Min-max normalization.

    Input
    -----
    x : any numpy array

    Output
    ------
    normalized array
    """

    if xmin is None:
        xmin = np.min(x)

    if xmax is None:
        xmax = np.max(x)

    x_norm = (

        (x - xmin)
        /
        (xmax - xmin + 1e-8)

    )

    return x_norm, xmin, xmax


# =========================================================
# 5. PREPROCESSING FUNCTION
# =========================================================

def preprocess_data(

    X_spectral,
    Y_flat,

    lat,
    slope,
    aspect,

    solar_zenith,
    solar_azimuth,

    sensor_zenith,
    sensor_azimuth

):

    """
    Builds:
    -------
    X_spec_norm
    Y_norm
    X_geometry

    Inputs
    ------
    X_spectral : (N,bands)
    Y_flat     : (N,bands)

    lat,slope,aspect : (N,)

    solar/sensor angles : (N,)
    """

    # =====================================================
    # A. NORMALIZE RUGGED SPECTRA
    # =====================================================

    X_spec_norm, spectral_min, spectral_max = (

        minmax_normalize(X_spectral)

    )


    # =====================================================
    # B. NORMALIZE FLAT TARGET
    # =====================================================

    # IMPORTANT:
    # use SAME scaling as rugged spectra

    Y_norm, _, _ = minmax_normalize(

        Y_flat,

        spectral_min,
        spectral_max

    )


    # =====================================================
    # C. COMPUTE T FACTOR
    # =====================================================

    T = compute_T_factor(

        lat,
        slope,
        aspect

    )


    # =====================================================
    # D. NORMALIZE T
    # =====================================================

    T_norm, T_min, T_max = (

        minmax_normalize(T)

    )

    T_norm = T_norm.reshape(-1,1)


    # =====================================================
    # E. ENCODE ANGLES
    # =====================================================

    solar_z = encode_angle(
        solar_zenith
    )

    solar_a = encode_angle(
        solar_azimuth
    )

    sensor_z = encode_angle(
        sensor_zenith
    )

    sensor_a = encode_angle(
        sensor_azimuth
    )


    # =====================================================
    # F. BUILD GEOMETRY MATRIX
    # =====================================================

    X_geometry = np.hstack([

        T_norm,

        solar_z,
        solar_a,

        sensor_z,
        sensor_a

    ])


    # =====================================================
    # G. RETURN EVERYTHING
    # =====================================================

    return (

        X_spec_norm,
        Y_norm,

        X_geometry,

        spectral_min,
        spectral_max,

        T_min,
        T_max

    )

