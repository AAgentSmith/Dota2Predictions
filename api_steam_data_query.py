# -*- coding: utf-8 -*-
"""
Created on Fri Jul 01 15:36:44 2016

@author: agentsmith
"""

import time
import os.path
import requests


def api_steam_data_query():
    """
        Cette fonction à pour objectif de récupérer des parties de Dota 2 ainsi que leurs détails via l'API Steam.
        args : "mongodb_collection_to_use" la collection MongoDB dans la base de données MongoDB à utiliser pour stocker les résultats des requêtes "matchsdetails"
        return : None
    """

    from mongodb_collection_connect import coll_matchdetails as mongodb_collection_to_use

    def get_matchs_id(mongodb_collection_to_use=mongodb_collection_to_use):
        """
            Cette fonction à pour but de récupèrer les match_id des parties de Dota 2 dont ne dispose pas.dispose pas.
            args :  "mongodb_collection_to_use" la collection située dans la base de données MongoDB "mongodb_database_to_use" à utiliser
            return : "list_match_id" la liste des match_id dont ne dispose pas déja dans la collection "mongodb_collection_to_use" spécifiée
        """

        # dev key steam : B084B54CF119658F7433604730BCF540
        # Récupération des 'match_id'
        print("#### Recuperation de l'historique 'matchs_id' #####")
        get_match_history_url_very_high_skill = 'http://api.steampowered.com/IDOTA2Match_570/GetMatchHistory/v1/?key=B084B54CF119658F7433604730BCF540&skill=3&min_players=10'

        # Récupération de l'id des matchs
        data_matches_id = [{"match_id": elt["match_id"], "lobby_type": elt["lobby_type"]} for elt in requests.get(get_match_history_url_very_high_skill).json()["result"]["matches"]]
        # Liste des 'match_id' dont on dispose déja dans la base de données
        list_existing_match_id = [elt["match_id"] for elt in mongodb_collection_to_use.find({}, {"match_id": 1})]
        # Liste des 'match_id' dont on ne dispose pas déja
        list_match_id = [elt["match_id"] for elt in data_matches_id if ((elt["match_id"] not in list_existing_match_id) & (elt["lobby_type"] in (7, 0)))]

        # On retourne la liste des match_id dont ne dispose pas
        return list_match_id

    # Récupération du détails des matchs pour chacun des 'matchs_id' récupérés précédement
    def get_match_details(match_id):
        """
            Cette fonction récupère le détail d'un match identifié par son match_id
            args : "match_id" l'identifiant du match
            return : "dict_match_details" le dictionnaire contenant le détail du match
        """

        temp_url_match_details = 'http://api.steampowered.com/IDOTA2Match_570/GetMatchDetails/v1/?key=B084B54CF119658F7433604730BCF540&match_id={}'.format(match_id)
        dict_match_details = requests.get(temp_url_match_details).json()["result"]

        return dict_match_details

    def insert_match_details_in_mongodb_collection(collection, list_match_id):
        """
            Cette fonction récupère le détail des matchs dont on à garder le match_id grâce à la fonction "get_match_details" et les insère
            dans la collection MongoDB une fois que tous les détails des matchs ont été récupérés.
            args : "collection" la collection MongoDB dans laquelle on va insèrer les résultats
                   "list_match_id" la liste des match_id dont on veut récupèrer le détail
            return : "None
        """

        # Récupération des détails des matchs
        request_executed = False
        while(not request_executed):
            try:
                list_matchs_details = [get_match_details(elt) for elt in list_match_id]
                # On ne garde que les matchs d'un certain 'game_mode' parmis (1,2,3,16,22) = ('Public matchmaking','Captain's mode','Random Draft','Captains Draft','Ranked Matchmaking')
                list_matchs_details2 = [elt for elt in list_matchs_details if elt['game_mode'] in (1, 2, 3, 16, 22)]
                request_executed = True
            except:
                request_executed = False

        # Insertion des résultats dans la base de données MongoDB
        collection.insert_many(list_matchs_details2)

        # On va enregistrer un message dans le fichier historique

        # Le fichier d'historique exsite t'il ?
        historic_exists = os.path.exists("/home/agentsmith/Travaux/CentralSupelec/ProjetDota2/logs/historique.txt")

        # On écrit dans le fichier 'historique.txt' une information sur le nombre d'observations ajoutées et le nombre total d'observations la collection MongoDB 'matchsdetails'
        if not historic_exists:
            os.system('touch /home/agentsmith/Travaux/CentralSupelec/ProjetDota2/logs/historique.txt')
            f = open("/home/agentsmith/Travaux/CentralSupelec/ProjetDota2/logs/historique.txt", "r+")
            f.write("\n" + time.strftime("%d/%m/%Y") + " - " + time.strftime("%H:%M:%S") + " ---> " + str(len(list_matchs_details2)) + " observations ajoutées dans la base données MongoDB 'list_matchs_details' ** " + str(collection.count()) + " observations dans la base de données")
            f.close()
        else:
            f = open("/home/agentsmith/Travaux/CentralSupelec/ProjetDota2/logs/historique.txt", "a")
            f.write("\n" + time.strftime("%d/%m/%Y") + " - " + time.strftime("%H:%M:%S") + " ---> " + str(len(list_matchs_details2)) + " observations ajoutées dans la base données MongoDB 'list_matchs_details' ** " + str(collection.count()) + " observations dans la base de données")
            f.close()

        # Affichage informations sur la base de données après ajout des observations
        print("#### INFORMATIONS BASE DE DONNEES ####\n * Collection 'matchdetailsdb' ---> " + str(collection.count()) + " observations au total\n                                    " + str(len(list_matchs_details2)) + " observations ajoutées")

        return None

    # Creation de la liste de match_id dont on veut récupérer le détail
    list_match_id = get_matchs_id()
    # Récupération du détail des match_id et insertion dans MongoDB
    insert_match_details_in_mongodb_collection(mongodb_collection_to_use, list_match_id)

    return None


# Récupération des matchs
# api_steam_data_query()
