# -*- coding: utf-8 -*-
"""
Created on Wed Sep  7 11:17:07 2016

@author: agentsmith
"""

import pandas as pd
import random as rand
import time


def data_processing(var_init, nb_data, list_of_matches=[]):
    """
        Cette fonction à pour but de selectionner aléatoirement des individus parmi l'ensemble des observations vérifiant les critères requis
        afin de construire notre modèle d'apprentissage dessus, depuis la collection mongoDB contenant les matchs filtrés.
        Les noms des colonnes qui seront utilisées dans les DataFrame générés ultérieurement sont initialisées.
        args : "var_init" le résultat de la fonction "var_init()" qui contient les matchs, les héros et les items
               "nb_data" le nombre de matchs que l'on retient
               "list_of_matches" une liste de match_id si l'on souhaite des matchs en particulier
        return : dictionnaire contenant
    """

    time_before = time.time()

    # Si une liste de match est fournie on récupère ces matchs
    if(len(list_of_matches) != 0):
        data = [eltmatches for eltmatches in var_init["DataList"] if (eltmatches["match_id"] in list_of_matches)]
    # Sinon on effectue une selection aléatoire
    else:
        # On selectionne autant de matchs ou le Radiant gagne que le Dire gagne
        radiant_win = [elt for elt in var_init["DataList"] if elt["radiant_win"]]
        radiant_win = rand.sample(radiant_win, nb_data / 2)
        data_filtered2 = radiant_win + rand.sample([elt for elt in var_init["DataList"] if elt["radiant_win"] is not True], nb_data / 2)
        data_filtered3 = data_filtered2
        data = rand.sample(data_filtered3, nb_data)

    # On cree le DataFrame
    df = pd.DataFrame()
    # On crée une colonne suplémentaire "index" qui sera utilisé lors du "apply" sur le DataFrame
    df["index"] = range(0, len(data))

    time_after = time.time()
    time_elapsed = (time_after - time_before) / 60.0

    return {"TimeProcessInMinutes": time_elapsed, "Results": {"DataFrame": df, "Data": data, "HeroesList": var_init["HeroesList"]}}
