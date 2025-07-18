#!/usr/bin/env python3
"""
Interface graphique pour le Script de Sauvegarde Automatique - Groupe 3
Nécessite tkinter (inclus par défaut avec Python)
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import threading
import os
import sys
from pathlib import Path
import logging

# Import du module de sauvegarde
try:
    from backup import BackupManager
except ImportError:
    messagebox.showerror("Erreur", "Le fichier 'backup.py' n'a pas été trouvé dans le même dossier!")
    sys.exit(1)

class BackupGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("🗂️ Sauvegarde Automatique - Groupe 3")
        self.root.geometry("800x600")
        self.root.resizable(True, True)
        
        # Variables
        self.source_var = tk.StringVar()
        self.dest_var = tk.StringVar()
        self.is_running = False
        
        # Initialisation du gestionnaire de sauvegarde
        self.backup_manager = None
        
        # Configuration du style
        self.setup_styles()
        
        # Création de l'interface
        self.create_widgets()
        
        # Centrer la fenêtre
        self.center_window()
    
    def setup_styles(self):
        """Configure les styles de l'interface"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Style personnalisé pour les boutons
        style.configure("Action.TButton", font=("Arial", 10, "bold"))
        style.configure("Success.TButton", background="#4CAF50", foreground="white")
        style.configure("Danger.TButton", background="#f44336", foreground="white")
    
    def center_window(self):
        """Centre la fenêtre sur l'écran"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
    
    def create_widgets(self):
        """Crée tous les widgets de l'interface"""
        # Frame principal
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configuration du redimensionnement
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # Titre
        title_label = ttk.Label(main_frame, text="🗂️ Sauvegarde Automatique", 
                               font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # Sélection du dossier source
        ttk.Label(main_frame, text="📁 Dossier source:").grid(row=1, column=0, sticky=tk.W, pady=5)
        
        source_frame = ttk.Frame(main_frame)
        source_frame.grid(row=1, column=1, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        source_frame.columnconfigure(0, weight=1)
        
        self.source_entry = ttk.Entry(source_frame, textvariable=self.source_var, width=50)
        self.source_entry.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 5))
        
        ttk.Button(source_frame, text="Parcourir", 
                  command=self.browse_source).grid(row=0, column=1)
        
        # Sélection du dossier destination
        ttk.Label(main_frame, text="💾 Dossier destination:").grid(row=2, column=0, sticky=tk.W, pady=5)
        
        dest_frame = ttk.Frame(main_frame)
        dest_frame.grid(row=2, column=1, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        dest_frame.columnconfigure(0, weight=1)
        
        self.dest_entry = ttk.Entry(dest_frame, textvariable=self.dest_var, width=50)
        self.dest_entry.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 5))
        
        ttk.Button(dest_frame, text="Parcourir", 
                  command=self.browse_destination).grid(row=0, column=1)
        
        # Boutons d'action
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=3, column=0, columnspan=3, pady=20)
        
        self.backup_button = ttk.Button(button_frame, text="🚀 Démarrer la sauvegarde", 
                                       command=self.start_backup, style="Action.TButton")
        self.backup_button.pack(side=tk.LEFT, padx=5)
        
        self.list_button = ttk.Button(button_frame, text="📋 Lister les sauvegardes", 
                                     command=self.list_backups)
        self.list_button.pack(side=tk.LEFT, padx=5)
        
        self.clear_button = ttk.Button(button_frame, text="🧹 Effacer les logs", 
                                      command=self.clear_logs)
        self.clear_button.pack(side=tk.LEFT, padx=5)
        
        # Barre de progression
        self.progress_var = tk.StringVar(value="Prêt")
        self.progress_label = ttk.Label(main_frame, textvariable=self.progress_var)
        self.progress_label.grid(row=4, column=0, columnspan=3, pady=5)
        
        self.progress_bar = ttk.Progressbar(main_frame, mode='indeterminate')
        self.progress_bar.grid(row=5, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)
        
        # Zone de logs
        logs_frame = ttk.LabelFrame(main_frame, text="📝 Logs d'exécution", padding="10")
        logs_frame.grid(row=6, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=10)
        logs_frame.columnconfigure(0, weight=1)
        logs_frame.rowconfigure(0, weight=1)
        main_frame.rowconfigure(6, weight=1)
        
        self.log_text = scrolledtext.ScrolledText(logs_frame, height=15, width=80)
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configuration des logs pour affichage dans l'interface
        self.setup_log_handler()
        
        # Chargement des chemins par défaut
        self.load_default_paths()
    
    def setup_log_handler(self):
        """Configure un handler pour afficher les logs dans l'interface"""
        class GUILogHandler(logging.Handler):
            def __init__(self, text_widget):
                super().__init__()
                self.text_widget = text_widget
            
            def emit(self, record):
                log_entry = self.format(record)
                self.text_widget.insert(tk.END, log_entry + '\n')
                self.text_widget.see(tk.END)
                self.text_widget.update()
        
        # Créer et configurer le handler
        self.gui_handler = GUILogHandler(self.log_text)
        self.gui_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
    
    def load_default_paths(self):
        """Charge des chemins par défaut"""
        home = Path.home()
        self.source_var.set(str(home / "Documents"))
        self.dest_var.set(str(home / "Backups"))
    
    def browse_source(self):
        """Ouvre une boîte de dialogue pour sélectionner le dossier source"""
        folder = filedialog.askdirectory(title="Sélectionner le dossier source")
        if folder:
            self.source_var.set(folder)
    
    def browse_destination(self):
        """Ouvre une boîte de dialogue pour sélectionner le dossier destination"""
        folder = filedialog.askdirectory(title="Sélectionner le dossier de destination")
        if folder:
            self.dest_var.set(folder)
    
    def validate_inputs(self):
        """Valide les entrées utilisateur"""
        source = self.source_var.get().strip()
        dest = self.dest_var.get().strip()
        
        if not source:
            messagebox.showerror("Erreur", "Veuillez sélectionner un dossier source")
            return False
        
        if not dest:
            messagebox.showerror("Erreur", "Veuillez sélectionner un dossier de destination")
            return False
        
        if not os.path.exists(source):
            messagebox.showerror("Erreur", f"Le dossier source '{source}' n'existe pas")
            return False
        
        if not os.path.isdir(source):
            messagebox.showerror("Erreur", f"'{source}' n'est pas un dossier")
            return False
        
        return True
    
    def start_backup(self):
        """Démarre la sauvegarde dans un thread séparé"""
        if self.is_running:
            messagebox.showwarning("Attention", "Une sauvegarde est déjà en cours")
            return
        
        if not self.validate_inputs():
            return
        
        # Démarrer la sauvegarde dans un thread séparé
        backup_thread = threading.Thread(target=self.run_backup)
        backup_thread.daemon = True
        backup_thread.start()
    
    def run_backup(self):
        """Exécute la sauvegarde"""
        try:
            self.is_running = True
            self.update_ui_state(True)
            
            # Créer le gestionnaire de sauvegarde
            self.backup_manager = BackupManager()
            
            # Ajouter le handler GUI au logger
            logger = logging.getLogger('backup')
            logger.addHandler(self.gui_handler)
            logger.setLevel(logging.INFO)
            
            # Lancer la sauvegarde
            source = self.source_var.get().strip()
            dest = self.dest_var.get().strip()
            
            self.progress_var.set("Sauvegarde en cours...")
            
            backup_path = self.backup_manager.backup_and_compress(source, dest)
            
            self.progress_var.set("Sauvegarde terminée ✅")
            
            # Afficher le résultat
            messagebox.showinfo("Succès", f"Sauvegarde terminée avec succès!\n\nFichier: {backup_path}")
            
        except Exception as e:
            self.progress_var.set("Erreur lors de la sauvegarde ❌")
            messagebox.showerror("Erreur", f"Erreur lors de la sauvegarde:\n{str(e)}")
        finally:
            self.is_running = False
            self.update_ui_state(False)
    
    def update_ui_state(self, is_running):
        """Met à jour l'état de l'interface selon l'état de la sauvegarde"""
        def update():
            if is_running:
                self.backup_button.config(text="⏳ Sauvegarde en cours...", state='disabled')
                self.progress_bar.start()
            else:
                self.backup_button.config(text="🚀 Démarrer la sauvegarde", state='normal')
                self.progress_bar.stop()
                self.progress_var.set("Prêt")
        
        # Exécuter dans le thread principal
        self.root.after(0, update)
    
    def list_backups(self):
        """Liste les sauvegardes existantes"""
        dest = self.dest_var.get().strip()
        if not dest:
            messagebox.showerror("Erreur", "Veuillez sélectionner un dossier de destination")
            return
        
        try:
            # Créer le gestionnaire si nécessaire
            if not self.backup_manager:
                self.backup_manager = BackupManager()
            
            backups = self.backup_manager.list_backups(dest)
            
            if not backups:
                messagebox.showinfo("Information", f"Aucune sauvegarde trouvée dans '{dest}'")
                return
            
            # Créer une fenêtre pour afficher les sauvegardes
            self.show_backups_window(backups)
            
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors de la liste des sauvegardes:\n{str(e)}")
    
    def show_backups_window(self, backups):
        """Affiche une fenêtre avec la liste des sauvegardes"""
        backup_window = tk.Toplevel(self.root)
        backup_window.title("📋 Liste des sauvegardes")
        backup_window.geometry("600x400")
        backup_window.resizable(True, True)
        
        # Frame principal
        frame = ttk.Frame(backup_window, padding="10")
        frame.pack(fill=tk.BOTH, expand=True)
        
        # Titre
        ttk.Label(frame, text="📋 Sauvegardes disponibles", 
                 font=("Arial", 12, "bold")).pack(pady=(0, 10))
        
        # Treeview pour afficher les sauvegardes
        columns = ('Nom', 'Date', 'Taille')
        tree = ttk.Treeview(frame, columns=columns, show='headings', height=15)
        
        # Configuration des colonnes
        tree.heading('Nom', text='Nom du fichier')
        tree.heading('Date', text='Date de création')
        tree.heading('Taille', text='Taille')
        
        tree.column('Nom', width=300)
        tree.column('Date', width=150)
        tree.column('Taille', width=100)
        
        # Ajout des données
        for backup in backups:
            tree.insert('', tk.END, values=(
                backup['name'],
                backup['date'].strftime('%Y-%m-%d %H:%M:%S'),
                self.backup_manager.format_size(backup['size'])
            ))
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        
        # Placement
        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Bouton fermer
        ttk.Button(backup_window, text="Fermer", 
                  command=backup_window.destroy).pack(pady=10)
    
    def clear_logs(self):
        """Efface les logs affichés"""
        self.log_text.delete(1.0, tk.END)
        self.log_text.insert(tk.END, "Logs effacés\n")

def main():
    """Fonction principale"""
    root = tk.Tk()
    app = BackupGUI(root)
    
    try:
        root.mainloop()
    except KeyboardInterrupt:
        print("Application fermée par l'utilisateur")

if __name__ == "__main__":
    main()