import os
import zipfile
from datetime import datetime

# Fonction de log
def log(message):
    print(message)
    # Créer le dossier logs si nécessaire
    os.makedirs("logs", exist_ok=True)
    with open("logs/backup.log", "a") as f:
        f.write(f"[{datetime.now()}] {message}\n")

def backup_and_compress(source_dir, backup_dir):
    if not os.path.isdir(source_dir):
        log("Le dossier source n'existe pas")
        return

    if not os.path.exists(backup_dir):
        os.makedirs(backup_dir)

    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    zip_name = f"sauvegarde_{timestamp}.zip"
    zip_path = os.path.join(backup_dir, zip_name)

    try:
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(source_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, start=source_dir)
                    zipf.write(file_path, arcname)
        log(f"Sauvegarde compressée créée : {zip_path}")
    except Exception as e:
        log(f"Erreur pendant la compression : {e}")

def test_log_file_contains_backup_message(self):
    log_path = "logs/backup.log"
    # Supprimer le log existant pour un test propre
    if os.path.exists(log_path):
        os.remove(log_path)

    # Exécuter une sauvegarde
    with io.StringIO() as buf, contextlib.redirect_stdout(buf):
        backup_and_compress(self.source, self.dest)

    self.assertTrue(os.path.exists(log_path))

    with open(log_path, "r") as f:
        content = f.read()

    self.assertIn("Sauvegarde compressée créée", content)
