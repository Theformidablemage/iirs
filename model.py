import numpy as np
import tensorflow as tf

from tensorflow.keras.layers import (
    Input,
    Dense,
    Concatenate
)

from tensorflow.keras.models import Model

from sklearn.model_selection import (
    train_test_split
)



# =========================================================
# 6. MODEL FUNCTION
# =========================================================

def build_topographic_model(

    num_bands,
    geometry_features

):

    """
    Builds topographic correction model.

    Inputs
    ------
    num_bands : int

    geometry_features : int
    """

    # =====================================================
    # INPUTS
    # =====================================================

    spectral_input = Input(
        shape=(num_bands,)
    )

    geo_input = Input(
        shape=(geometry_features,)
    )


    # =====================================================
    # SPECTRAL BRANCH
    # =====================================================

    x1 = Dense(
        128,
        activation='relu'
    )(spectral_input)

    x1 = Dense(
        64,
        activation='relu'
    )(x1)


    # =====================================================
    # GEOMETRY BRANCH
    # =====================================================

    x2 = Dense(
        32,
        activation='relu'
    )(geo_input)

    x2 = Dense(
        16,
        activation='relu'
    )(x2)


    # =====================================================
    # FEATURE FUSION
    # =====================================================

    combined = Concatenate()([

        x1,
        x2

    ])


    # =====================================================
    # FUSION LEARNING
    # =====================================================

    x = Dense(
        128,
        activation='relu'
    )(combined)

    x = Dense(
        64,
        activation='relu'
    )(x)


    # =====================================================
    # OUTPUT
    # =====================================================

    output = Dense(

        num_bands,

        activation='linear'

    )(x)


    # =====================================================
    # BUILD MODEL
    # =====================================================

    model = Model(

        inputs=[

            spectral_input,
            geo_input

        ],

        outputs=output

    )


    # =====================================================
    # COMPILE
    # =====================================================

    model.compile(

        optimizer=tf.keras.optimizers.Adam(
            learning_rate=0.001
        ),

        loss='mse',

        metrics=['mae']

    )

    return model




