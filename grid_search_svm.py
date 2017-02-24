# -*- coding: utf-8 -*-
"""
Created on Wed Sep  7 11:17:07 2016

@author: agentsmith
"""

from sklearn import svm
from sklearn.model_selection import GridSearchCV
from sklearn.metrics import classification_report


def grid_search_svm(learning_and_training_dict, parameters, number_kfolds=5):
    """
        Cette fonction à pour but d'estimer les meilleurs paramètres d'un modèle de Support Vector Machine par cross validation sur l'ensemble d'apprentissage, on spécifiera le nombre de Kfold.
        args : "learning_and_training_dict" : dictionnaire qui contient les données d'apprentissage et de test
               "kfold_cross_validation" : true ou false selon kfold cross validation
               "number_kfolds" : nombre de kfolds
        return : dictionnaire contenant les meilleurs paramètres
    """

    # On crée une instance de modèle SVM
    svr = svm.SVC()
    clf = GridSearchCV(svr, parameters, cv=number_kfolds)
    clf.fit(learning_and_training_dict["TrainingFeatures"], learning_and_training_dict["TrainingLabels"])

    print("Best parameters set found on development set:")
    print()
    print(clf.best_params_)
    print()
    print("Grid scores on development set:")
    print()

    means = clf.cv_results_['mean_test_score']
    stds = clf.cv_results_['std_test_score']

    for mean, std, params in zip(means, stds, clf.cv_results_['params']):
        print("%0.3f (+/-%0.03f) for %r"
              % (mean, std * 2, params))

    print("Detailed classification report:")
    print("The model is trained on the full development set.")
    print("The scores are computed on the full evaluation set.")

    y_true, y_pred = learning_and_training_dict["TestLabels"], clf.predict(learning_and_training_dict["TestFeatures"])

    print(classification_report(y_true, y_pred))

    # La fonction retourne le dictionnaire contenant les meilleurs paramètres
    return clf.best_params_
