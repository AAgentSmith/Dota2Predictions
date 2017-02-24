# -*- coding: utf-8 -*-
"""
Created on Wed Sep  7 11:17:07 2016

@author: agentsmith
"""

import numpy as np
import time
import pandas as pd
import matplotlib.pyplot as mpl
from sklearn.metrics import confusion_matrix
from sklearn.model_selection import KFold
from sklearn.linear_model import LogisticRegression


def logistic_regression_model(learning_and_training_dict, kfold_cross_validation, number_kfolds):
    """
        Cette fonction réalise une modélisation par régression logistique.
        args : "learning_and_training_dict" : dictionnaire qui contient les données d'apprentissage et de test
               "kfold_cross_validation" : true ou false selon kfold cross validation
               "number_kfolds" : nombre de kfolds
        return : un dictionnaire contenant le modèle, les erreurs de test et d'apprentissage ainsi que le temps de calcul
    """

    if not kfold_cross_validation:

        time_before = time.time()
        # On crée une instance de "LogisticRegression"
        logit = LogisticRegression()
        # Apprentissage du modèle
        my_logistic_regression_trained = logit.fit(learning_and_training_dict["TrainingFeatures"], learning_and_training_dict["TrainingLabels"])
        time_after = time.time()
        time_elapsed = (time_after - time_before) / 60.0
        # Erreur d'apprentissage & Matrice de confusion
        training_labels_predicted = my_logistic_regression_trained.predict(learning_and_training_dict["TrainingFeatures"])
        training_confusion = confusion_matrix(training_labels_predicted, learning_and_training_dict["TrainingLabels"])
        training_error = 100 - (float(training_confusion.trace()) / float(len(learning_and_training_dict["TrainingLabels"])) * 100)
        # Test du modèle & Matrice de confusion
        test_labels_predicted = my_logistic_regression_trained.predict(learning_and_training_dict["TestFeatures"])
        test_confusion = confusion_matrix(test_labels_predicted, learning_and_training_dict["TestLabels"])
        test_error = 100 - (float(test_confusion.trace()) / float(len(learning_and_training_dict["TestLabels"])) * 100)

        # Construction de la courbe ROC #
        # Prediction des probabilité d'appartenances à chacune des deux classes pour les données de test
        test_proba_predicted = my_logistic_regression_trained.predict_proba(learning_and_training_dict["TestFeatures"])
        # On crée un DataFrame contenant le label de l'individu ainsi que la probabilité prédite par le modèle de régression logistique (On trie dans un ordre décroissant)
        predicted_proba_dataframe = pd.DataFrame(np.stack((learning_and_training_dict["TestLabels"], test_proba_predicted[:, 0], test_proba_predicted[:, 1]), -1), columns=["Label", "Proba_False", "Proba_True"])
        predicted_proba_dataframe["Label_By_Proba_True"] = pd.Series()
        predicted_proba_dataframe = predicted_proba_dataframe.sort(columns="Proba_True", ascending=False)

        roc_dataframe = []
        for seuil in np.arange(0, 1.05, 0.05):

            predicted_proba_dataframe["Label_By_Proba_True"] = predicted_proba_dataframe.apply(lambda elt: int(elt["Proba_True"] >= seuil), 1)
            tep_confusion_matrix = confusion_matrix(y_true=predicted_proba_dataframe["Label"], y_pred=predicted_proba_dataframe["Label_By_Proba_True"], labels=[False, True])
            true_positives_rate = float(tep_confusion_matrix[1, 1]) / (tep_confusion_matrix[1, 0] + tep_confusion_matrix[1, 1])
            false_positives_rate = float(tep_confusion_matrix[0, 1]) / (tep_confusion_matrix[0, 0] + tep_confusion_matrix[0, 1])

            if(seuil == 0.5):
                true_positives_rate05 = true_positives_rate
                false_positives_rate05 = false_positives_rate

            roc_dataframe.append({"Seuil": seuil, "true_positives_rate": true_positives_rate, "false_positives_rate": false_positives_rate})

        roc_dataframe = pd.DataFrame(roc_dataframe)
        roc_dataframe = roc_dataframe.sort(columns="Seuil", ascending=False)

        # Calcul de area_under_curve "Area Under the Curve"
        area_under_curve = np.trapz(roc_dataframe["true_positives_rate"], roc_dataframe["false_positives_rate"])

        fig = mpl.figure()
        ax = fig.add_subplot(111)
        ax.plot(roc_dataframe["false_positives_rate"], roc_dataframe["true_positives_rate"])
        ax.plot(np.arange(0, 1.05, 0.05), np.arange(0, 1.05, 0.05))
        ax.axhline(true_positives_rate05, color="red")
        ax.axvline(false_positives_rate05, color="red")
        ax.set_xlabel("Taux de faux positifs")
        ax.set_ylabel("Taux de vrais positifs")
        ax.set_title("Courbe ROC - area_under_curve = " + str(round(area_under_curve, 2)))
        mpl.show()

        print("Training error --> " + str(training_error) + " %")
        print("Test error --> " + str(test_error) + " %")
        print("###################################")
        print("TimeProcessInMinutes ---> : " + str(time_elapsed))
        print("###################################")

        return {"Model": my_logistic_regression_trained, "FitTime": time_elapsed, "training_error": training_error, "test_error": test_error, "training_confusionMatrix": training_confusion, "test_confusionMatrix": test_confusion}

    else:

        time_before = time.time()
        # On crée une instance de "LogisticRegression"
        logit = LogisticRegression()
        # On crée un set de Kfold cross validation
        kf = KFold(n_splits=number_kfolds)
        error_list = []

        for train, test in kf.split(learning_and_training_dict["X"]):

            # Apprentissage du modèle
            kfold_my_logistic_regression_trained = logit.fit(learning_and_training_dict["X"].iloc[train, ], learning_and_training_dict["Y"].iloc[train, ])
            # Erreur d'apprentissage & Matrice de confusion
            kfold_training_classes_predicted = kfold_my_logistic_regression_trained.predict(learning_and_training_dict["X"].iloc[train, ])
            kfold_training_confusion = confusion_matrix(kfold_training_classes_predicted, learning_and_training_dict["Y"].iloc[train, ])
            kfold_training_error = 100 - (float(kfold_training_confusion.trace()) / float(len(learning_and_training_dict["Y"].iloc[train, ])) * 100)
            # Test du modèle & Matrice de confusion
            kfold_test_classes_predicted = kfold_my_logistic_regression_trained.predict(learning_and_training_dict["X"].iloc[test, ])
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

        return {"Model": kfold_my_logistic_regression_trained, "FitTime": time_elapsed, "MeanTrainError": mean_error_train, "VarTrainError": std_error_training**2, "Meantest_error": mean_error_testing, "Vartest_error": std_error_test**2}
