#!/usr/bin/env python3
"""
Tests unitaires pour le Script de Sauvegarde Automatique - Groupe 3
Auteur: Aboubacar S Magasouba (branche test-logs)
"""

import unittest
import tempfile
import os
import shutil
import zipfile
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock
import logging

# Ajouter le répertoire parent au path pour importer backup
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from backup import BackupManager
except ImportError as e:
    print(f"Erreur d'import: {e}")
    sys.exit(1)

class TestBackupManager(unittest.TestCase):
    """Tests pour la classe BackupManager"""
    
    def setUp(self):
        """Préparation avant chaque test"""
        # Créer des répertoires temporaires
        self.temp_dir = tempfile.mkdtemp()
        self.source_dir = os.path.join(self.temp_dir, "source")
        self.backup_dir = os.path.join(self.temp_dir, "backup")
        
        # Créer le répertoire source
        os.makedirs(self.source_dir)
        
        # Créer quelques fichiers de test
        self.create_test_files()
        
        # Initialiser le gestionnaire de sauvegarde
        self.backup_manager = BackupManager(log_level=logging.CRITICAL)  # Réduire les logs pour les tests
    
    def tearDown(self):
        """Nettoyage après chaque test"""
        # Supprimer les répertoires temporaires
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def create_test_files(self):
        """Crée des fichiers de test dans le répertoire source"""
        # Fichier texte simple
        with open(os.path.join(self.source_dir, "test.txt"), "w") as f:
            f.write("Contenu de test")
        
        # Créer un sous-dossier avec des fichiers
        sub_dir = os.path.join(self.source_dir, "subdir")
        os.makedirs(sub_dir)
        
        with open(os.path.join(sub_dir, "subfile.txt"), "w") as f:
            f.write("Fichier dans sous-dossier")
        
        # Fichier binaire (simulé)
        with open(os.path.join(self.source_dir, "binary.bin"), "wb") as f:
            f.write(b'\x00\x01\x02\x03\x04\x05')
    
    def test_backup_manager_initialization(self):
        """Test l'initialisation du BackupManager"""
        self.assertIsNotNone(self.backup_manager)
        self.assertIsNotNone(self.backup_manager.logger)
    
    def test_validate_paths_valid(self):
        """Test la validation avec des chemins valides"""
        try:
            self.backup_manager.validate_paths(self.source_dir, self.backup_dir)
        except Exception as e:
            self.fail(f"validate_paths a échoué avec des chemins valides: {e}")
    
    def test_validate_paths_invalid_source(self):
        """Test la validation avec un répertoire source inexistant"""
        invalid_source = os.path.join(self.temp_dir, "inexistant")
        with self.assertRaises(ValueError):
            self.backup_manager.validate_paths(invalid_source, self.backup_dir)
    
    def test_get_backup_filename(self):
        """Test la génération du nom de fichier de sauvegarde"""
        filename = self.backup_manager.get_backup_filename()
        self.assertTrue(filename.startswith("backup_"))
        self.assertTrue(filename.endswith(".zip"))
        self.assertIn("_", filename)  # Vérifier la présence du timestamp
    
    def test_get_backup_filename_custom_prefix(self):
        """Test la génération du nom avec un préfixe personnalisé"""
        filename = self.backup_manager.get_backup_filename("custom")
        self.assertTrue(filename.startswith("custom_"))
        self.assertTrue(filename.endswith(".zip"))
    
    def test_calculate_folder_size(self):
        """Test le calcul de la taille d'un dossier"""
        size = self.backup_manager.calculate_folder_size(self.source_dir)
        self.assertGreater(size, 0)
        self.assertIsInstance(size, int)
    
    def test_calculate_folder_size_empty_dir(self):
        """Test le calcul de la taille d'un dossier vide"""
        empty_dir = os.path.join(self.temp_dir, "empty")
        os.makedirs(empty_dir)
        size = self.backup_manager.calculate_folder_size(empty_dir)
        self.assertEqual(size, 0)
    
    def test_format_size(self):
        """Test le formatage de la taille"""
        self.assertEqual(self.backup_manager.format_size(1024), "1.00 KB")
        self.assertEqual(self.backup_manager.format_size(1024 * 1024), "1.00 MB")
        self.assertEqual(self.backup_manager.format_size(1024 * 1024 * 1024), "1.00 GB")
        self.assertEqual(self.backup_manager.format_size(500), "500.00 B")
    
    def test_backup_and_compress_success(self):
        """Test une sauvegarde réussie"""
        backup_path = self.backup_manager.backup_and_compress(self.source_dir, self.backup_dir)
        
        # Vérifier que le fichier de sauvegarde existe
        self.assertTrue(os.path.exists(backup_path))
        self.assertTrue(backup_path.endswith(".zip"))
        
        # Vérifier que c'est un fichier ZIP valide
        self.assertTrue(zipfile.is_zipfile(backup_path))
        
        # Vérifier le contenu du ZIP
        with zipfile.ZipFile(backup_path, 'r') as zipf:
            file_list = zipf.namelist()
            self.assertIn("test.txt", file_list)
            self.assertIn("subdir/subfile.txt", file_list)
            self.assertIn("binary.bin", file_list)
    
    def test_backup_and_compress_invalid_source(self):
        """Test une sauvegarde avec source invalide"""
        invalid_source = os.path.join(self.temp_dir, "inexistant")
        with self.assertRaises(ValueError):
            self.backup_manager.backup_and_compress(invalid_source, self.backup_dir)
    
    def test_backup_and_compress_creates_destination(self):
        """Test que la sauvegarde crée le répertoire de destination"""
        non_existent_dest = os.path.join(self.temp_dir, "new_backup_dir")
        backup_path = self.backup_manager.backup_and_compress(self.source_dir, non_existent_dest)
        
        self.assertTrue(os.path.exists(non_existent_dest))
        self.assertTrue(os.path.exists(backup_path))
    
    def test_list_backups_empty_directory(self):
        """Test la liste des sauvegardes dans un répertoire vide"""
        os.makedirs(self.backup_dir)
        backups = self.backup_manager.list_backups(self.backup_dir)
        self.assertEqual(len(backups), 0)
    
    def test_list_backups_with_backups(self):
        """Test la liste des sauvegardes avec des fichiers existants"""
        # Créer une sauvegarde
        backup_path = self.backup_manager.backup_and_compress(self.source_dir, self.backup_dir)
        
        # Lister les sauvegardes
        backups = self.backup_manager.list_backups(self.backup_dir)
        
        self.assertEqual(len(backups), 1)
        self.assertEqual(backups[0]['path'], backup_path)
        self.assertTrue(backups[0]['name'].startswith("backup_"))
        self.assertGreater(backups[0]['size'], 0)
    
    def test_list_backups_nonexistent_directory(self):
        """Test la liste des sauvegardes dans un répertoire inexistant"""
        non_existent = os.path.join(self.temp_dir, "inexistant")
        backups = self.backup_manager.list_backups(non_existent)
        self.assertEqual(len(backups), 0)
    
    def test_backup_preserves_structure(self):
        """Test que la sauvegarde preserve la structure des dossiers"""
        backup_path = self.backup_manager.backup_and_compress(self.source_dir, self.backup_dir)
        
        # Extraire et vérifier la structure
        extract_dir = os.path.join(self.temp_dir, "extract")
        os.makedirs(extract_dir)
        
        with zipfile.ZipFile(backup_path, 'r') as zipf:
            zipf.extractall(extract_dir)
        
        # Vérifier que les fichiers sont bien présents
        self.assertTrue(os.path.exists(os.path.join(extract_dir, "test.txt")))
        self.assertTrue(os.path.exists(os.path.join(extract_dir, "subdir", "subfile.txt")))
        self.assertTrue(os.path.exists(os.path.join(extract_dir, "binary.bin")))
    
    def test_backup_file_content_integrity(self):
        """Test que le contenu des fichiers est préservé"""
        backup_path = self.backup_manager.backup_and_compress(self.source_dir, self.backup_dir)
        
        # Extraire et vérifier le contenu
        extract_dir = os.path.join(self.temp_dir, "extract")
        os.makedirs(extract_dir)
        
        with zipfile.ZipFile(backup_path, 'r') as zipf:
            zipf.extractall(extract_dir)
        
        # Vérifier le contenu du fichier texte
        with open(os.path.join(extract_dir, "test.txt"), "r") as f:
            content = f.read()
            self.assertEqual(content, "Contenu de test")
        
        # Vérifier le contenu du fichier binaire
        with open(os.path.join(extract_dir, "binary.bin"), "rb") as f:
            content = f.read()
            self.assertEqual(content, b'\x00\x01\x02\x03\x04\x05')
    
    def test_multiple_backups_different_names(self):
        """Test que plusieurs sauvegardes ont des noms différents"""
        backup1 = self.backup_manager.backup_and_compress(self.source_dir, self.backup_dir)
        
        # Attendre un peu pour avoir un timestamp différent
        import time
        time.sleep(1)
        
        backup2 = self.backup_manager.backup_and_compress(self.source_dir, self.backup_dir)
        
        # Vérifier que les noms sont différents
        self.assertNotEqual(os.path.basename(backup1), os.path.basename(backup2))
        
        # Vérifier que les deux fichiers existent
        self.assertTrue(os.path.exists(backup1))
        self.assertTrue(os.path.exists(backup2))
    
    @patch('os.access')
    def test_backup_permission_error(self, mock_access):
        """Test la gestion des erreurs de permission"""
        # Simuler l'absence de permission de lecture
        mock_access.return_value = False
        
        with self.assertRaises(PermissionError):
            self.backup_manager.backup_and_compress(self.source_dir, self.backup_dir)
    
    def test_backup_with_empty_source(self):
        """Test la sauvegarde d'un dossier vide"""
        empty_source = os.path.join(self.temp_dir, "empty_source")
        os.makedirs(empty_source)
        
        backup_path = self.backup_manager.backup_and_compress(empty_source, self.backup_dir)
        
        self.assertTrue(os.path.exists(backup_path))
        self.assertTrue(zipfile.is_zipfile(backup_path))
        
        # Vérifier que le ZIP est vide
        with zipfile.ZipFile(backup_path, 'r') as zipf:
            self.assertEqual(len(zipf.namelist()), 0)
    
    def test_backup_with_special_characters(self):
        """Test la sauvegarde avec des caractères spéciaux dans les noms"""
        special_file = os.path.join(self.source_dir, "fichier_spécial_éàù.txt")
        with open(special_file, "w", encoding="utf-8") as f:
            f.write("Contenu avec caractères spéciaux: éàù")
        
        backup_path = self.backup_manager.backup_and_compress(self.source_dir, self.backup_dir)
        
        # Vérifier que le fichier est dans l'archive
        with zipfile.ZipFile(backup_path, 'r') as zipf:
            file_list = zipf.namelist()
            self.assertTrue(any("fichier_spécial" in name for name in file_list))

class TestBackupCLI(unittest.TestCase):
    """Tests pour l'interface en ligne de commande"""
    
    def setUp(self):
        """Préparation avant chaque test"""
        self.temp_dir = tempfile.mkdtemp()
        self.source_dir = os.path.join(self.temp_dir, "source")
        self.backup_dir = os.path.join(self.temp_dir, "backup")
        
        os.makedirs(self.source_dir)
        
        # Créer un fichier de test
        with open(os.path.join(self.source_dir, "test.txt"), "w") as f:
            f.write("Test CLI")
    
    def tearDown(self):
        """Nettoyage après chaque test"""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    @patch('sys.argv', ['backup.py', '--help'])
    def test_cli_help(self):
        """Test l'aide de la CLI"""
        with patch('sys.exit') as mock_exit:
            try:
                from backup import main
                main()
            except SystemExit:
                pass
            mock_exit.assert_called()
    
    @patch('sys.argv')
    def test_cli_backup_success(self, mock_argv):
        """Test une sauvegarde réussie via CLI"""
        mock_argv.__getitem__ = lambda self, index: [
            'backup.py', self.source_dir, self.backup_dir
        ][index]
        mock_argv.__len__ = lambda self: 3
        
        # Importer et tester la fonction main
        from backup import main
        result = main()
        
        # Vérifier que la sauvegarde a été créée
        self.assertTrue(os.path.exists(self.backup_dir))
        backup_files = [f for f in os.listdir(self.backup_dir) if f.endswith('.zip')]
        self.assertGreater(len(backup_files), 0)

if __name__ == '__main__':
    # Configuration des tests
    unittest.main(verbosity=2, buffer=True)