# -*- coding: utf-8 -*-
"""
Created on Wed Sep  7 11:17:07 2016

@author: agentsmith
"""

from __future__ import print_function
import numpy as np
import jsonlines
from scipy.spatial.distance import hamming


def matches_similarity_by_team(heroes_in_match, matches_base, heroes_file):
    """
        Cette fonction à pour objectif d'extraire les matchs similaires de la liste des matchs dont on dispose déja
        au match qui va se dérouler en termes de héros présents dans la partie.
        1) Si on fournit une list de 10 héros alors on va calculer la similiratité entre les matchs en base et celui dont on dispose (en termes de héros présents).
        2) Si on fournit un dictionnaire contenant les champs "Equipe1": listedeherosradiant & "Equipe2": listedeherosdire alors on extrait les matchs qui font matcher exactement
            les héros précisés.
        3) heroes_in_match : list ou dictionnaire
           matches_base : une liste de match contenant le détail des héros présents dans le match
           heroes_file
    """

    # 1) Calcul des indices de similarité :
    if((type(heroes_in_match) == list) & (len(heroes_in_match) == 10)):
        # Construction des colonnes représentant la présences des héros
        heroes = []
        # On recupere tous les id des heros
        with jsonlines.open(heroes_file) as reader:
            for obj in reader:
                heroes.append(obj['id'])

        radiant_heroes_presences = ["Radiant_Hero_" + str(elt) + "_TeamPick" for elt in heroes]
        dire_heroes_presences = ["Dire_Hero_" + str(elt) + "_TeamPick" for elt in heroes]

        # Première fonction de construction
        def fill_series_of_presence(list_presences, heroes_in_match, heroes, hero):

            if hero in heroes_in_match[0:5]:
                list_presences[heroes.index(hero)] = 1
                list_presences[111 + heroes.index(hero)] = 0
            elif hero in heroes_in_match[5:]:
                list_presences[heroes.index(hero)] = 0
                list_presences[111 + heroes.index(hero)] = 1
            else:
                list_presences[heroes.index(hero)] = 0
                list_presences[111 + heroes.index(hero)] = 0

        # Deuxieme fonction de construction
        def fill_series_of_presenceMain(list_presences, heroes_in_match, heroes):

            list_presences = list_presences * len(heroes) * 2
            # On applique la sfonction pour chsaque "hero_id": dont on dispose
            [fill_series_of_presence(list_presences, heroes_in_match, heroes, elthero) for elthero in heroes]
            return list_presences

        # Vecteur de présence des héros pour les parties dont on dispose en base
        # Construction du vecteur de présences pour les parties dont on dispose en base
        list_of_heroes_presences_base_matches_filtered = [(eltmatches[0], fill_series_of_presenceMain([None], eltmatches[1], heroes)) for eltmatches in matches_base]

        # Fonction qui calcule la distance entre un match et la liste des matchs en base
        def distance_current_match_and_matchs_in_base(heroes_in_match, presences_matchs_in_base, heroes):

            # On construit le vecteur de présence des héros pour la partie courrante
            atual_heroes_presences = fill_series_of_presenceMain([None], heroes_in_match, heroes)
            # Calcul des distances entre vecteur de présence de héros - Distance de Hamming
            list_of_distances = [(elt[0], hamming(atual_heroes_presences, elt[1])) for elt in presences_matchs_in_base]
            # On trie la liste des (matchs_id, distance)
            list_of_distances.sort(key=lambda x: int(x[0]), reverse=True)
            # On renvoie la liste contenant les distances entre les matchs et leurs id
            return list_of_distances
        # Premier calcul de distance pour la composition Radiant : equipe_1 & Dire : equipe_2
        first_side_distances = distance_current_match_and_matchs_in_base(heroes_in_match, list_of_heroes_presences_base_matches_filtered, heroes)
        # Second calcul de distance pour la composition Radiant : equipe_2 & Dire : equipe_1
        heroes_in_match = heroes_in_match[5:10] + heroes_in_match[0:5]
        second_side_distances = distance_current_match_and_matchs_in_base(heroes_in_match, list_of_heroes_presences_base_matches_filtered, heroes)
        # On selectionne la distance minimale par rapport aux matchs en base
        select_minimal_hamming_similarity = [(first_side_distances[elt_index][0], min(first_side_distances[elt_index][1], second_side_distances[elt_index][1])) for elt_index in range(0, len(first_side_distances))]
        select_minimal_hamming_similarity.sort(key=lambda x: x[1])
        list_of_distances = [elt[1] for elt in select_minimal_hamming_similarity]
        # Valeurs de similarités calculées uniques
        uniques_distances = np.unique(list_of_distances)
        # Valeurs de similarité possibles
        possibles_similarity_values = {str(elt): round((elt * 2) / 222.0, 8) for elt in range(1, 11)}
        # Heatmap du calcul de similarité
        reverse_dictionnary = dict((v, k) for k, v in possibles_similarity_values.iteritems())
        index_similarity_values = [(reverse_dictionnary[round(elt, 8)], elt) for elt in list_of_distances]
        # Indexation du nombre de matchs avec un nombre de héros en communs avec le match courrant
        intkeylist = [int(eltkey) for eltkey in possibles_similarity_values.keys()]
        intkeylist.sort(reverse=True)
        # Affichage d'informations
        print("############ INFORMATIONS SUR LE NOMBRE DE MATCHS EN BASE AVEC UN CERTAIN NOMBRE DE HEROS EN COMMUN AVEC LA PARTIE COURRANTE ############")
        for key in intkeylist:
            tempitems = len([elt for elt in index_similarity_values if (elt[0] == str(10 - key))])
            print("############ " + str(key) + " HEROS EN COMMUN ############")
        # Selection des matchs avec un nombre de héros en communs choisit
        matchs_similar_id = []
        commun = [1, 2, 3, 4, 5, 6, 7, 8, 9]
        for eltcommun in commun:
            similarity_values_commun = possibles_similarity_values[str(10 - eltcommun)]
            matchs_communs_id = [elt[0] for elt in select_minimal_hamming_similarity if (round(elt[1], 8) == similarity_values_commun)]
            matchs_similar_id.append((eltcommun, matchs_communs_id))
            matchs_similar_iddict = {elt[0]: elt[1] for elt in matchs_similar_id}
        return matchs_similar_iddict
    # 2) Extraction des matchs qui match les héros spécfiés dans chaque équipe
    elif(type(heroes_in_match) == dict):
        matchs_id_check_heroes = []

        # Fonction qui regarde si les heros spécifiés sont présents dans la liste des héros d'un match en base
        def check_heroes_presences(specified_heroes, elt_match_base, matchs_id_check_heroes):
            # On attribue à la variable "specified_heroes" la liste des héros du matchs en base courant
            heroesbase = elt_match_base[1]
            # On considère alternativement les deux équipes en Radiant & Dire
            # Side 1
            equipe1_heroes = specified_heroes[specified_heroes.keys()[0]]
            first_side_equipe1_heroes_check = [elt in heroesbase[0:5] for elt in equipe1_heroes]
            if((len(np.unique(first_side_equipe1_heroes_check)) == 1) & (np.unique(first_side_equipe1_heroes_check)[0])):
                first_side_equipe1_heroes_check = True
            else:
                first_side_equipe1_heroes_check = False
            equipe2_heroes = specified_heroes[specified_heroes.keys()[1]]
            first_side_equipe2_heroes_check = [elt in heroesbase[5:10] for elt in equipe2_heroes]
            if((len(np.unique(first_side_equipe2_heroes_check)) == 1) & (np.unique(first_side_equipe2_heroes_check)[0])):
                first_side_equipe2_heroes_check = True
            else:
                first_side_equipe2_heroes_check = False
            if((first_side_equipe2_heroes_check) & (first_side_equipe1_heroes_check)):
                first_side_check = True
            else:
                first_side_check = False
            # Side 2
            equipe1_heroes = specified_heroes[specified_heroes.keys()[0]]
            second_side_equipe1_heroes_check = [elt in heroesbase[5:10] for elt in equipe1_heroes]
            if((len(np.unique(second_side_equipe1_heroes_check)) == 1) & (np.unique(second_side_equipe1_heroes_check)[0])):
                second_side_equipe1_heroes_check = True
            else:
                second_side_equipe1_heroes_check = False
            equipe2_heroes = specified_heroes[specified_heroes.keys()[1]]
            second_side_equipe2_heroes_check = [elt in heroesbase[0:5] for elt in equipe2_heroes]
            if((len(np.unique(second_side_equipe2_heroes_check)) == 1) & (np.unique(second_side_equipe2_heroes_check)[0])):
                second_side_equipe2_heroes_check = True
            else:
                second_side_equipe2_heroes_check = False
            if((second_side_equipe2_heroes_check) & (second_side_equipe1_heroes_check)):
                second_side_check = True
            else:
                second_side_check = False
            # Un des deux check est t'il ok ?
            if((second_side_check) or (first_side_check)):
                check = True
                matchs_id_check_heroes.append(elt_match_base[0])
        # Pour chacun des matchs en base on applique la fonction précédente
        checkingforeachmatchinbase = [check_heroes_presences(heroes_in_match, elt_match_base, matchs_id_check_heroes) for elt_match_base in matches_base]
        # Finallement on retourne la liste des match_id des matchs qui vérifient la présence des héros spécifiés
        return matchs_id_check_heroes
