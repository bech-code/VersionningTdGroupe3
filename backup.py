import os
import zipfile
import datetime

def backup_and_compress(source_dir, backup_dir):
    # Vérifier si le dossier source existe
    if not os.path.isdir(source_dir):
        print("Le dossier source n'existe pas")
        return

    # Créer automatiquement le dossier de destination s'il n'existe pas
    if not os.path.exists(backup_dir):
        os.makedirs(backup_dir)

    # Créer un nom de fichier ZIP avec horodatage
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    zip_name = f"sauvegarde_{timestamp}.zip"
    zip_path = os.path.join(backup_dir, zip_name)

    try:
        # Créer l'archive ZIP
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(source_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    # On garde la structure relative du fichier pour la restauration
                    arcname = os.path.relpath(file_path, start=source_dir)
                    zipf.write(file_path, arcname)
        print(f"Sauvegarde compressée créée : {zip_path}")
    except Exception as e:
        print(f"Erreur pendant la compression : {e}")

# Exemple d'exécution manuelle
if __name__ == "__main__":
    import sys

    if len(sys.argv) != 3:
        print("Utilisation : python backup.py dossier_source dossier_destination")
    else:
        source = sys.argv[1]
        destination = sys.argv[2]

#        print(f"DEBUG - source : {source}")
#        print(f"DEBUG - os.path.isdir(source) : {os.path.isdir(source)}")
#        print(f"DEBUG - destination : {destination}")
#        print(f"DEBUG - os.path.exists(destination) : {os.path.exists(destination)}")

        backup_and_compress(source, destination)
