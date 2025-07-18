#!/usr/bin/env python3
"""
Script de Sauvegarde Automatique - Groupe 3
Auteurs: Mohamed Bechir Diarra, Cecile Penda, Ousmane Camara, Aboubacar S Magasouba
Version: 1.0
"""

import os
import shutil
import datetime

def backup_folder(source_dir, backup_dir):
    # Vérifier si le dossier source existe
    if not os.path.isdir(source_dir):
        print("Le dossier source n'existe pas")
        return

    # Créer automatiquement le dossier de destination s'il n'existe pas
    if not os.path.exists(backup_dir):
        os.makedirs(backup_dir)

    # Créer un nom unique pour la sauvegarde avec horodatage
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    backup_name = f"sauvegarde_{timestamp}"
    destination_path = os.path.join(backup_dir, backup_name)

    # Copier le dossier source vers la destination
    try:
        shutil.copytree(source_dir, destination_path)
        print(f"Sauvegarde réussie dans : {destination_path}")
    except Exception as e:
        print(f"Erreur pendant la sauvegarde : {e}")

 # pour tester decommentez cette partie en remplaçant les chemins (remplacer\ par / dans le chemin)

# if __name__ == "__main__":
#     backup_folder("chemin/vers/source", "chemin/vers/destination")