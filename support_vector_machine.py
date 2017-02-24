# -*- coding: utf-8 -*-
"""
Created on Wed Sep  7 11:17:07 2016

@author: agentsmith
"""

import numpy as np
import time
from sklearn.metrics import confusion_matrix
from sklearn.model_selection import KFold
from sklearn import svm


def support_vector_machine_model(learning_and_training_dict, kfold_cross_validation, number_kfolds, svm_parameters):
    """
        Cette fonction applique un modèle d'apprentissage de type SVM avec
        un SVM pré-configuré à l'avance, les paramètres du modèles auront été determinés par GridSearch.
        Possibilité d'effectuer un Kfold cross validation ou un simpe apprentissage Test / Train.
        args : "learning_and_training_dict" : dictionnaire qui contient les données d'apprentissage et de test
               "kfold_cross_validation" : true ou false selon kfold cross validation
               "number_kfolds" : nombre de kfolds
               "svm_parameters" : les paramètres du svm désirés
        return : un dictionnaire contenant le modèle, les erreurs de test et d'apprentissage ainsi que le temps de calcul
    """

    # Creation d'une instance d'objet type "svm" afin d'entrainer un modèle de type support vector machine avec les paramètres désirés
    my_svm = svm.SVC()
    # On fixe les paramètres
    if len(svm_parameters) != 0:

        for parameters_keys in svm_parameters:
            setattr(my_svm, parameters_keys, svm_parameters[parameters_keys])

    if not kfold_cross_validation:

        time_before = time.time()

        # Apprentissage du modèle
        my_trained_svm = my_svm.fit(learning_and_training_dict["TrainingFeatures"], learning_and_training_dict["TrainingLabels"])
        # Erreur d'apprentissage & Matrice de confusion
        training_labels_predicted = my_trained_svm.predict(learning_and_training_dict["TrainingFeatures"])
        training_confusion = confusion_matrix(training_labels_predicted, learning_and_training_dict["TrainingLabels"])
        training_error = 100 - (float(training_confusion.trace()) / float(len(learning_and_training_dict["TrainingLabels"])) * 100)
        # Test du modèle & Matrice de confusion
        test_labels_predicted = my_trained_svm.predict(learning_and_training_dict["TestFeatures"])
        test_confusion = confusion_matrix(test_labels_predicted, learning_and_training_dict["TestLabels"])
        test_error = 100 - (float(test_confusion.trace()) / float(len(learning_and_training_dict["TestLabels"])) * 100)

        time_after = time.time()
        time_elapsed = (time_after - time_before) / 60.0

        print("Training error --> " + str(training_error) + " %")
        print("Test error --> " + str(test_error) + " %")
        print("###################################")
        print("TimeProcessInMinutes ---> : " + str(time_elapsed))
        print("###################################")

        return {"Model": my_trained_svm, "FitTime": time_elapsed, "training_error": training_error, "test_error": test_error, "training_confusionMatrix": training_confusion, "test_confusionMatrix": test_confusion}

    else:

        time_before = time.time()

        # On crée un set de Kfold cross validation
        kf = KFold(n_splits=number_kfolds)
        error_list = []

        for train, test in kf.split(learning_and_training_dict["X"]):

            # Apprentissage du modèle
            my_trained_svm_kfold = my_svm.fit(learning_and_training_dict["X"].iloc[train, ], learning_and_training_dict["Y"].iloc[train, ])
            # Erreur d'apprentissage & Matrice de confusion
            kfold_training_classes_predicted = my_trained_svm_kfold.predict(learning_and_training_dict["X"].iloc[train, ])
            kfold_training_confusion = confusion_matrix(kfold_training_classes_predicted, learning_and_training_dict["Y"].iloc[train, ])
            kfold_training_error = 100 - (float(kfold_training_confusion.trace()) / float(len(learning_and_training_dict["Y"].iloc[train, ])) * 100)
            # Test du modèle & Matrice de confusion
            kfold_test_classes_predicted = my_trained_svm_kfold.predict(learning_and_training_dict["X"].iloc[test, ])
            kfold_test_confusion = confusion_matrix(kfold_test_classes_predicted, learning_and_training_dict["Y"].iloc[test, ])
            kfold_test_error = 100 - (float(kfold_test_confusion.trace()) / float(len(learning_and_training_dict["Y"].iloc[test, ])) * 100)
            error_list.append({"training_error": kfold_training_error, "test_error": kfold_test_error})

        # Calcul de l'erreur moyenne en Train & Test
        mean_error_train = np.mean([elt["training_error"] for elt in error_list])
        std_error_training = np.std([elt["training_error"] for elt in error_list])
        mean_error_testing = np.mean([elt["test_error"] for elt in error_list])
        std_error_test = np.std([elt["test_error"] for elt in error_list])

        time_after = time.time()
        time_elapsed = (time_after - time_before) / 60.0

        print("Mean training error --> " + str(mean_error_train) + " % --- Variance error :" + str(std_error_training**2))
        print("Mean test error --> " + str(mean_error_testing) + " % --- Variance error :" + str(std_error_test**2))
        print("###################################")
        print("TimeProcessInMinutes ---> : " + str(time_elapsed))
        print("###################################")

        return {"Model": my_trained_svm_kfold, "FitTime": time_elapsed, "MeanTrainError": mean_error_train, "VarTrainError": std_error_training**2, "Meantest_error": mean_error_testing, "Vartest_error": std_error_test**2}
