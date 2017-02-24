# -*- coding: utf-8 -*-
"""
Created on Wed Sep  7 11:17:07 2016

@author: agentsmith
"""

from pymongo import MongoClient


def mongodb_collection_connect(database, collection, only_connect=True):
    """
        Cette fonction à pour but de requêter une collection dans une base de données
        MongoDB.
        args : "database" la database dans laquelle est située la collection
                "collection" la collection qu'on souhaite récupérer
                "only_connect" True ou False selon que l'on veuille seulement se connecter ou renvoyer le contenu de la collection
        return : "my_collection_to_list" une liste contenant les éléments de la collection si on veut le contenue de la collection
                 "my_collection" si on se connecte seulement à la collection
    """

    # Connection à MongoDB et récupération de la collection spécifiée dans la base de données spécifiée
    client = MongoClient()
    db = getattr(client, database)
    my_collection = getattr(db, collection)
    if only_connect:
        return my_collection
    else:
        my_collection_to_list = [elt for elt in my_collection.find()]
        return my_collection_to_list


# On initialise la connection à la collection de MongoDB
coll_matchdetails = mongodb_collection_connect("Dota2DataBase", "matchdetails")
