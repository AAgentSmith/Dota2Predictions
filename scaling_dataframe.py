# -*- coding: utf-8 -*-
"""
Created on Wed Sep  7 11:17:07 2016

@author: agentsmith
"""

from sklearn import preprocessing


def scaling_dataframe(df):
    """
        Cette fonction à pour objectif de Scaler la matrice de features.
    """
    return preprocessing.scale(df)
