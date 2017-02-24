# -*- coding: utf-8 -*-
"""
Created on Wed Sep  7 11:17:07 2016

@author: apgentsmith
"""

import pickle


def serialization(obj, path_to_serialize, file_name, dump):
    """
        Cette fonction à pour but de sérializer un objet pour une futur utilisation
        Le nom du fichier d'output doit se terminer par ".p"
        args : "obj" l'objet à sérializer
               "path_to_serialize" path ou l'on va enregistrer l'objet sérializé
               " file_name" : nom du fichier contenant l'objet sérializé
               "dump" : True si on dump l'objet ou False si on load l'objet
    """

    if dump:
        # Dump de l'objet (serialization)
        pickle.dump(obj, open(path_to_serialize + file_name + ".p", "wb"))
        return None
    else:
        # Load de l'objet (Deserialization)
        return pickle.load(open(path_to_serialize + file_name + ".p", "rb"))
