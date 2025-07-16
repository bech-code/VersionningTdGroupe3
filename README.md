💾 Script de Sauvegarde Automatique – Groupe 3

🎯 Objectif du Projet

Ce projet a été réalisé dans le cadre du module de **Versionning avec Git**.  
Il a pour objectif de développer un script Python permettant de **sauvegarder automatiquement un dossier** vers un autre emplacement, avec :

- 📦 **Compression ZIP**
- 🕒 **Horodatage de la sauvegarde**
- 🧾 **Logs d’exécution**
- 🔁 **Fonctionnement planifiable (via cron)**
- ✅ **Tests automatisés**

---

👥 Membres de l'équipe (Groupe 3)

| Nom                      | Rôle                               | Branche Git              |
|--------------------------|------------------------------------|--------------------------|
| Mohamed Bechir Diarra    | Chef de projet & Documentation     | `docs`                   |
| Cecile Penda             | Développement sauvegarde           | `backup-script`          |
| Ousmane Camara           | Compression & Horodatage           | `compression-feature`    |
| Aboubacar S Magasouba    | Logs & Tests                       | `test-logs`              |
| Membre 5                 | Intégration finale & Conflits      | `integration`            |

---

## 🗂️ Structure du Projet

```
backup.py            # Script principal de sauvegarde
logs/                # Fichiers de log générés automatiquement
test/                # Scripts de test unitaire
cron/                # Exemples de planification automatique
README.md            # Présentation du projet
.gitignore           # Fichiers ignorés par Git
```

---

## ⚙️ Utilisation du Script

```bash
python backup.py chemin/du/dossier_source chemin/du/dossier_destination
```

📝 Exemple :
```bash
python backup.py ~/Documents/mon_projet ~/Sauvegardes
```

📦 Cela génèrera un fichier ZIP dans le dossier destination, avec un nom comme :
```
backup_2025-07-16_22-30-42.zip
```

---

## 🧪 Tests

Le projet contient des tests unitaires pour vérifier le bon fonctionnement du script.

```bash
python -m unittest discover test
```

---

## 🗓️ Planification automatique (exemple cron)

Vous pouvez automatiser l’exécution du script avec une tâche cron (Linux/macOS).  
Exemple pour une exécution tous les jours à 2h du matin :

```bash
0 2 * * * /usr/bin/python3 /chemin/vers/backup.py /source /destination
```

---

## 📂 `.gitignore`

Le fichier `.gitignore` permet d’exclure de la version Git les fichiers et dossiers suivants :

```
__pycache__/
*.pyc
*.zip
*.log
logs/
```

---

## 🔗 Dépôt GitHub

📁 Projet disponible sur GitHub :  
👉 [https://github.com/bech-code/VersionningTdGroupe3](https://github.com/bech-code/VersionningTdGroupe3)

---

## 🧠 Git & Collaboration

Ce projet a été développé en mode collaboratif avec Git.  
Chaque membre a :
- Travaillé dans une branche dédiée
- Réalisé plusieurs commits clairs
- Fait une **pull request** vers `main`
- Participé à la **résolution de conflits**
- Contribué à la version finale intégrée et taguée `v1.0`

---

## ✅ Livrables demandés

- [x] 📁 Dépôt GitHub distant
- [x] 🌿 Travail en branches
- [x] ✅ Commits clairs
- [x] 🔀 Pull requests et gestion de conflits
- [x] 📄 Fichier `.gitignore`
- [x] 📝 Fichier `README.md`
- [x] 🎥 Présentation orale & PowerPoint

---

🧠 *Projet réalisé dans le cadre d'un TD de versionning à l'ISTA - GL3 2025*
