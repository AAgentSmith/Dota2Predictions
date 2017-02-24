#!/bin/bash

# Lancement de MongoDB
sudo service mongod start

# On lance une première fois la récupération des matchs pour en avoir le plus possible (100)
python ~/media/agentsmith/D64C25154C24F1C32/Work/Travaux/CentralSupelec/prgClean2/python/api_steam_data_query.py 2>&1 ~/loghistory

# On relance toutes les 45 secondes le script pour obtenir les nouveaux matchs
watch -n 45 python ~/media/agentsmith/D64C25154C24F1C32/Work/Travaux/CentralSupelec/prgClean2/python/api_steam_data_query.py 2>&1 ~/loghistory