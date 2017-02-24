# -*- coding: utf-8 -*-
"""
Created on Wed Sep  7 11:17:07 2016

@author: agentsmith
"""

import jsonlines
from mongodb_collection_connect import mongodb_collection_connect


def var_init(mongodb_database, matchs_collection, heroes_collection, items_collection, request_match_heroes_list=False):
    """
        Cette fonction initialise les variables dont on va se servir tout au long
        de l'étude.
        args : "mongodb_database" base de données MongoDB dans laquelle on va aller reqûeter les collections contenant les matchs, héros et items
               "matchs_collection" collection MongoDB contenant les matchs que l'on veut analyser
               "heroes_collection" collection MongoDB contenant les héros
               "items_collection" collection MongoDB contenant les items
        return : "var_init" dictionnaire qui contient les observations requêtées sur MongoDB, la liste des héros et la liste des items
    """

    def read_my_json(json_path):
        """
            Cette fonction lit un fichier jsonlines et stocke le contenu dans un dictionnaire.
            arg : "json_path" path du fichier jsonlines à lire
            return : "my_dict" dictionnaire contenant le contenu du fichier jsonlines lu
        """
        my_dict = dict()

        with jsonlines.open(json_path) as reader:
            for obj in reader:
                my_dict[obj["id"]] = obj["localized_name"]

        if json_path == "Items":
            my_dict[0] = "None"

        return my_dict

    # Initialisation du dictionnaire qui va être ret
    var_init = dict()

    # Récupération des données depuis MongoDB
    var_init["Items"] = mongodb_collection_connect(mongodb_database, items_collection, False)
    var_init["HeroesList"] = mongodb_collection_connect(mongodb_database, heroes_collection, False)
    var_init["DataList"] = mongodb_collection_connect(mongodb_database, matchs_collection, False)

    if request_match_heroes_list:
        var_init["MatchsHeroesList"] = [{"match_id": elt["match_id"], "heroes_list": [eltheroid["hero_id"] for eltheroid in elt["players"]]} for elt in var_init["Data"].find()]

    return var_init
