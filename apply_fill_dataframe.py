# -*- coding: utf-8 -*-
"""
Created on Wed Sep  7 11:17:07 2016

@author: agentsmith
"""

import numpy as np
import pandas as pd
import time
from fill_dataframe import fill_dataframe


def apply_fill_dataframe(data_process, variable_to_fill):
    """
        Cette fonction remplit le DataFrame passé en entrée et produit 2 outputs : Un DataFrame représentant la présence des héros dans une partie
        et un DataFrame représentant les statistiques des deux équipes d'une partie
        args : "data_process" le résultat de la fonction "data_process" contenue dans "data_process.py" qui contient les données
               "variable_to_fill" indique les features qui devront être construite dans la fonction "fill_dataframe" contenue dans "fill_dataframe.py"
    """

    time_before = time.time()

    # On récupère la liste des données issues de MongoDB
    data = data_process["Results"]["Data"]
    # On récupère la liste des héros
    heroes = data_process["Results"]["HeroesList"]
    # On récupère le DataFrame que l'on va modifier
    df = data_process["Results"]["DataFrame"]
    # Sur chacune des lignes du DataFrame on applique la fonction "fill_dataframe" contenue dans "fill_dataframe.py"
    df_apply_result = df.apply(fill_dataframe, axis=1, args=(variable_to_fill, data, heroes,)).drop("index", 1)

    # Index des valeurs manquantes dans le DataFrame construit
    nan_index_list = []
    for i in range(0, len(df_apply_result)):
        if(True in pd.isnull(df_apply_result.iloc[i, :].values)):
            nan_index_list.append(i)
    if(len(nan_index_list) > 0):
        print("############ WARNING #####################\n############ EXISTENCE DE NAN ############")
    else:
        print("############ PAS DE NAN ############")

    # Split du DataFrame précédent en 2 et supression des colonnes non utiles qui ont servies à construire les autres colonnes utiles
    if(variable_to_fill in ["Custom", "Custom2"]):

        # 1) DataFrame représentant la présence des héros dans chaque équipe
        dataframe_heroes_presences_columns = [elt for elt in df_apply_result.columns if ("_TeamPick" in elt)] + ["Victoire"]
        dataframe_heroes_presences = df_apply_result.loc[:, dataframe_heroes_presences_columns]

        # 2) DataFrame représentant les statistiques des deux équipes
        if(variable_to_fill == "Custom"):
            dataframe_team_stats_columns = ["Radiant_Golds", "Radiant_Hero_Damage", "Radiant_Xp", "Radiant_Hero_Healing", "Radiant_Levels", "Radiant_Denies", "Radiant_Kda", "Dire_Golds", "Dire_Hero_Damage", "Dire_Xp", "Dire_Hero_Healing", "Dire_Levels", "Dire_Denies", "Dire_Kda", "Victoire"]
            dataframe_team_stats = df_apply_result.loc[:, dataframe_team_stats_columns]

            time_after = time.time()
            time_elapsed = (time_after - time_before) / 60.0

            print("###################################")
            print("TimeProcessInMinutes ---> : {}".format(time_elapsed))
            print("###################################")

            return {"TimeProcessInMinutes": time_elapsed, "Results": {"Presences": dataframe_heroes_presences, "TeamsStats": dataframe_team_stats}}

        elif(variable_to_fill == "Custom2"):
            # Récupération des colonnes et construction du DataFrame
            DfHeroesPresencesColumns = [eltcolumn for eltcolumn in df_apply_result.columns if ("TeamPick" in eltcolumn)] + ["Victoire"]
            DfHeroesPresences = df_apply_result.loc[:, DfHeroesPresencesColumns]
            # Récupération des colonnes et construction du DataFrame
            dataframe_team_stats_classif_columns = [eltcolumn for eltcolumn in df_apply_result.columns if (("_Denies" not in eltcolumn) & ("_Items" not in eltcolumn) & ("_Hero_Name" not in eltcolumn) & ("TeamPick" not in eltcolumn) & (("Radiant_Hero_" in eltcolumn) or ("Dire_Hero_" in eltcolumn)))] + ["Victoire", "TimeDuration"]
            dataframe_team_statsClassif = df_apply_result.loc[:, dataframe_team_stats_classif_columns]
            # Récupération des colonnes et construction du DataFrame
            dataframe_team_stats_global_columns = [eltcolumn for eltcolumn in df_apply_result.columns if (("TeamPick" not in eltcolumn) & (("Radiant_" in eltcolumn) or ("Dire_" in eltcolumn)))] + ["Victoire", "TimeDuration"]
            dataframe_stats_global_and_heroes = df_apply_result.loc[:, list(np.unique(dataframe_team_stats_classif_columns + dataframe_team_stats_global_columns))]

            time_after = time.time()
            time_elapsed = (time_after - time_before) / 60.0

            print("###################################")
            print("TimeProcessInMinutes ---> : {}".format(time_elapsed))
            print("###################################")

            return {"TimeProcessInMinutes": time_elapsed, "Results": {"Presences": DfHeroesPresences, "TeamsStats": dataframe_team_statsClassif, "Global": dataframe_stats_global_and_heroes}}

        return {"TimeProcessInMinutes": time_elapsed, "Results": df_apply_result}
