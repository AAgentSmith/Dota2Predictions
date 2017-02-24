# -*- coding: utf-8 -*-
"""
Created on Wed Sep  7 11:17:07 2016

@author: agentsmith
"""

from api_steam_data_query import api_steam_data_query
from var_init import var_init
from data_process import data_processing
from apply_fill_dataframe import apply_fill_dataframe
from create_learning_and_testing_sets import create_learning_and_testing_sets
from logistic_regression import logistic_regression_model
from support_vector_machine import support_vector_machine_model
from grid_search_svm import grid_search_svm
from serialization import serialization
import os


# Récupération des données sur l'Api Steam
api_steam_data_query()

# Récupération des données depuis la base MongoDB
var_init = var_init("Dota2DataBase", "matchsFiltered", "heroeslistdb", "itemslistdb")

# Selection des données d'analyse
data_process = data_processing(var_init, 100)

# Construction des DataFrame à partir des données selectionnées
apply_fill_dataframe = apply_fill_dataframe(data_process, "Custom2")

# On dispose de trois DataFrame à ce stade :
# apply_fill_dataframe["Results"]["Presences"] DataFrame représentant la présence des héros dans un match
# apply_fill_dataframe["Results"]["TeamsStats"] DataFrame représentant les descripteurs des héros présents dans le match
# apply_fill_dataframe["Results"]["Global"] DataFrame représentant la partie au global

# Creation du dictionnaire contenant les jeux d'apprentissage et de test à partir du DataFrame représentant la présence des héros dans la partie, 70 % Train & 30 % Test
learning_and_testings_sets = create_learning_and_testing_sets(apply_fill_dataframe["Results"]["Presences"], 0.7)

# Modélisation par régression logistique
logistic_regression = logistic_regression_model(learning_and_testings_sets, False, 0)

# Meilleurs paramètres pour modélisation par support vector machine - Grid Search
svm_best_parameters = grid_search_svm(learning_and_testings_sets,
                                      [{'kernel': ['linear'], 'C': [1, 10, 100]}, {'kernel': ['rbf', 'poly', 'sigmoid'],
                                       'C':[1, 10, 100], 'gamma':[0.1, 0.01, 0.001]}])

# Modélisation par support vector machine avec liste de paramètres fixés
support_vector_machine = support_vector_machine_model(learning_and_testings_sets, False, 0, svm_best_parameters)

# Serialization des modèles pour utilisation ultèrieure
serialization(logistic_regression["Model"], "/home/agentsmith/", "my_logistic_model", True)
serialization(support_vector_machine["Model"], "/home/agentsmith/", "my_svm_model", True)

# Simulation d'une phase de pick / lancer le script "pick_coaching.py" avec la commande bokeh serv
os.chdir("/media/agentsmith/D64C25154C24F1C3/Work/Travaux/Dota2Predictions")
os.system("bokeh serve pick_coaching.py")
