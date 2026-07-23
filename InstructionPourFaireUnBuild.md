# Création de son propre build

## Dépendances nécessaires

* Python 3.x
* PySide6
* PyInstaller
* matplotlib
* openai

## Étapes pour créer un build

### 1. Installer les dépendances nécessaires :

```bash
pip install PySide6

```

```bash
pip install PySide6 pyinstaller

```

### 2. Vérifier que les dossiers sont vides :

* Le build réutilise tout ce qui est dans l'application. Pour ne pas poser de problème, il est *fortement* recommandé de supprimer tout ce qui se trouve dans les dossiers et fichiers suivants :

```
   -Doc/
   -LLMOutput/
   -outputs/
   -Scan/
   -Sortie/
   -.clef.txt # pour ne pas donner sa clé à toutes les personnes qui vont utiliser la nouvelle version

```

### 3. Créer la base de l'application :

* Utiliser `pyinstaller` avec le fichier `editor.spec` adapté pour inclure toutes les dépendances et ressources nécessaires.
* Lancer le build avec la commande :

```bash
  python -m PyInstaller --noconfirm editor.spec

```

### 4. Ajouter les fichiers manquants

* Cette partie pourra être modifiée en fonction de l'évolution des efforts de maintenance.
* L'application doit contenir à la fin :

```
dist/
├── retro_catalogage/
    ├── retro_catalogage.exe
    ├── .clef.txt  # pensez à activer la vision des éléments cachés pour pouvoir la voir
    ├── _internal/
        ├── # tous les éléments générés automatiquement
        ├── Doc/
        ├── LLMOutput/
        ├── Scan/
        ├── Sortie/

