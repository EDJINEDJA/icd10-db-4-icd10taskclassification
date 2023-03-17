#!/bin/bash

@echo "Bienvenue .."

# Chemin vers le dossier contenant le script Python et le fichier Pipfile.lock
SCRIPT_PATH = /home/lnit/icd10-db-4-icd10taskclassification/


@echo "Enable environnement .."
# Activer l'environnement virtuel Pipenv
cd $SCRIPT_PATH && pipenv shell

# Exécuter le script Python à l'aide de pipenv run
pipenv run python nom_du_script.py > $SCRIPT_PATH/log.txt

# Désactiver l'environnement virtuel Pipenv
exit