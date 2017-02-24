# -*- coding: utf-8 -*-
"""
Created on Wed Sep  7 11:17:07 2016

@author: agentsmith
"""

from __future__ import print_function
import numpy as np
import pandas as pd
from copy import deepcopy
from bokeh.plotting import figure
from bokeh.io import curdoc
from bokeh.layouts import widgetbox, column
from bokeh.models.widgets import Select
from bokeh.models import LabelSet, ColumnDataSource, FixedTicker
from serialization import serialization
from mongodb_collection_connect import mongodb_collection_connect

heroes = mongodb_collection_connect("Dota2DataBase", "heroeslistdb", False)
heroes = {elt["id"]: elt["localized_name"] for elt in heroes}


def pick_coaching(logisticmodel, heroesdict, listofheroes=[]):
    """
        Cette fonction à pour but de recommander les picks de héros lors de la phase de pick des héros.
        Cette recommandation sera basée sur la variation de la probabilité de gagner des deux équipes selon la modification de la présence des héros dans les
        deux équipes. Le modèle sur lequel s'appuiera cette recommandation sera un modèle de type logit.
        #
        Paramètres :
        - logisticmodel : le modèle qui a été crée
        - listofheroes : la liste des héros présents dans la partie, si vide alors aucun héros n'a été selectionné
        - heroesdict : le dictionnaire des héros qui sont pris en compte dans la phase de pick
    """

    global win_proba_data_source
    global delta_win_proba_data_source
    global ennemy_delta_win_proba_data_source
    global labels_data_source
    global other_parameters

    # Fonction qui calcule les probabilités de gagner de chacune des deux équipes
    def predict_with_swap_team(series):
        """
            Cette fonction calcule la probabilité d'une équipe en tant que Radiant et Dire en faisant
            la moyenne des probabilité de gagner de l'équipe Radiant avant et après swap des équipes.
            args : "series" une pandas.Series qui contient les héros des deux équipes
            return : Un dictionnaire contenant les probabilités de gagner des deux équipes
        """

        # Première prédiction
        FirstPredictProba = logisticmodel.predict_proba(series.reshape(1, -1))
        FirstPredictProbaRadiantWin = FirstPredictProba[0][1]
        FirstPredictProbaDireWin = FirstPredictProba[0][0]
        # On swap les équipes & on calcule la proba
        FirstPart = list(series[0:len(heroesdict)])
        SecondPart = list(series[len(heroesdict):])
        SecondPredictProba = logisticmodel.predict_proba(pd.Series(SecondPart + FirstPart).reshape(1, -1))
        SecondPredictProbaRadiantWin = SecondPredictProba[0][1]
        SecondPredictProbaDireWin = SecondPredictProba[0][0]
        # Calcul des proba moyennes
        AvgRadiant = np.mean((FirstPredictProbaRadiantWin, SecondPredictProbaDireWin))
        AvgDire = np.mean((FirstPredictProbaDireWin, SecondPredictProbaRadiantWin))
        # On renvoit les probabilité de gagner des deux équipes de la configuration de la série passée en argument

        return {"Radiant_Hero_": round(AvgRadiant, 2), "Dire_Hero_": round(AvgDire, 2)}

    # Data Source initialles
    def win_proba_data_source_update(ProbaWinChanges):
        """
            Cette fonction à pour but d'initialiser les probabilités de gagner des deux équipes.
            args : "ProbaWinChanges"
            return : "win_proba_data_source" un objet de type ColumnDataSource contenant les probabilités de gagner des équipes
        """

        win_proba_data_source = ColumnDataSource(data=dict(NbPick=range(0, len(ProbaWinChanges["Radiant"])), Radiant=ProbaWinChanges["Radiant"], Dire=ProbaWinChanges["Dire"]))

        return win_proba_data_source

    def ennemy_delta_win_proba_data_source_update(EnnemyPredictProbaList):
        """
            Cette fonction à pour but d'initialiser les probabilités de gagner des deux équipes.
            args : "EnnemyPredictProbaList"
            return : "ennemy_delta_win_proba_data_source" un objet de type ColumnDataSource contenant les probabilités de gagner des équipes
        """

        ennemy_delta_win_proba_data_source = ColumnDataSource(data=dict(Xaxisindex=range(0, len(EnnemyPredictProbaList)), Heros=[str(elt[0]) for elt in EnnemyPredictProbaList], Delta=[elt[1] for elt in EnnemyPredictProbaList]))

        return ennemy_delta_win_proba_data_source

    def delta_win_proba_data_source_update(PredictProbaList):
        """
            Cette fonction à pour but d'initialiser les probabilités de gagner des deux équipes.
            args : "PredictProbaList"
            return : "delta_win_proba_data_source" un objet de type ColumnDataSource contenant les probabilités de gagner des équipes
        """

        delta_win_proba_data_source = ColumnDataSource(data=dict(Xaxisindex=range(0, len(PredictProbaList)), Heros=[str(elt[0]) for elt in PredictProbaList], Delta=[elt[1] for elt in PredictProbaList]))

        return delta_win_proba_data_source

    # Radiant + Dire proba labelling
    def update_proba_change_labels(win_proba_data_source, other_parameters):
        """
            Cette fonction à pour but de changer les labels des différents points du graphique d'évolution des probabilités
            args : "win_proba_data_source" qui contient l'évolution des probabilités de gagner des deux équipes
                   "other_parameters" contient d'autres paramètres comme les noms des héros choisis successivement
            return : "labels_data_source" un objet de type ColumnDataSource contenant les labels des héros choisis et les probabilités associées à chaque pick
        """

        labels_data_source.data["Proba"] = win_proba_data_source.data["Radiant"] + win_proba_data_source.data["Dire"]
        labels_data_source.data["NbPick"] = win_proba_data_source.data["NbPick"] * 2
        RadiantLabels = []
        for i in range(0, len(win_proba_data_source.data["Radiant"])):
            RadiantLabels.append(str(win_proba_data_source.data["Radiant"][i]) + "% " + other_parameters.data["Radiant_Hero_"][i])
        DireLabels = []
        for i in range(0, len(win_proba_data_source.data["Dire"])):
            DireLabels.append(str(win_proba_data_source.data["Dire"][i]) + "% " + other_parameters.data["Dire_Hero_"][i])
        labels_data_source.data["Text"] = RadiantLabels + DireLabels

        return labels_data_source

    # Initialisation à vide
    win_proba_data_source = ColumnDataSource()
    delta_win_proba_data_source = ColumnDataSource()
    ennemy_delta_win_proba_data_source = ColumnDataSource()
    labels_data_source = ColumnDataSource(data=dict(NbPick=[], Proba=[], Text=[]))
    # Variables et paramètres généraux dont on a besoin de modifier tout au long du processus
    other_parameters = ColumnDataSource(dict(compt=[], vectheroes=[pd.Series()], currentHeroChoice=[], theoricvectheroes=[pd.Series()], theoriccurrentHeroChoice=[], Radiant_Hero_=[], Dire_Hero_=[]))

    if(len(listofheroes) == 0):

        # Liste représentant les héros actuels dans la partie / Indice du milieu de list
        DictOfPicks = {"Radiant_Hero_": [], "Dire_Hero_": []}
        # On crée un nouveau dictionnaire contenant les héros avec le statut "Pick" "NotPick"
        heroestemp = {elt[0]: {"HeroName": elt[1], "StatusPick": False} for elt in heroesdict.items()}
        heroestempreverse = {elt[1]: elt[0] for elt in heroes.items()}
        # Creation des colonnes du vecteur de présence de héros à partir des noms de héros contenus dans le dictionnaire de héros crée précédement
        Radiantcolheroes = ["Radiant_Hero_" + heroestemp[eltkey]["HeroName"] for eltkey in heroestemp.keys()]
        Direcolheroes = ["Dire_Hero_" + heroestemp[eltkey]["HeroName"] for eltkey in heroestemp.keys()]
        colheroes = Radiantcolheroes + Direcolheroes
        # Creation du vecteur de présence de héro initialisé à 0 partout
        vectheroes = pd.Series([False] * (len(heroesdict) * 2), index=colheroes)
        # Compteurs de héros selectionnés
        compt = 0
        # Initialisation de certains paramètre généraux dans la source de données "other_parameters"
        other_parameters.data["compt"] = [compt]
        other_parameters.data["vectheroes"] = [vectheroes]
        other_parameters.data["theoricvectheroes"] = [vectheroes]
        other_parameters.data["currentHeroChoice"] = [-1]
        other_parameters.data["theoriccurrentHeroChoice"] = [-1]
        other_parameters.data["Radiant_Hero_"] = [" "]
        other_parameters.data["Dire_Hero_"] = [" "]
        Team = ["Radiant_Hero_", "Dire_Hero_"] * 7
        # Dictionnaire contenant l'évolution des proba de win pour les deux équipes
        ProbaWinChanges = {"Radiant": [50.0], "Dire": [50.0]}
        # Initialisation des sources de données
        win_proba_data_source = win_proba_data_source_update(ProbaWinChanges)
        labels_data_source = update_proba_change_labels(win_proba_data_source, other_parameters)
        delta_win_proba_data_source = delta_win_proba_data_source_update([(str(elt[1]), 0) for elt in heroes.items()])
        ennemy_delta_win_proba_data_source = ennemy_delta_win_proba_data_source_update([(str(elt[1]), 0) for elt in heroes.items()])
        # On extraie les héros qui sont encore selectionnables
        PossibleHeroesPick = [elt for elt in heroestemp.keys() if (elt not in DictOfPicks["Radiant_Hero_"] + DictOfPicks["Dire_Hero_"])]

        # Initialisation des graphiques
        WinProbaChanges = figure(
            y_range=[0, 100], title="Win probability for each Team at this stage of pick",
            x_axis_label='Number of Picks', y_axis_label='Win %', plot_width=1500, plot_height=400
        )

        # Evolution des probabilité de gagner des deux équipes
        WinProbaChanges.line(source=win_proba_data_source, x="NbPick", y="Dire", line_color="red")
        WinProbaChanges.triangle(source=win_proba_data_source, x="NbPick", y="Dire", legend="Dire win %", fill_color="red", size=15)
        WinProbaChanges.line(source=win_proba_data_source, x="NbPick", y="Radiant", line_color="green")
        WinProbaChanges.circle(source=win_proba_data_source, x="NbPick", y="Radiant", legend="Radiant win %", fill_color="green", size=15)
        Probalabels = LabelSet(source=labels_data_source, x='NbPick', y='Proba', text='Text', level='glyph', x_offset=5, y_offset=5, angle=0)
        WinProbaChanges.add_layout(Probalabels)
        WinProbaChanges.circle(source=win_proba_data_source, x="NbPick", y="Radiant", legend="Radiant win %", fill_color="green", size=15)
        Probalabels = LabelSet(source=labels_data_source, x='NbPick', y='Proba', text='Text', level='glyph', x_offset=5, y_offset=5, angle=0)
        WinProbaChanges.add_layout(Probalabels)
        WinProbaChanges.xaxis[0].ticker = FixedTicker(ticks=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11])

        # Barplot des delta de Win proba pour chaque héro
        DeltaWinProbaByHero = figure(plot_height=600, plot_width=1500, title=" Delta Win Proba par hero", tools="crosshair,pan,reset,save,wheel_zoom")
        labels = LabelSet(source=delta_win_proba_data_source, x='Xaxisindex', y='Delta', text='Heros', level='glyph',
                          x_offset=5, y_offset=5, angle=1.45)
        DeltaWinProbaByHero.add_layout(labels)
        DeltaWinProbaByHero.vbar(source=delta_win_proba_data_source, x='Xaxisindex', top='Delta', width=0.3, bottom=0, color="blue")

        # Equipe ennemie
        EnnemyDeltaWinProbaByHero = figure(plot_height=600, plot_width=1500, title=unicode("NEXT PICK ------ Delta Win Proba par hero"), tools="crosshair,pan,reset,save,wheel_zoom")
        labels = LabelSet(source=ennemy_delta_win_proba_data_source, x='Xaxisindex', y='Delta', text='Heros', level='glyph',
                          x_offset=5, y_offset=5, angle=1.45)
        EnnemyDeltaWinProbaByHero.add_layout(labels)
        EnnemyDeltaWinProbaByHero.vbar(source=ennemy_delta_win_proba_data_source, x='Xaxisindex', top='Delta', width=0.3, bottom=0, color="orange")

        # Widget de selection
        herosoptions = [''] + [str(heroestemp[elt]["HeroName"]) for elt in PossibleHeroesPick]
        herosoptions.sort()
        SelectHero = Select(title="Hero selection", options=herosoptions)

        print("###### HERO PICK POUR LE MOMENT #######")
        print(DictOfPicks)
        print(len([elt for elt in heroestemp.keys() if(elt not in DictOfPicks["Radiant_Hero_"] + DictOfPicks["Dire_Hero_"])]))

        # Update Functions
        def update(attrname, old, new):
            """
                Cette fonction permet a l'utilisateur de choisir un héros parmis une selection de héros,
                selon le choix du héro les graphiques doivent se mettre à jour en simulant une phase de pick de dota2.
            """

            global win_proba_data_source
            global delta_win_proba_data_source
            global ennemy_delta_win_proba_data_source
            global labels_data_source
            global other_parameters

            # Boucle de selection des personnages
            if(new != ""):

                print("##################### ITERATION " + str(other_parameters.data["compt"][0] + 1) + " #####################")
                if((10 > other_parameters.data["compt"][0]) & (other_parameters.data["compt"][0] >= 1)):

                    currentHeroChoice = heroestempreverse[new]
                    print(" Hero choisit : " + new)
                    # On met à jour le vecteur de héro & on met à jour le statut du héros dans le dictionnaire des héros
                    vectheroes = deepcopy(other_parameters.data["vectheroes"][0])
                    vectheroes[Team[other_parameters.data["compt"][0]] + heroestemp[currentHeroChoice]["HeroName"]] = True
                    heroestemp[currentHeroChoice]["StatusPick"] = True
                    # Probabilité de gagner dans la configuration suivante & on l'ajoute aux liste d'évolution des proba des deux équipes
                    CurrentConfProbWin = predict_with_swap_team(vectheroes)[Team[other_parameters.data["compt"][0]]]
                    print(Team[1 + other_parameters.data["compt"][0]])
                    print(1 - CurrentConfProbWin)
                    ProbaWinChanges[Team[other_parameters.data["compt"][0]].replace("_Hero_", "")].append(CurrentConfProbWin * 100)
                    ProbaWinChanges[Team[other_parameters.data["compt"][0] + 1].replace("_Hero_", "")].append(100 - (CurrentConfProbWin * 100))
                    # On ajoute au dictionnaire contenant les listes de héros le héro choisit
                    DictOfPicks[Team[other_parameters.data["compt"][0]]].append(currentHeroChoice)
                    other_parameters.data["vectheroes"] = [vectheroes]
                    other_parameters.data["currentHeroChoice"] = [currentHeroChoice]
                    other_parameters.data["theoricvectheroes"] = [pd.Series()]
                    other_parameters.data["theoriccurrentHeroChoice"] = [-1]
                    other_parameters.data[Team[other_parameters.data["compt"][0]]].append(" " + new)
                    other_parameters.data[Team[other_parameters.data["compt"][0] + 1]].append(" ")
                    other_parameters.data["compt"] = [other_parameters.data["compt"][0] + 1]
                    # On extraie les héros qui sont encore selectionnables
                    ChoosenHeroes = DictOfPicks["Radiant_Hero_"] + DictOfPicks["Dire_Hero_"]
                    PossibleHeroesPick = [elt for elt in heroestemp.keys() if(elt not in ChoosenHeroes)]
                    PredictProbaList = []

                    # On va calculer la variation de probabilité de gagné avec chaque personnage ajouté pour l'équipe dans la configuration suivante
                    for eltpossibleheroespick in PossibleHeroesPick:

                        TheoricVectHeroes = deepcopy(other_parameters.data["vectheroes"][0])
                        TheoricVectHeroes[Team[other_parameters.data["compt"][0]] + heroestemp[eltpossibleheroespick]["HeroName"]] = True
                        # Calcul de la probabilité de gagner & ajout au dictionnaire des proba
                        print(heroestemp[eltpossibleheroespick]["HeroName"], predict_with_swap_team(TheoricVectHeroes)[Team[other_parameters.data["compt"][0]]] - (1 - CurrentConfProbWin), Team[other_parameters.data["compt"][0]])
                        PredictProbaList.append((heroestemp[eltpossibleheroespick]["HeroName"], round((predict_with_swap_team(TheoricVectHeroes)[Team[other_parameters.data["compt"][0]]] - (1 - CurrentConfProbWin)) * 100, 6), eltpossibleheroespick))

                    # Tri de la liste des proba pour l'équipe actuelle
                    PredictProbaList.sort(reverse=True, key=lambda x: x[1])
                    PredictProbaList = [elt for elt in PredictProbaList]
                    # other_parameters.data["compt"] = [other_parameters.data["compt"][0] + 1]
                    # On va calculer la moyenne du delta de win proba pour l'équipe adverse pour chacun des héros qui pouront être pick selon les pick de l'equipe actuelle
                    MeanPredictProbaDict = {}

                    for eltprobachange in PredictProbaList:

                        # On simule le pick de ce héro et on calcule les delta de proba win pour chaque héro de l'équipe adverse
                        TheoricCurrentHeroChoice = eltprobachange[2]
                        # On fait une copie des variables nécessaires aux prédictions & on ajoute au dictionnaire contenant les listes de héros le héro choisit
                        TheoricDictOfPicks = deepcopy(DictOfPicks)
                        # On met à jour le vecteur de héro & on met à jour le statut du héros dans le dictionnaire des héros
                        Theoricheroestemp = deepcopy(heroestemp)
                        Theoricheroestemp[TheoricCurrentHeroChoice]["StatusPick"] = True
                        TheoricVectHeroes = deepcopy(other_parameters.data["vectheroes"][0])
                        # On simule le pick du héro pour cette équipe
                        TheoricVectHeroes[Team[other_parameters.data["compt"][0]] + Theoricheroestemp[eltprobachange[2]]["HeroName"]] = True
                        # On ajoute au dictionnaire contenant les listes de héros le héro choisit
                        TheoricDictOfPicks[Team[other_parameters.data["compt"][0]]].append(TheoricCurrentHeroChoice)
                        # On extraie les héros qui sont encore selectionnables
                        TheoricPossibleHeroesPick = [elt for elt in Theoricheroestemp.keys() if(elt not in TheoricDictOfPicks["Radiant_Hero_"] + TheoricDictOfPicks["Dire_Hero_"])]
                        TheoricPredictProbaList = []
                        # Probabilité de gagner dans la configuration suivante
                        TheoricCurrentConfProbWin = predict_with_swap_team(TheoricVectHeroes)[Team[deepcopy(other_parameters.data["compt"][0]) + 1]]

                        # On va calculer la variation de probabilité de gagné avec chaque personnage ajouté pour l'équipe dans la configuration suivante
                        for eltpossibleheroespick in TheoricPossibleHeroesPick:

                            TheoricVectHeroes2 = deepcopy(TheoricVectHeroes)
                            TheoricVectHeroes2[Team[deepcopy(other_parameters.data["compt"][0]) + 1] + Theoricheroestemp[eltpossibleheroespick]["HeroName"]] = True
                            # Calcul de la probabilité de gagner & ajout au dictionnaire des proba
                            TheoricPredictProbaList.append((Theoricheroestemp[eltpossibleheroespick]["HeroName"], predict_with_swap_team(TheoricVectHeroes2)[Team[deepcopy(other_parameters.data["compt"][0]) + 1]], eltpossibleheroespick))

                        # Tri de la liste des proba
                        TheoricPredictProbaList.sort(reverse=True, key=lambda x: x[1])
                        # On selectionne seulement les 5 premiers items
                        TheoricPredictProbaDict = {theoricelt[0]: round((theoricelt[1] - TheoricCurrentConfProbWin) * 100, 6) for theoricelt in TheoricPredictProbaList}
                        for key in TheoricPredictProbaDict.keys():

                            if key in MeanPredictProbaDict.keys():
                                MeanPredictProbaDict[key].append(TheoricPredictProbaDict[key])
                            else:
                                MeanPredictProbaDict[key] = [TheoricPredictProbaDict[key]]

                    # Calcul de la moyenne du delta pour chacun des héro possiblement pickable par l'équipe adverse basé sur les calculs dans la boucle
                    MeanPredictProbaList = [(elt[0], np.mean(elt[1])) for elt in MeanPredictProbaDict.items()]
                    MeanPredictProbaList = [elt for elt in MeanPredictProbaList]
                    print("\n")
                    print("############ PICKING TEAM ---> " + Team[compt].replace("_Hero_", "").upper() + " / Actual proba win :" + str(100 - (CurrentConfProbWin * 100)) + " % " + " ############")
                    print("############ EQUIPES ACTUELLES ############")
                    print(" Radiant --> " + str([heroestemp[eltheroesradiant]["HeroName"] for eltheroesradiant in DictOfPicks["Radiant_Hero_"]]))
                    print(" Dire --> " + str([heroestemp[eltheroesradiant]["HeroName"] for eltheroesradiant in DictOfPicks["Dire_Hero_"]]))
                    delta_win_proba_data_source.data = dict(Xaxisindex=range(0, len(PredictProbaList)), Heros=[str(elt[0]) for elt in PredictProbaList], Delta=[elt[1] for elt in PredictProbaList])
                    ennemy_delta_win_proba_data_source.data = dict(Xaxisindex=range(0, len(MeanPredictProbaList)), Heros=[str(elt[0]) for elt in MeanPredictProbaList], Delta=[elt[1] for elt in MeanPredictProbaList])
                    win_proba_data_source.data = dict(NbPick=range(0, len(ProbaWinChanges["Radiant"])), Radiant=ProbaWinChanges["Radiant"], Dire=ProbaWinChanges["Dire"])
                    labels_data_source = update_proba_change_labels(win_proba_data_source, other_parameters)

                elif(other_parameters.data["compt"][0] == 0):

                    printlist = heroestemp.items()
                    printlist.sort(key=lambda x: x[1]["HeroName"])
                    print("############ Equipe : " + Team[other_parameters.data["compt"][0]].strip("_Hero_").upper() + " PICK FIRST HERO ############")
                    print("############ Liste des héros et leurs id ############")
                    print("\n")
                    print("############ TEAM : " + Team[other_parameters.data["compt"][0]].replace("_Hero_", "").upper() + " <----> PICK A HERO BY ID ############")
                    currentHeroChoice = heroestempreverse[new]
                    print(" Hero choisit : " + new)
                    # On met à jour le vecteur de héro & on met à jour le statut du héros dans le dictionnaire des héros
                    vectheroes = deepcopy(other_parameters.data["vectheroes"][0])
                    vectheroes[Team[other_parameters.data["compt"][0]] + heroestemp[currentHeroChoice]["HeroName"]] = True
                    heroestemp[currentHeroChoice]["StatusPick"] = True
                    # Probabilité de gagner dans la configuration suivante & on l'ajoute aux liste d'évolution des proba des deux équipes
                    CurrentConfProbWin = predict_with_swap_team(vectheroes)[Team[other_parameters.data["compt"][0]]]
                    ProbaWinChanges[Team[other_parameters.data["compt"][0]].replace("_Hero_", "")].append(CurrentConfProbWin * 100)
                    ProbaWinChanges[Team[other_parameters.data["compt"][0] + 1].replace("_Hero_", "")].append(100 - (CurrentConfProbWin * 100))
                    # On ajoute au dictionnaire contenant les listes de héros le héro choisit
                    DictOfPicks[Team[other_parameters.data["compt"][0]]].append(currentHeroChoice)
                    other_parameters.data["vectheroes"] = [vectheroes]
                    other_parameters.data["currentHeroChoice"] = [currentHeroChoice]
                    other_parameters.data["theoricvectheroes"] = [pd.Series()]
                    other_parameters.data["theoriccurrentHeroChoice"] = [-1]
                    other_parameters.data[Team[other_parameters.data["compt"][0]]].append(" " + new)
                    other_parameters.data[Team[other_parameters.data["compt"][0] + 1]].append(" ")
                    other_parameters.data["compt"] = [other_parameters.data["compt"][0] + 1]
                    win_proba_data_source.data = dict(NbPick=range(0, len(ProbaWinChanges["Radiant"])), Radiant=ProbaWinChanges["Radiant"], Dire=ProbaWinChanges["Dire"])
                    # On extraie les héros qui sont encore selectionnables
                    ChoosenHeroes = DictOfPicks["Radiant_Hero_"] + DictOfPicks["Dire_Hero_"]
                    PossibleHeroesPick = [elt for elt in heroestemp.keys() if (elt not in ChoosenHeroes)]
                    PredictProbaList = []

                    # On va calculer la variation de probabilité de gagné avec chaque personnage ajouté pour l'équipe dans la configuration suivante
                    for eltpossibleheroespick in PossibleHeroesPick:

                        TheoricVectHeroes = deepcopy(other_parameters.data["vectheroes"][0])
                        TheoricVectHeroes[Team[other_parameters.data["compt"][0]] + heroestemp[eltpossibleheroespick]["HeroName"]] = True
                        # Calcul de la probabilité de gagner & ajout au dictionnaire des proba
                        PredictProbaList.append((heroestemp[eltpossibleheroespick]["HeroName"], round((predict_with_swap_team(TheoricVectHeroes)[Team[other_parameters.data["compt"][0]]]) * 100 - (100 - (CurrentConfProbWin * 100)), 6), eltpossibleheroespick))

                    # Tri de la liste des proba pour l'équipe actuelle
                    PredictProbaList.sort(reverse=True, key=lambda x: x[1])
                    PredictProbaList = [elt for elt in PredictProbaList]
                    MeanPredictProbaDict = {}

                    # On va calculer la moyenne du delta de win proba pour l'équipe adverse pour chacun des héros qui pouront être pick selon les pick de l'equipe actuelle
                    for eltprobachange in PredictProbaList:

                        # On simule le pick de ce héro et on calcule les delta de proba win pour chaque héro de l'équipe adverse
                        TheoricCurrentHeroChoice = eltprobachange[2]
                        # On fait une copie des variables nécessaires aux prédictions & on ajoute au dictionnaire contenant les listes de héros le héro choisit
                        TheoricDictOfPicks = deepcopy(DictOfPicks)
                        # On met à jour le vecteur de héro & on met à jour le statut du héros dans le dictionnaire des héros
                        Theoricheroestemp = deepcopy(heroestemp)
                        Theoricheroestemp[TheoricCurrentHeroChoice]["StatusPick"] = True
                        TheoricVectHeroes = deepcopy(other_parameters.data["vectheroes"][0])
                        # On simule le pick du héro pour cette équipe
                        TheoricVectHeroes[Team[other_parameters.data["compt"][0]] + Theoricheroestemp[eltprobachange[2]]["HeroName"]] = True
                        # On ajoute au dictionnaire contenant les listes de héros le héro choisit
                        TheoricDictOfPicks[Team[other_parameters.data["compt"][0]]].append(TheoricCurrentHeroChoice)
                        # On extraie les héros qui sont encore selectionnables
                        TheoricPossibleHeroesPick = [elt for elt in Theoricheroestemp.keys() if(elt not in TheoricDictOfPicks["Radiant_Hero_"] + TheoricDictOfPicks["Dire_Hero_"])]
                        TheoricPredictProbaList = []
                        # Probabilité de gagner dans la configuration suivante
                        TheoricCurrentConfProbWin = predict_with_swap_team(TheoricVectHeroes)[Team[deepcopy(other_parameters.data["compt"][0]) + 1]]
                        # On va calculer la variation de probabilité de gagné avec chaque personnage ajouté pour l'équipe dans la configuration suivante
                        for eltpossibleheroespick in TheoricPossibleHeroesPick:

                            TheoricVectHeroes2 = deepcopy(TheoricVectHeroes)
                            TheoricVectHeroes2[Team[deepcopy(other_parameters.data["compt"][0]) + 1] + Theoricheroestemp[eltpossibleheroespick]["HeroName"]] = True
                            # Calcul de la probabilité de gagner & ajout au dictionnaire des proba
                            TheoricPredictProbaList.append((Theoricheroestemp[eltpossibleheroespick]["HeroName"], predict_with_swap_team(TheoricVectHeroes2)[Team[deepcopy(other_parameters.data["compt"][0]) + 1]], eltpossibleheroespick))

                        # Tri de la liste des proba
                        TheoricPredictProbaList.sort(reverse=True, key=lambda x: x[1])
                        # On selectionne seulement les 5 premiers items
                        TheoricPredictProbaDict = {theoricelt[0]: round((theoricelt[1] - TheoricCurrentConfProbWin) * 100, 6) for theoricelt in TheoricPredictProbaList}
                        for key in TheoricPredictProbaDict.keys():

                            if key in MeanPredictProbaDict.keys():
                                MeanPredictProbaDict[key].append(TheoricPredictProbaDict[key])

                            else:
                                MeanPredictProbaDict[key] = [TheoricPredictProbaDict[key]]

                    # Calcul de la moyenne du delta pour chacun des héro possiblement pickable par l'équipe adverse basé sur les calculs dans la boucle
                    MeanPredictProbaList = [(elt[0], np.mean(elt[1])) for elt in MeanPredictProbaDict.items()]
                    MeanPredictProbaList.sort(reverse=True, key=lambda x: x[1])
                    MeanPredictProbaList = [elt for elt in MeanPredictProbaList]
                    ennemy_delta_win_proba_data_source.data = dict(Xaxisindex=range(0, len(MeanPredictProbaList)), Heros=[elt[0] for elt in MeanPredictProbaList], Delta=[elt[1] for elt in MeanPredictProbaList])
                    delta_win_proba_data_source.data = dict(Xaxisindex=range(0, len(PredictProbaList)), Heros=[elt[0] for elt in PredictProbaList], Delta=[elt[1] for elt in PredictProbaList])
                    labels_data_source = update_proba_change_labels(win_proba_data_source, other_parameters)

        # On lie le module de selection et la fonction d'update
        SelectHero.on_change('value', update)
        # Set up layouts and add to document
        inputs = widgetbox(SelectHero)
        curdoc().add_root(column(WinProbaChanges, DeltaWinProbaByHero, EnnemyDeltaWinProbaByHero, inputs))
        curdoc().title = "PickCoaching"

        return None


pick_coaching(serialization(1, "/home/agentsmith/Travaux/CentralSupelec/ProjetDota2/divers/Models/", "LogisticModelFullPartial", False), heroes)
