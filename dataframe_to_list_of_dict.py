# -*- coding: utf-8 -*-
"""
Created on Wed Sep  7 11:17:07 2016

@author: agentsmith
"""

import json


def dataframe_to_list_of_dict(df, file_nametowrite):
    """
        Cette fonction à pour but de transformer un Pandas DataFrame contenant les informations de plusieurs matchs en une
        liste de dictionnaire dont chaque dictionnaire représente un match et ses détails.
        Cette liste de dictionnaire est ensuite écrite dans un fichier afin d'être exploitée plus tard.
    """

    list_of_dict = []
    df.apply(lambda elt: list_of_dict.append(elt.to_dict()), axis=1)
    list_of_dict = list_of_dict[0:2]
    with open(file_nametowrite, 'w') as fp:
        json.dump(list_of_dict, fp)
