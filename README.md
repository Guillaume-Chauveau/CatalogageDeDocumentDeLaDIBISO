# Manuel Technique de l'Application de Rétrocatalogage de Documents

## Introduction

Cette application est une interface graphique développée en Python utilisant PySide6 pour la gestion et l'édition de fiches bibliographiques extraites de documents scannés. Elle permet de traiter des informations provenant de sorties LLM (Large Language Models) pour créer des formulaires structurés, les éditer manuellement et les exporter dans un format spécifique.

L'application est conçue pour faciliter le catalogage de documents scientifiques, en particulier des articles et ouvrages en chimie.

## Architecture Générale

L'application suit une architecture modulaire avec séparation des préoccupations :

- **Interface Utilisateur** : Fenêtres et formulaires créés avec Qt Designer (.ui files)
- **Logique Métier** : Classes Python gérant les données et les opérations
- **Persistance** : Fichiers texte pour stocker les données des fiches
- **Intégration LLM** : Utilisation de sorties prétraitées par IA

### Structure des Dossiers

```
app/
├── main.py                # Gestion des intération entre les interface et le code
├── Fiche.py               # Classe principale pour gérer les fiches
├── Caracteristique.py     # Classe de base pour les caractéristiques
├── CaracteristiqueMultiple.py # Extension pour caractéristiques multiples
├── ListeAFinir.py         # Gestion du catalogue et du répertoire courant
├── Parametre.py           # Interface d'information et lieu pour rentré la clef API
├── FormulaireAuteur.py    # Formulaire pour auteurs
├── FormulaireChampsScientifique.py # Formulaire pour champs scientifiques
├── Statistique.py         # Non intégré a la version final mais peut toujours etre utilisé avec par ligne de code
├── UI/                   # Interfaces Qt Designer
│   ├── *.ui              # Fichiers d'interface
│   └── *_ui.py           # Code Python généré
├── Doc/                  # Docier de travaile pour la création des fiches
├── LLMOutput/            # Docier de sauvegarde de la vertion original des fiches
├── Scan/                 # Docier qui regroupe les images scannées ajouté une par une
├── Sortie/               # Exports finaux respectant le standart UniMARC
├── Backend/              # Docier qui regroupe les codes relatifit a l'API
│   ├── convert_json_to_txt.py #Fichier convertisant les JSON donné par le LLM en txt utilisé par l'interface graphique
│   ├──
└── Image/                # Ressources graphiques
```

## Classes Principales

### Classe Fiche

**Fichier** : `Fiche.py`

La classe `Fiche` représente une fiche bibliographique complète. Elle gère :

- **Attributs principaux** :
  - `window` : Référence à la fenêtre Qt
  - `listeDesCaracteristiques` : Liste des caractéristiques de la fiche
  - `chemain` : Chemin vers le fichier de données
  - `nomDuFichier` : Nom du fichier traité

- **Méthodes clés** :
  - `__init__()` : Initialisation avec chargement des caractéristiques
  - `lecture()` : Lecture des données depuis fichier
  - `affichage()` : Génération du texte d'export au format MARC
  - `ecriture()` : Sauvegarde et export
  - `sauvgarde()` : Sauvegarde dans Doc/
  - `exportation()` : Export dans Sortie/
  - `zoom()` / `resetZoom()` : Gestion du zoom sur l'image
  - `calculeDeLaBareCentrale()` : Calcul de la progression globale

### Classe Caracteristique

**Fichier** : `Caracteristique.py`

Classe de base pour représenter une caractéristique simple d'une fiche.

- **Attributs** :
  - `nom` : Nom de la caractéristique
  - `id` : Identifiant numérique
  - `valeur` : Valeur actuelle
  - `edite` : Indicateur d'édition manuelle
  - `proba` : Probabilité/confiance (0-100)

### Classe CaracteristiqueMultiple

**Fichier** : `CaracteristiqueMultiple.py`

Extension de `Caracteristique` pour gérer des valeurs multiples (listes).

- **Particularités** :
  - Valeur stockée comme liste
  - `getValeur()` retourne une chaîne jointe par ", "
  - Méthodes spéciales pour champs scientifiques

### Classe ListeAFinir

**Fichier** : `ListeAFinir.py`

Gère le catalogue des documents à traiter.

- **Attributs** :
  - `Fiches` : Liste de tous les documents
  - `FichesNonFinies` : Documents non encore exportés

- **Méthodes** :
  - `creerCatalogue()` : Affichage selon filtre
  - `openFileDialog()` : Ajout de nouveaux documents

### Classe FormulaireAuteur

**Fichier** : `FormulaireAuteur.py`

Permet de saisir plusieurs auteurs, co-auteurs et auteurs secondaires avec leurs rôles respectifs à l’aide de lignes dynamiques ajoutables/supprimables.

### Classe FormulaireChampsScientifique

**Fichier** : `FormulaireChampsScientifique.py`

Permet de sélectionner plusieurs champs scientifiques depuis une liste dynamique et d’ajouter de nouveaux libellés si nécessaire.

### Classe Statistique

**Fichier** : `Statistique.py`

Calcule des indicateurs de qualité et de complétion des fiches, tels que le ratio de saisie humaine, le pourcentage de fiches traitées et les erreurs constatées par caractéristique.

## Éléments récemment ajoutés

- Gestion de formulaires secondaires pour les auteurs et les champs scientifiques
- Import de nouveaux documents à partir d’images sélectionnées dans le système
- Choix du répertoire de scans depuis le catalogue
- Affichage d’éléments statistiques graphiques dans une fenêtre dédiée
- Redimensionnement dynamique de l’interface et zoom sur l’image scannée

## Flux d'Utilisation

1. **Démarrage** : `main.py` lance l'application et affiche le catalogue
2. **Sélection** : Utilisateur choisit un document dans la liste
3. **Chargement** : Création d'une instance `Fiche` avec données préremplies
4. **Édition** : Modification manuelle des champs via l'interface
5. **Validation** : Sauvegarde et export au format MARC
6. **Navigation** : Retour au catalogue ou visualisation du rendu

## Format de Données

### Fichiers d'Entrée (LLMOutput/ et Doc/)

Format : `label$valeur$probabilite$edite`

Exemple :
```
Titre$Influence des agents physiques$85$0
Auteur$Liebig, Justus$92$1
Annee$1850$78$0
```

Les champs multi-valués, comme les auteurs et les champs scientifiques, sont remplis dans des formulaires spécifiques puis réinjectés dans la fiche principale. Les valeurs sont ensuite sauvegardées dans les fichiers texte au format ci-dessus.

### Format d'Export (Sortie/)

Format MARC simplifié avec codes spécifiques :

- `200` : Titre et auteurs principaux
- `210` : Informations de publication
- `606` : Champs scientifiques
- `700/701/702` : Auteurs et rôles
- `712` : Collectivités

## Interface Utilisateur

### Fenêtres Principales

1. **Catalogue** (`changementDePage.ui`)
   - Liste des documents avec filtre "Voir fini"
   - Boutons : Actualiser, Paramètres, Ajouter fichier, Statistiques, Choisir un nouveau dossier de base

2. **Formulaire** (`Formulaire.ui`)
   - Grille d'édition des caractéristiques
   - Barre de progression centrale
   - Boutons : Validation, Quitter, Zoom, Sauvegarde, Reset

3. **Rendu** (`RenduFormulaire.ui`)
   - Affichage du texte exporté
   - Boutons : Copier, Retour au formulaire, Retour au catalogue

4. **Paramètres** (`Parametre.ui`)
   - Configuration des types de traitement et des paramètres à afficher

5. **Statistiques** (`Statistiques.ui`)
   - Graphiques de progression, de saisie humaine et d’erreurs par caractéristique

### Gestion Dynamique du Layout

La fonction `activerRedimensionnementDynamique()` assure que l'interface s'adapte aux redimensionnements :

- Gestion des `QMainWindow` avec `centralwidget`
- Support des `QDialog` et `QWidget`
- Configuration récursive des enfants

## Installation et Exécution

### Prérequis

- Python 3.x
- PySide6
- Qt Designer (pour modification des .ui)

### Installation

```bash
pip install PySide6
```

### Exécution

```bash
python main.py
```

### Création d'un build

```bash
pyinstaller editor.spec
```
### Structure des Données

Créer les dossiers suivants dans le répertoire de l'application :
- `Doc/` : Documents traités
- `LLMOutput/` : Sorties brutes du LLM
- `Scan/` : Images scannées
- `Sortie/` : Exports finaux
- `Image/` : Ressources graphiques

## Détails Techniques

### Gestion des Caractéristiques

La liste des caractéristiques est définie dans `Fiche.listeDesNom` :

```python
listeDesNom = ["Article", "Titre", "Auteur", "Complement du titre",
               "Numero du volume", "Ville", "Editeur", "Annee",
               "Illustration", "Dimension", "Indexation Rameau",
               "Premier Auteur", "Co-Auteur", "Role Auteur", "Role CoAuteur",
               "Auteur Secondaire", "Role Auteur Secondaire",
               "Nom de la Collectivite", "Role de la Collectivite"]
```

Les caractéristiques multiples sont définies dans `listeDesCaracteristiquesMultiple`.

### Calcul des Probabilités

- Couleurs selon seuils :
  - ≤30 : Rouge
  - ≤50 : Orange
  - ≤75 : Jaune
  - ≤99 : Vert
  - 100 : Cyan

### Zoom et Navigation

- Zoom factoriel sur l'image scannée
- Reset du zoom disponible
- Navigation entre formulaires préservée

### Export MARC

Le format d'export suit une structure MARC simplifiée avec des codes spécifiques pour les champs bibliographiques en chimie.

## Maintenance et Extension

### Ajout de Nouvelles Caractéristiques

1. Ajouter le nom dans `Fiche.listeDesNom`
2. Définir l'indice dans les constantes
3. Adapter `affichage()` pour l'export
4. Mettre à jour l'interface Qt Designer si nécessaire

### Modification des Formats

- Éditer `Fiche.affichage()` pour changer le format d'export
- Adapter `Fiche.lecture()` pour nouveaux formats d'entrée

### Debugging

- Logs dans la console pour les opérations principales
- Indicateurs visuels (points colorés, barres de progression)
- Validation des chemins de fichiers

### Création de son propre build
- Utiliser `pyinstaller` avec un fichier `editor.spec` adapté pour inclure toutes les dépendances et ressources nécessaires.
- Lancer le build avec la commande:
 ``` bash
 python -m PyInstaller --clean --noconfirm editor.spec
 ``` 

## Conclusion

Cette application fournit une interface efficace pour le catalogage semi-automatisé de documents scientifiques, combinant les capacités des LLM avec l'édition manuelle experte. Son architecture modulaire facilite la maintenance et l'extension pour de nouveaux types de documents ou formats d'export.
