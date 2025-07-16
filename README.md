# 💾 Script de Sauvegarde Automatique (Groupe 3)

## 🎯 Objectif
Ce projet a pour but de développer un script Python qui sauvegarde un dossier vers un autre emplacement, avec compression ZIP et horodatage.

## 👥 Membres du groupe
- Mohamed Bechir Diarra (Chef de projet)
- Membre 2 : Sauvegarde
- Membre 3 : Compression
- Membre 4 : Logs & Tests
- Membre 5 : Intégration finale

## 📁 Structure du projet
```
backup.py  
logs/  
test/  
cron/  
README.md  
.gitignore  
```

## ⚙️ Utilisation
```bash
python backup.py dossier_source dossier_destination
```

## 🧪 Tests
```bash
python -m unittest discover test
```

## 🔗 Dépôt GitHub
[VersionningTdGroupe3](https://github.com/bech-code/VersionningTdGroupe3)

## 📂 .gitignore
Ajoute tous les fichiers inutiles à ignorer dans `.gitignore` :
- `__pycache__/`
- `*.pyc`
- `*.log`
- `*.zip`
