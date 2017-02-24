# -*- coding: utf-8 -*-
"""
Created on Wed Sep  7 11:17:07 2016

@author: agentsmith
"""

import numpy as np
import pandas as pd


def create_learning_and_testing_sets(df, prap):
    """
        Cette fonction sépare un jeu de données en jeu de test & d'apprentissage
        args : "df" le DataFrame contenant les données
               "prap" le pourcentage de données à utiliser en train
        return : un dictionnaire contenant les données et les jeux d'apprentissage et de test
    """

    y = df['Victoire']
    x = df.drop('Victoire', 1)
    x.index = range(0, len(x))
    y.index = range(0, len(y))
    learning_index = [elt for elt in x.sample(frac=prap).index]
    testing_index = [elt for elt in x.index if elt not in learning_index]

    if ((len(learning_index) + len(testing_index)) == len(x)):

        features_learning = x.iloc[learning_index, :]
        features_testing = x.iloc[testing_index, :]
        # Echantillons de classes
        classes_learning = pd.DataFrame(y).iloc[learning_index, :]
        classes_testing = pd.DataFrame(y).iloc[testing_index, :]
        numpy_training_features = np.array(features_learning)
        numpy_training_classes = np.array(classes_learning).ravel()
        numpy_testing_features = np.array(features_testing)
        numpy_testing_classes = np.array(classes_testing).ravel()

        return {"X": x, "Y": y, "TrainingFeatures": numpy_training_features, "TrainingLabels": numpy_training_classes, "TestFeatures": numpy_testing_features, "TestLabels": numpy_testing_classes}
