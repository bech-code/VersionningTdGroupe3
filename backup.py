#!/usr/bin/env python3
"""
Script de Sauvegarde Automatique - Groupe 3
Auteurs: Mohamed Bechir Diarra, Cecile Penda, Ousmane Camara, Aboubacar S Magasouba
Version: 1.0
"""

import os
import zipfile
import datetime
import logging
import sys
import argparse
from pathlib import Path

class BackupManager:
    def __init__(self, log_level=logging.INFO):
        """Initialise le gestionnaire de sauvegarde avec logging"""
        self.setup_logging(log_level)
        
    def setup_logging(self, log_level):
        """Configure le système de logging"""
        # Créer le dossier logs s'il n'existe pas
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        
        # Nom du fichier de log avec timestamp
        log_filename = f"backup_{datetime.datetime.now().strftime('%Y-%m-%d')}.log"
        log_path = log_dir / log_filename
        
        # Configuration du logging
        logging.basicConfig(
            level=log_level,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_path, encoding='utf-8'),
                logging.StreamHandler(sys.stdout)
            ]
        )
        self.logger = logging.getLogger(__name__)
        
    def validate_paths(self, source_dir, backup_dir):
        """Valide les chemins source et destination"""
        if not os.path.isdir(source_dir):
            raise ValueError(f"Le dossier source '{source_dir}' n'existe pas")
        
        if not os.access(source_dir, os.R_OK):
            raise PermissionError(f"Pas de permission de lecture sur '{source_dir}'")
        
        # Créer le dossier de destination s'il n'existe pas
        try:
            os.makedirs(backup_dir, exist_ok=True)
        except OSError as e:
            raise PermissionError(f"Impossible de créer le dossier de destination '{backup_dir}': {e}")
        
        if not os.access(backup_dir, os.W_OK):
            raise PermissionError(f"Pas de permission d'écriture sur '{backup_dir}'")
    
    def get_backup_filename(self, prefix="backup"):
        """Génère un nom de fichier de sauvegarde avec horodatage"""
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        return f"{prefix}_{timestamp}.zip"
    
    def calculate_folder_size(self, folder_path):
        """Calcule la taille totale d'un dossier"""
        total_size = 0
        try:
            for dirpath, dirnames, filenames in os.walk(folder_path):
                for filename in filenames:
                    file_path = os.path.join(dirpath, filename)
                    if os.path.exists(file_path):
                        total_size += os.path.getsize(file_path)
        except (OSError, IOError) as e:
            self.logger.warning(f"Erreur lors du calcul de la taille: {e}")
        return total_size
    
    def format_size(self, size_bytes):
        """Formate la taille en octets de manière lisible"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.2f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.2f} TB"
    
    def backup_and_compress(self, source_dir, backup_dir, compression_level=zipfile.ZIP_DEFLATED):
        """
        Sauvegarde et compresse un dossier vers un fichier ZIP
        
        Args:
            source_dir (str): Chemin du dossier source
            backup_dir (str): Chemin du dossier de destination
            compression_level: Niveau de compression ZIP
        
        Returns:
            str: Chemin du fichier de sauvegarde créé
        """
        start_time = datetime.datetime.now()
        
        try:
            # Validation des chemins
            self.validate_paths(source_dir, backup_dir)
            
            # Calcul de la taille source
            source_size = self.calculate_folder_size(source_dir)
            self.logger.info(f"Début de la sauvegarde de '{source_dir}' ({self.format_size(source_size)})")
            
            # Génération du nom de fichier
            zip_filename = self.get_backup_filename()
            zip_path = os.path.join(backup_dir, zip_filename)
            
            # Compteurs pour le suivi
            file_count = 0
            
            # Création de l'archive ZIP
            with zipfile.ZipFile(zip_path, 'w', compression_level) as zipf:
                for root, dirs, files in os.walk(source_dir):
                    for file in files:
                        file_path = os.path.join(root, file)
                        
                        # Vérifier si le fichier existe et est accessible
                        if os.path.exists(file_path) and os.access(file_path, os.R_OK):
                            try:
                                # Chemin relatif pour préserver la structure
                                arcname = os.path.relpath(file_path, start=source_dir)
                                zipf.write(file_path, arcname)
                                file_count += 1
                                
                                # Log de progression tous les 100 fichiers
                                if file_count % 100 == 0:
                                    self.logger.info(f"Traité {file_count} fichiers...")
                                    
                            except (OSError, IOError) as e:
                                self.logger.warning(f"Impossible de sauvegarder le fichier '{file_path}': {e}")
                        else:
                            self.logger.warning(f"Fichier inaccessible: '{file_path}'")
            
            # Vérification de la sauvegarde
            if not os.path.exists(zip_path):
                raise RuntimeError("Le fichier de sauvegarde n'a pas été créé")
            
            # Calcul du temps d'exécution et de la taille finale
            end_time = datetime.datetime.now()
            duration = (end_time - start_time).total_seconds()
            backup_size = os.path.getsize(zip_path)
            compression_ratio = (1 - backup_size / source_size) * 100 if source_size > 0 else 0
            
            # Logs de succès
            self.logger.info(f"✅ Sauvegarde terminée avec succès!")
            self.logger.info(f"📁 Fichier: {zip_path}")
            self.logger.info(f"📊 Statistiques:")
            self.logger.info(f"   - Fichiers traités: {file_count}")
            self.logger.info(f"   - Taille originale: {self.format_size(source_size)}")
            self.logger.info(f"   - Taille compressée: {self.format_size(backup_size)}")
            self.logger.info(f"   - Ratio de compression: {compression_ratio:.1f}%")
            self.logger.info(f"   - Durée: {duration:.2f} secondes")
            
            return zip_path
            
        except Exception as e:
            self.logger.error(f"❌ Erreur lors de la sauvegarde: {e}")
            raise
    
    def list_backups(self, backup_dir):
        """Liste toutes les sauvegardes dans le dossier de destination"""
        try:
            if not os.path.exists(backup_dir):
                return []
            
            backups = []
            for file in os.listdir(backup_dir):
                if file.startswith("backup_") and file.endswith(".zip"):
                    file_path = os.path.join(backup_dir, file)
                    stat = os.stat(file_path)
                    backups.append({
                        'name': file,
                        'path': file_path,
                        'size': stat.st_size,
                        'date': datetime.datetime.fromtimestamp(stat.st_mtime)
                    })
            
            return sorted(backups, key=lambda x: x['date'], reverse=True)
            
        except Exception as e:
            self.logger.error(f"Erreur lors de la liste des sauvegardes: {e}")
            return []

def main():
    """Fonction principale avec interface en ligne de commande"""
    parser = argparse.ArgumentParser(
        description="Script de Sauvegarde Automatique - Groupe 3",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemples d'utilisation:
  python backup.py ~/Documents ~/Backups
  python backup.py /var/www /home/user/backups --verbose
  python backup.py ./project ./backups --list
        """
    )
    
    parser.add_argument('source', nargs='?', help='Dossier source à sauvegarder')
    parser.add_argument('destination', nargs='?', help='Dossier de destination')
    parser.add_argument('--verbose', '-v', action='store_true', help='Mode verbose')
    parser.add_argument('--list', '-l', action='store_true', help='Lister les sauvegardes existantes')
    parser.add_argument('--version', action='version', version='%(prog)s 1.0')
    
    args = parser.parse_args()
    
    # Configuration du niveau de log
    log_level = logging.DEBUG if args.verbose else logging.INFO
    backup_manager = BackupManager(log_level)
    
    try:
        # Mode liste des sauvegardes
        if args.list:
            if not args.destination:
                print("❌ Erreur: Spécifiez le dossier de destination pour lister les sauvegardes")
                return 1
            
            backups = backup_manager.list_backups(args.destination)
            if not backups:
                print(f"📂 Aucune sauvegarde trouvée dans '{args.destination}'")
                return 0
            
            print(f"📂 Sauvegardes trouvées dans '{args.destination}':")
            print("-" * 80)
            for backup in backups:
                print(f"📁 {backup['name']}")
                print(f"   📅 Date: {backup['date'].strftime('%Y-%m-%d %H:%M:%S')}")
                print(f"   📊 Taille: {backup_manager.format_size(backup['size'])}")
                print()
            return 0
        
        # Mode sauvegarde
        if not args.source or not args.destination:
            print("❌ Erreur: Spécifiez le dossier source et destination")
            print("Usage: python backup.py <source> <destination>")
            print("Aide: python backup.py --help")
            return 1
        
        # Expansion des chemins
        source_path = os.path.expanduser(args.source)
        dest_path = os.path.expanduser(args.destination)
        
        # Exécution de la sauvegarde
        backup_path = backup_manager.backup_and_compress(source_path, dest_path)
        print(f"\n🎉 Sauvegarde réussie: {backup_path}")
        return 0
        
    except KeyboardInterrupt:
        print("\n⏹️  Sauvegarde annulée par l'utilisateur")
        return 1
    except Exception as e:
        print(f"Erreur pendant la sauvegarde : {e}")

if __name__ == "__main__":
    sys.exit(main())