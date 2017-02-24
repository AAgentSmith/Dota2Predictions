# -*- coding: utf-8 -*-
"""
Created on Wed Sep  7 11:17:07 2016

@author: agentsmith
"""

from copy import deepcopy
import pandas as pd


def fill_dataframe(elt, variable_to_fill, data_games, heroes):
    """
        Cette fonction à pour but de remplir un DataFrame avec les données qui ont été collectées sur internet et stockées dans MongoDB.
        Pour cela on effectue un "apply" sur le DataFrame "df" qui a été initialisé à vide, et on remplit/modifie les lignes du DataFrame à partir de la liste
        "data_games" qui contient les matchs sur lesquels on va mener notre analyse.
        args : "elt" représente une ligne du DataFrame sur lequel on applique le "apply"
               "variable_to_fill" indique quelles features doivent être générées
               "data" liste contenant les matchs qui vont être représentés par les lignes du DataFrame résultant
               "heroes" liste des héros
        return : "elt" qui est une ligne du DataFrame représentant un match suite à la génération des features
    """

    # index du match courrant
    temp_game = deepcopy(data_games[elt["index"]])

    # Liste qui contiendra les héros présents dans le match
    list_heroes_id_used = list()

    def game_global_attributes(game, elt=elt):
        """
            Cette fonction à pour but de remplir les attributs globaux relatifs à la partie.
            args : "game" un élément de la liste "data_games" qui va servir à remplir la ligne courrante du DataFrame, qui représente la partie courrante.
                   "elt" la ligne courrante du DataFrame que l'on remplit
            return : "None"
        """

        # Global attributes
        elt['TimeDuration'] = game['duration'] / float(60)
        elt['Victoire'] = game['radiant_win']
        elt['First_Blood_Time'] = game['first_blood_time']

        # Radiant attributes
        elt["Radiant_GPM"] = 0
        elt["Radiant_Hero_Damage"] = 0
        elt["Radiant_XPM"] = 0
        elt["Radiant_Tower_Damage"] = 0
        elt["Radiant_Hero_Healing"] = 0
        elt["Radiant_Levels"] = 0
        elt["Radiant_Denies"] = 0
        elt["Radiant_KDA"] = 0.0
        elt["Radiant_kills"] = 0
        elt["Radiant_assists"] = 0
        elt["Radiant_deaths"] = 0
        elt['Barracks_Status_Radiant'] = game['barracks_status_radiant']
        elt['Towers_Status_Radiant'] = game['tower_status_radiant']

        # Dire attributes
        elt["Dire_GPM"] = 0
        elt["Dire_Hero_Damage"] = 0
        elt["Dire_XPM"] = 0
        elt["Dire_Tower_Damage"] = 0
        elt["Dire_Hero_Healing"] = 0
        elt["Dire_Levels"] = 0
        elt["Dire_Denies"] = 0
        elt["Dire_KDA"] = 0.0
        elt["Dire_kills"] = 0
        elt["Dire_assists"] = 0
        elt["Dire_deaths"] = 0
        elt["match_id"] = temp_game["match_id"]
        elt['Barracks_Status_Dire'] = game['barracks_status_dire']
        elt['Towers_Status_Dire'] = game['tower_status_dire']

        return None

    game_global_attributes(temp_game)

    def heroes_in_game(players_elt, variable_to_fill, elt=elt):
        """
            Cette fonction à pour but de remplir les attributs des joueurs présents dans la partie en parcourant
            la liste des joeurs d'une partie contenue dans l'attribut "players" du match courrant.
            args : "players_elt" un élément de la liste de joueurs de l'attribut "players" du match courrant
                   "variable_to_fill" indique quelles features doivent être générées
                   "elt" la ligne courrante du DataFrame que l'on remplit
            return : "None"
        """

        # ID héros du joueur courrant
        thid = str(players_elt['hero_id'])
        # On ajoute l'ID du héros à la liste des ID des héros présents dans la partie
        list_heroes_id_used.append(thid)

        if variable_to_fill == "Custom":

            if temp_game['players'].index(players_elt) <= 4:

                # Radiant - Presence des héros
                elt["Radiant_Hero_{}_TeamPick".format(thid)] = 1
                elt["Dire_Hero_{}_TeamPick".format(thid)] = 0
                # Radiant - Aggrégation des statistiques relatives aux héros de l'équipe
                elt["Radiant_Golds"] = elt["Radiant_Golds"] + players_elt["gold"] + players_elt["gold_spent"]
                elt["Radiant_Hero_Damage"] = elt["Radiant_Hero_Damage"] + players_elt["hero_damage"]
                elt["Radiant_Xp"] = elt["Radiant_Xp"] + (players_elt["xp_per_min"] * elt["TimeDuration"])
                elt["Radiant_Tower_Damage"] = elt["Radiant_Tower_Damage"] + players_elt["tower_damage"]
                elt["Radiant_Hero_Healing"] = elt["Radiant_Hero_Healing"] + players_elt["hero_healing"]
                elt["Radiant_Levels"] = elt["Radiant_Levels"] + players_elt["level"]
                elt["Radiant_Denies"] = elt["Radiant_Denies"] + players_elt["denies"]
                elt["Radiant_kills"] = elt["Radiant_kills"] + players_elt["kills"]
                elt["Radiant_assists"] = elt["Radiant_assists"] + players_elt["assists"]
                elt["Radiant_deaths"] = elt["Radiant_deaths"] + players_elt["deaths"]
                elt["Radiant_Kda"] = elt["Radiant_Kda"] + float(((float(players_elt["kills"]) + float(players_elt["assists"])) / float(max(players_elt["deaths"], 1)))) * float(1.0 / 5.0)

            else:

                # Dire - Presence des héros
                elt["Dire_Hero_{}_TeamPick".format(thid)] = 1
                elt["Radiant_Hero_{}_TeamPick".format(thid)] = 0
                # Dire - Aggrégation des statistiques relatives aux héros de l'équipe
                elt["Dire_Golds"] = elt["Dire_Golds"] + players_elt["gold"] + players_elt["gold_spent"]
                elt["Dire_Hero_Damage"] = elt["Dire_Hero_Damage"] + players_elt["hero_damage"]
                elt["Dire_Xp"] = elt["Dire_Xp"] + (players_elt["xp_per_min"] * elt["TimeDuration"])
                elt["Dire_Tower_Damage"] = elt["Dire_Tower_Damage"] + players_elt["tower_damage"]
                elt["Dire_Hero_Healing"] = elt["Dire_Hero_Healing"] + players_elt["hero_healing"]
                elt["Dire_Levels"] = elt["Dire_Levels"] + players_elt["level"]
                elt["Dire_Denies"] = elt["Dire_Denies"] + players_elt["denies"]
                elt["Dire_kills"] = elt["Dire_kills"] + players_elt["kills"]
                elt["Dire_assists"] = elt["Dire_assists"] + players_elt["assists"]
                elt["Dire_deaths"] = elt["Dire_deaths"] + players_elt["deaths"]
                elt["Dire_Kda"] = elt["Dire_Kda"] + float(((float(players_elt["kills"]) + float(players_elt["assists"])) / float(max(players_elt["deaths"], 1)))) * float(1.0 / 5.0)

        if(variable_to_fill == "Custom2"):

            if temp_game['players'].index(players_elt) <= 4:

                # Radiant - Presence des héros & statistiques
                elt["Radiant_Hero_{}_TeamPick".format(thid)] = 1
                elt["Dire_Hero_{}_TeamPick".format(thid)] = 0
                elt["Radiant_Hero_{}_Kda".format(thid)] = (players_elt["kills"] + players_elt["assists"]) / float(max(1, players_elt["deaths"]))
                elt["Dire_Hero_{}_Kda".format(thid)] = 0.0
                elt["Radiant_Hero_{}_xp_per_min".format(thid)] = players_elt["xp_per_min"]
                elt["Dire_Hero_{}_xp_per_min".format(thid)] = 0
                elt["Radiant_Hero_{}_hero_damage".format(thid)] = players_elt["hero_damage"]
                elt["Dire_Hero_{}_hero_damage".format(thid)] = 0
                elt["Radiant_Hero_{}_level".format(thid)] = players_elt["level"]
                elt["Dire_Hero_{}_level".format(thid)] = 0
                elt["Radiant_Hero_{}_gold_per_min".format(thid)] = players_elt["gold_per_min"]
                elt["Dire_Hero_{}_gold_per_min".format(thid)] = 0
                elt["Radiant_Hero_{}_gold".format(thid)] = players_elt["gold"]
                elt["Dire_Hero_{}_gold".format(thid)] = 0
                elt["Radiant_Hero_{}_gold_spent".format(thid)] = players_elt["gold_spent"]
                elt["Dire_Hero_{}_gold_spent".format(thid)] = 0
                elt["Radiant_Hero_{}_Items".format(thid)] = [[players_elt["item_" + str(eltitem)]] for eltitem in range(0, 6)]
                elt["Dire_Hero_{}_Items".format(thid)] = ["None"] * 6
                elt["Radiant_Hero_{}_tower_damage".format(thid)] = players_elt["tower_damage"]
                elt["Dire_Hero_{}_tower_damage".format(thid)] = 0
                elt["Radiant_Hero_{}_hero_healing".format(thid)] = players_elt["hero_healing"]
                elt["Dire_Hero_{}_hero_healing".format(thid)] = 0
                elt["Radiant_Hero_{}_last_hits".format(thid)] = players_elt["last_hits"]
                elt["Dire_Hero_{}_last_hits".format(thid)] = 0
                elt["Radiant_Hero_{}_denies".format(thid)] = players_elt["denies"]
                elt["Dire_Hero_{}_denies".format(thid)] = 0
                elt["Radiant_GPM"] = elt["Radiant_GPM"] + (float(players_elt["gold_per_min"]) / 5.0)
                elt["Radiant_Hero_Damage"] = 0 + players_elt["hero_damage"]
                elt["Radiant_XPM"] = elt["Radiant_XPM"] + (float(players_elt["xp_per_min"]) / 5.0)
                elt["Radiant_Tower_Damage"] = elt["Radiant_Tower_Damage"] + players_elt["tower_damage"]
                elt["Radiant_Hero_Healing"] = elt["Radiant_Hero_Healing"] + players_elt["hero_healing"]
                elt["Radiant_Levels"] = elt["Radiant_Levels"] + players_elt["level"]
                elt["Radiant_Denies"] = elt["Radiant_Denies"] + players_elt["denies"]
                elt["Radiant_KDA"] = elt["Radiant_KDA"] + float(((float(players_elt["kills"]) + float(players_elt["assists"])) / float(max(players_elt["deaths"], 1)))) * float(1.0 / 5.0)

            else:

                # Dire - Presence des héros & statistiques
                elt["Dire_Hero_{}_TeamPick".format(thid)] = 1
                elt["Radiant_Hero_{}_TeamPick".format(thid)] = 0
                elt["Dire_Hero_{}_Kda".format(thid)] = (players_elt["kills"] + players_elt["assists"]) / float(max(1, players_elt["deaths"]))
                elt["Radiant_Hero_{}_Kda".format(thid)] = 0.0
                elt["Dire_Hero_{}_xp_per_min".format(thid)] = players_elt["xp_per_min"]
                elt["Radiant_Hero_{}_xp_per_min".format(thid)] = 0
                elt["Radiant_Hero_{}_hero_damage".format(thid)] = 0
                elt["Dire_Hero_{}_hero_damage".format(thid)] = players_elt["hero_damage"]
                elt["Radiant_Hero_{}_level".format(thid)] = 0
                elt["Dire_Hero_{}_level".format(thid)] = players_elt["level"]
                elt["Radiant_Hero_{}_gold_per_min".format(thid)] = 0
                elt["Dire_Hero_{}_gold_per_min".format(thid)] = players_elt["gold_per_min"]
                elt["Radiant_Hero_{}_gold".format(thid)] = 0
                elt["Dire_Hero_{}_gold".format(thid)] = players_elt["gold"]
                elt["Radiant_Hero_{}_gold_spent".format(thid)] = 0
                elt["Dire_Hero_{}_gold_spent".format(thid)] = players_elt["gold_spent"]
                elt["Radiant_Hero_{}_Items".format(thid)] = ["None"] * 6
                elt["Dire_Hero_{}_Items".format(thid)] = [[players_elt["item_" + str(eltitem)]] for eltitem in range(0, 6)]
                elt["Radiant_Hero_{}_tower_damage".format(thid)] = 0
                elt["Dire_Hero_{}_tower_damage".format(thid)] = players_elt["tower_damage"]
                elt["Radiant_Hero_{}_hero_healing".format(thid)] = 0
                elt["Dire_Hero_{}_hero_healing".format(thid)] = players_elt["hero_healing"]
                elt["Radiant_Hero_{}_last_hits".format(thid)] = 0
                elt["Dire_Hero_{}_last_hits".format(thid)] = players_elt["last_hits"]
                elt["Radiant_Hero_{}_denies".format(thid)] = 0
                elt["Dire_Hero_{}_denies".format(thid)] = players_elt["denies"]
                elt["Dire_GPM"] = elt["Dire_GPM"] + (float(players_elt["gold_per_min"]) / 5.0)
                elt["Dire_Hero_Damage"] = 0 + players_elt["hero_damage"]
                elt["Dire_XPM"] = elt["Dire_XPM"] + (float(players_elt["xp_per_min"]) / 5.0)
                elt["Dire_Tower_Damage"] = elt["Dire_Tower_Damage"] + players_elt["tower_damage"]
                elt["Dire_Hero_Healing"] = elt["Dire_Hero_Healing"] + players_elt["hero_healing"]
                elt["Dire_Levels"] = elt["Dire_Levels"] + players_elt["level"]
                elt["Dire_Denies"] = elt["Dire_Denies"] + players_elt["denies"]
                elt["Dire_KDA"] = elt["Dire_KDA"] + float(((float(players_elt["kills"]) + float(players_elt["assists"])) / float(max(players_elt["deaths"], 1)))) * float(1.0 / 5.0)

        return None

    # On remplit les attributs des héros présents
    [heroes_in_game(players_elt, variable_to_fill) for players_elt in temp_game['players']]

    def heroes_not_in_game_attributes(list_heroes_id_used, heroes_elt, variable_to_fill, elt=elt):
        """
            Cette fonction a pour but de définir et remplir les colonnes / attributs relatifs aux héros non présents dans la partie
            args :  "list_heroes_id_used" la liste des héros présents dans la partie
                    "elt" la ligne courrante du DataFrame que l'on remplit
                    "heroes_elt" l'élément courrant de la liste des héros
                    "variable_to_fill" indique les features a générer
            return : "None"
        """

        if str(heroes_elt) not in list_heroes_id_used:

            if variable_to_fill == "Custom":
                # Radiant Hero attributes
                elt["Radiant_Hero_{}_TeamPick".format(heroes_elt)] = 0
                # Dire Hero attributes
                elt["Dire_Hero_{}_TeamPick".format(heroes_elt)] = 0

            elif(variable_to_fill == "Custom2"):

                for team in ["Dire", "Radiant"]:

                    elt["{}_Hero_{}_TeamPick".format(team, heroes_elt)] = 0
                    elt["{}_Hero_{}_Kda".format(team, heroes_elt)] = 0.0
                    elt["{}_Hero_{}_xp_per_min".format(team, heroes_elt)] = 0
                    elt["{}_Hero_{}_hero_damage".format(team, heroes_elt)] = 0
                    elt["{}_Hero_{}_level".format(team, heroes_elt)] = 0
                    elt["{}_Hero_{}_gold_per_min".format(team, heroes_elt)] = 0
                    elt["{}_Hero_{}_gold".format(team, heroes_elt)] = 0
                    elt["{}_Hero_{}_gold_spent".format(team, heroes_elt)] = 0
                    elt["{}_Hero_{}_Items".format(team, heroes_elt)] = ["None"] * 6
                    elt["{}_Hero_{}_tower_damage".format(team, heroes_elt)] = 0
                    elt["{}_Hero_{}_hero_healing".format(team, heroes_elt)] = 0
                    elt["{}_Hero_{}_last_hits".format(team, heroes_elt)] = 0
                    elt["{}_Hero_{}_denies".format(team, heroes_elt)] = 0
                    elt["{}_Hero_{}_GPM".format(team, heroes_elt)] = 0
                    elt["{}_Hero_Damage".format(team, heroes_elt)] = 0
                    elt["{}_Hero_{}_XPM".format(team, heroes_elt)] = 0
                    elt["{}_Hero_{}_Tower_Damage".format(team, heroes_elt)] = 0
                    elt["{}_Hero_Healing".format(team, heroes_elt)] = 0
                    elt["{}_Hero_{}_Levels".format(team, heroes_elt)] = 0
                    elt["{}_Hero_{}_Denies".format(team, heroes_elt)] = 0
                    elt["{}_Hero_{}_KDA".format(team, heroes_elt)] = 0

        return None

    # On remplit les attributs des héros non présents
    heroes_id = [eltheroes["id"] for eltheroes in heroes]
    [heroes_not_in_game_attributes(list_heroes_id_used, heroes_elt, variable_to_fill) for heroes_elt in heroes_id]

    # Cette partie du code à pour objectif de mettre en forme les features
    if variable_to_fill == "Custom2":

        # Constitution le la ligne représentant les statistiques de l'équipe
        radiant_heroes_id = list_heroes_id_used[0:5]
        dire_heroes_id = list_heroes_id_used[5:10]

        if(variable_to_fill == "Custom2"):
            # Construction du dictionnaire de héros dont on va se servir pour construire les colonnes de notre DataFrame
            heroes_dict = {str(elt["id"]): elt["localized_name"] for elt in heroes}

            # On va construire les colonnes de chaque équipe en les triant par leurs niveau de gold par minutes descendant
            radiant_heroes_stats = [(elt["Radiant_Hero_" + eltheroes + "_gold_per_min"], elt["Radiant_Hero_" + eltheroes + "_xp_per_min"], elt["Radiant_Hero_" + eltheroes + "_hero_damage"]) for eltheroes in radiant_heroes_id]
            radiant_heroes_stats.sort(reverse=True, key=lambda x: (x[0], x[1], x[2]))
            dire_heroes_stats = [(elt["Dire_Hero_" + eltheroes + "_gold_per_min"], elt["Dire_Hero_" + eltheroes + "_xp_per_min"], elt["Dire_Hero_" + eltheroes + "_hero_damage"]) for eltheroes in dire_heroes_id]
            dire_heroes_stats.sort(reverse=True, key=lambda x: (x[0], x[1], x[2]))
            # Position de chacun des héros vis à vis de l'indicateur de gold par minutes
            radiant_heroes_id_position = [(int(eltheroes), radiant_heroes_stats.index((elt["Radiant_Hero_" + eltheroes + "_gold_per_min"], elt["Radiant_Hero_" + eltheroes + "_xp_per_min"], elt["Radiant_Hero_" + eltheroes + "_hero_damage"]))) for eltheroes in radiant_heroes_id]
            dire_heroes_id_position = [(int(eltheroes), dire_heroes_stats.index((elt["Dire_Hero_" + eltheroes + "_gold_per_min"], elt["Dire_Hero_" + eltheroes + "_xp_per_min"], elt["Dire_Hero_" + eltheroes + "_hero_damage"]))) for eltheroes in dire_heroes_id]

        else:
            # On va construire les colonnes de chaque équipe en les triant par leurs niveau de gold par minutes descendant
            radiant_heroes_stats = [(elt["Radiant_Hero_" + eltheroes + "_gold_per_min"], elt["Radiant_Hero_" + eltheroes + "_xp_per_min"], elt["Radiant_Hero_" + eltheroes + "_hero_damage"]) for eltheroes in radiant_heroes_id]
            radiant_heroes_stats.sort(reverse=True, key=lambda x: (x[0], x[1], x[2]))
            dire_heroes_stats = [(elt["Dire_Hero_" + eltheroes + "_gold_per_min"], elt["Dire_Hero_" + eltheroes + "_xp_per_min"], elt["Dire_Hero_" + eltheroes + "_hero_damage"]) for eltheroes in dire_heroes_id]
            dire_heroes_stats.sort(reverse=True, key=lambda x: (x[0], x[1], x[2]))
            # Position de chacun des héros vis à vis de l'indicateur de gold par minutes
            radiant_heroes_id_position = [(int(eltheroes), radiant_heroes_stats.index((elt["Radiant_Hero_" + eltheroes + "_gold_per_min"], elt["Radiant_Hero_" + eltheroes + "_xp_per_min"], elt["Radiant_Hero_" + eltheroes + "_hero_damage"]))) for eltheroes in radiant_heroes_id]
            dire_heroes_id_position = [(int(eltheroes), dire_heroes_stats.index((elt["Dire_Hero_" + eltheroes + "_gold_per_min"], elt["Dire_Hero_" + eltheroes + "_xp_per_min"], elt["Dire_Hero_" + eltheroes + "_hero_damage"]))) for eltheroes in dire_heroes_id]

        # Liste des colonnes crées pour chacun des 5 héros de chaque équipe
        vector_stats_dual = {}
        for team in ["Radiant_Hero_", "Dire_Hero_"]:

            if(team == "Radiant_Hero_"):
                HeroesPosition = radiant_heroes_id_position

            else:
                HeroesPosition = dire_heroes_id_position

            for eltTupleHeroesIdPosition in HeroesPosition:

                vector_stats_dual[team + str(eltTupleHeroesIdPosition[1]) + "_KDA"] = elt[team + str(eltTupleHeroesIdPosition[0]) + "_Kda"]
                vector_stats_dual[team + str(eltTupleHeroesIdPosition[1]) + "_GPM"] = elt[team + str(eltTupleHeroesIdPosition[0]) + "_gold_per_min"]
                vector_stats_dual[team + str(eltTupleHeroesIdPosition[1]) + "_XPM"] = elt[team + str(eltTupleHeroesIdPosition[0]) + "_xp_per_min"]
                vector_stats_dual[team + str(eltTupleHeroesIdPosition[1]) + "_Level"] = elt[team + str(eltTupleHeroesIdPosition[0]) + "_level"]
                vector_stats_dual[team + str(eltTupleHeroesIdPosition[1]) + "_Damage"] = elt[team + str(eltTupleHeroesIdPosition[0]) + "_hero_damage"]

                if(variable_to_fill == "Custom2"):
                    vector_stats_dual[team + str(eltTupleHeroesIdPosition[1]) + "_Hero_Name"] = heroes_dict[str(eltTupleHeroesIdPosition[0])]
                    vector_stats_dual[team + str(eltTupleHeroesIdPosition[1]) + "_Items"] = elt[team + str(eltTupleHeroesIdPosition[0]) + "_Items"]
                    vector_stats_dual[team + str(eltTupleHeroesIdPosition[1]) + "_Denies"] = elt[team + str(eltTupleHeroesIdPosition[0]) + "_denies"]

        vector_stats_dual["Victoire"] = elt["Victoire"]
        vector_stats_dual["TimeDuration"] = elt["TimeDuration"]
        vector_stats_dual["index"] = elt["index"]

        if(variable_to_fill == "Custom2"):

            # On ajoute les colonnes de présences des héros
            for elt_index in elt.index:

                if("TeamPick" in elt_index):
                    vector_stats_dual[elt_index] = elt[elt_index]

            for team in ["Radiant", "Dire"]:

                vector_stats_dual[team + "_Hero_Damage"] = elt[team + "_Hero_Damage"]
                vector_stats_dual[team + "_XPM"] = elt[team + "_XPM"]
                vector_stats_dual[team + "_Tower_Damage"] = elt[team + "_Tower_Damage"]
                vector_stats_dual[team + "_Hero_Healing"] = elt[team + "_Hero_Healing"]
                vector_stats_dual[team + "_Levels"] = elt[team + "_Levels"]
                vector_stats_dual[team + "_KDA"] = elt[team + "_KDA"]
                vector_stats_dual[team + "_GPM"] = elt[team + "_GPM"]

            # Variable catégorielle représentant le temps de la partie
            if(vector_stats_dual["TimeDuration"] <= 20):
                vector_stats_dual["TimeDurationCategorial"] = "Under20Minutes"

            elif(20 < vector_stats_dual["TimeDuration"] <= 30):
                vector_stats_dual["TimeDurationCategorial"] = "20-30Minutes"

            elif(30 < vector_stats_dual["TimeDuration"] <= 40):
                vector_stats_dual["TimeDurationCategorial"] = "30-40Minutes"

            elif(40 < vector_stats_dual["TimeDuration"] <= 50):
                vector_stats_dual["TimeDurationCategorial"] = "40-50Minutes"

            elif(50 < vector_stats_dual["TimeDuration"] <= 60):
                vector_stats_dual["TimeDurationCategorial"] = "50-60Minutes"

            else:
                vector_stats_dual["TimeDurationCategorial"] = "More1Hour"

            # Ajout du "match_id"
            vector_stats_dual["match_id"] = elt["match_id"]

        elt = pd.Series(vector_stats_dual)

        return elt

    # On retourne l'élément courrant modifié et rempli
    else:

        return elt
