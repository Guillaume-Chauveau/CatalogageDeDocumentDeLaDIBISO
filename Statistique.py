"""
Module de statistiques sur le corpus de documents catalogues.

Architecture :
- StatistiqueCache : lit une seule fois chaque fichier de champs (Doc/*.txt),
  garde le resultat dans un JSON (.stats_cache.json) indexe par mtime, et ne
  reparse que les fichiers nouveaux ou modifies a chaque appel de actualiser().
  -> ajouter un document et recliquer sur "Statistiques" ne recalcule QUE ce
  document, pas l'ensemble du corpus.
- Statistique : consomme le cache et expose des methodes de dessin
  (matplotlib Figure) pour un tableau de bord par defaut + un graphique
  generique ou l'axe X (regroupement) et l'axe Y (metrique) sont au choix.
"""

import json
import os
from pathlib import Path
from statistics import mean

from matplotlib.figure import Figure

from app_paths import get_data_dir


# --------------------------------------------------------------------------- #
# Cache incremental
# --------------------------------------------------------------------------- #

class StatistiqueCache:
    """Parse chaque fichier de champs une seule fois et garde le resultat en cache."""

    NOM_FICHIER_CACHE = "stats_cache.json"
    VERSION = 2  # a incrementer si le format d'une entree change (invalide le cache existant)

    @staticmethod
    def _getCacheDir() -> Path:
        # Meme emplacement que Parametre.CONFIG_FILE : jamais dans Doc, donc
        # jamais listé par ListeAFinir.ajouterFicheAuto() (os.listdir(Doc)).
        cache_dir = Path.home() / ".app_config"
        cache_dir.mkdir(parents=True, exist_ok=True)
        return cache_dir

    def __init__(self):
        self.dossier_doc = get_data_dir("Doc")
        self.dossier_sortie = get_data_dir("Sortie")
        self.dossier_llm = get_data_dir("LLMOutput")
        self.chemin_cache = self._getCacheDir() / self.NOM_FICHIER_CACHE
        self.documents_par_nom = self._charger()

    # -- persistance ---------------------------------------------------- #

    def _charger(self):
        if os.path.exists(self.chemin_cache):
            try:
                with open(self.chemin_cache, "r", encoding="utf-8") as f:
                    contenu = json.load(f)
                if isinstance(contenu, dict) and contenu.get("_version") == self.VERSION:
                    documents = contenu.get("documents", {})
                    if isinstance(documents, dict):
                        return documents
            except (json.JSONDecodeError, OSError, AttributeError, TypeError):
                pass
        # Fichier absent, corrompu, ou format inattendu : on repart d'un cache
        # vide -> actualiser() reconstruira tout depuis les fichiers Doc/*.txt.
        return {}

    def _sauvegarder(self):
        try:
            with open(self.chemin_cache, "w", encoding="utf-8") as f:
                json.dump(
                    {"_version": self.VERSION, "documents": self.documents_par_nom},
                    f, ensure_ascii=False, indent=2,
                )
        except OSError:
            # Echec d'ecriture (disque plein, droits...) : les stats du jour
            # restent affichees, seul le cache disque n'est pas mis a jour ;
            # tout sera reparse au prochain lancement.
            pass

    # -- lecture des fichiers de champs ---------------------------------- #

    @staticmethod
    def _lireFichierDeChamps(chemin):
        """label$valeur$proba$edit -> {label: {valeur, proba, edite}}"""
        champs = {}
        if not os.path.exists(chemin):
            return champs
        with open(chemin, "r", encoding="utf-8") as f:
            for ligne in f:
                ligne = ligne.rstrip("\n")
                if not ligne:
                    continue
                morceaux = ligne.split("$", 3)
                if len(morceaux) != 4:
                    continue
                label, valeur, proba, edit = morceaux
                try:
                    proba_flottant = float(proba) if proba not in ("", "None") else None
                except ValueError:
                    proba_flottant = None
                champs[label] = {
                    "valeur": valeur.strip(),
                    "proba": proba_flottant,
                    "edite": edit == "1",
                }
        return champs

    @staticmethod
    def _normaliserValeur(valeur):
        """Compare deux valeurs sans tenir compte de l'ordre pour les champs
        multi-valeurs (separes par '; ', cf. CaracteristiqueMultiple.getValeur)."""
        if valeur is None:
            return ""
        texte = valeur.strip()
        if ";" in texte:
            return tuple(sorted(e.strip() for e in texte.split(";") if e.strip()))
        return texte

    def _analyserDocument(self, nomFichier):
        chemin_doc = os.path.join(self.dossier_doc, nomFichier)
        champs = self._lireFichierDeChamps(chemin_doc)

        chemin_llm = os.path.join(self.dossier_llm, nomFichier)
        champs_llm = self._lireFichierDeChamps(chemin_llm)

        probas = [c["proba"] for c in champs.values() if c["proba"] is not None]
        champs_edites = [label for label, c in champs.items() if c["edite"]]

        champs_corriges = [
            label for label, c in champs.items()
            if label in champs_llm
            and self._normaliserValeur(c["valeur"]) != self._normaliserValeur(champs_llm[label]["valeur"])
        ]

        return {
            "mtime": os.path.getmtime(chemin_doc),
            "champs": {label: c["valeur"] for label, c in champs.items()},
            "confiances": {label: c["proba"] for label, c in champs.items() if c["proba"] is not None},
            "nb_champs": len(champs),
            "champs_edites": champs_edites,
            "champs_corriges": champs_corriges,
            "confiance_moyenne": mean(probas) if probas else None,
            "termine": os.path.exists(os.path.join(self.dossier_sortie, nomFichier)),
        }

    # -- mise a jour incrementale ---------------------------------------- #

    def actualiser(self):
        """Ne reparse que les fichiers nouveaux ou modifies depuis le dernier appel."""
        if not os.path.isdir(self.dossier_doc):
            return

        fichiers_actuels = {f for f in os.listdir(self.dossier_doc) if f.endswith(".txt")}

        # purge des entrees dont le fichier a disparu (renomme/supprime)
        for nom in list(self.documents_par_nom.keys()):
            if nom not in fichiers_actuels:
                del self.documents_par_nom[nom]

        modifie = False
        for nom in fichiers_actuels:
            chemin = os.path.join(self.dossier_doc, nom)
            mtime = os.path.getmtime(chemin)
            entree = self.documents_par_nom.get(nom)

            if entree is not None and entree.get("mtime") == mtime:
                # fichier de champs inchange : seul le statut "termine" peut
                # avoir bouge (export fait apres coup) -> pas de reparsing.
                nouveau_termine = os.path.exists(os.path.join(self.dossier_sortie, nom))
                if entree.get("termine") != nouveau_termine:
                    entree["termine"] = nouveau_termine
                    modifie = True
                continue

            self.documents_par_nom[nom] = self._analyserDocument(nom)
            modifie = True

        if modifie:
            self._sauvegarder()

    def documents(self):
        return self.documents_par_nom


# --------------------------------------------------------------------------- #
# Statistiques + graphiques
# --------------------------------------------------------------------------- #

METRIQUE_NB_DOCUMENTS = "Nombre de documents"
METRIQUE_CONFIANCE_CHAMP = "Confiance moyenne du champ (%)"
METRIQUE_CONFIANCE_GLOBALE = "Confiance moyenne globale (%)"
METRIQUE_TAUX_CORRECTION = "Taux de correction humaine (%)"
METRIQUE_TAUX_TERMINE = "Taux de fiches terminees (%)"

METRIQUES_DISPONIBLES = [
    METRIQUE_NB_DOCUMENTS,
    METRIQUE_CONFIANCE_CHAMP,
    METRIQUE_CONFIANCE_GLOBALE,
    METRIQUE_TAUX_CORRECTION,
    METRIQUE_TAUX_TERMINE,
]

# Ordre de preference pour l'axe X (les champs vraiment "statistiques" d'abord)
CHAMPS_PRIORITAIRES = [
    "Langue", "Annee", "Ville", "Editeur", "Indexation Rameau",
    "Auteur", "Collection", "Mention d'edition", "Nom de la Collectivite",
]


class Statistique:

    def __init__(self):
        self.cache = StatistiqueCache()
        self.cache.actualiser()

    def rafraichir(self):
        """A appeler quand on veut prendre en compte les documents ajoutes
        depuis l'ouverture de la fenetre de statistiques (ne reparse que le delta)."""
        self.cache.actualiser()

    # -- infos generales -------------------------------------------------- #

    def nombreDeDocuments(self):
        return len(self.cache.documents())

    def pourcentageFait(self):
        docs = self.cache.documents()
        if not docs:
            return 0
        return sum(1 for d in docs.values() if d["termine"]) / len(docs) * 100

    def ratioRealisationHumaine(self):
        docs = self.cache.documents().values()
        total = sum(d["nb_champs"] for d in docs)
        edites = sum(len(d["champs_edites"]) for d in docs)
        return edites / total if total else 0

    # -- decouverte des champs disponibles -------------------------------- #

    def champsDisponibles(self):
        """Labels de champs reellement presents dans le corpus, champs
        'statistiques' usuels en premier."""
        labels = set()
        for doc in self.cache.documents().values():
            labels.update(doc["champs"].keys())
        reste = sorted(labels - set(CHAMPS_PRIORITAIRES))
        return [c for c in CHAMPS_PRIORITAIRES if c in labels] + reste

    def metriquesDisponibles(self):
        return list(METRIQUES_DISPONIBLES)

    # -- moteur generique X / Y ------------------------------------------- #

    def _grouperParChamp(self, champ):
        groupes = {}
        for doc in self.cache.documents().values():
            valeur = doc["champs"].get(champ, "").strip()
            cle = valeur if valeur else "Non renseigne"
            groupes.setdefault(cle, []).append(doc)
        return groupes

    def _valeurMetrique(self, docs, champ, metrique):
        if not docs:
            return 0
        if metrique == METRIQUE_NB_DOCUMENTS:
            return len(docs)
        if metrique == METRIQUE_CONFIANCE_CHAMP:
            confiances = [d["confiances"][champ] for d in docs if champ in d["confiances"]]
            return mean(confiances) * 100 if confiances else 0
        if metrique == METRIQUE_CONFIANCE_GLOBALE:
            confiances = [d["confiance_moyenne"] for d in docs if d["confiance_moyenne"] is not None]
            return mean(confiances) * 100 if confiances else 0
        if metrique == METRIQUE_TAUX_CORRECTION:
            ratios = [len(d["champs_edites"]) / d["nb_champs"] for d in docs if d["nb_champs"]]
            return mean(ratios) * 100 if ratios else 0
        if metrique == METRIQUE_TAUX_TERMINE:
            return sum(1 for d in docs if d["termine"]) / len(docs) * 100
        return 0

    def donneesGraphiquePersonnalise(self, champ_x, metrique_y, top_n=25):
        """Regroupe les documents par valeur de `champ_x`, calcule `metrique_y`
        par groupe. Tri chronologique/numerique si les valeurs le permettent
        (ex. Annee), sinon par frequence decroissante, plafonne a top_n groupes."""
        groupes = self._grouperParChamp(champ_x)
        items = [
            (cle, self._valeurMetrique(docs, champ_x, metrique_y), len(docs))
            for cle, docs in groupes.items()
        ]

        def cle_tri_numerique(item):
            try:
                return (0, float(item[0]))
            except ValueError:
                return (1, -item[2])

        tout_numerique = all(cle_tri_numerique(it)[0] == 0 for it in items)

        if len(items) > top_n:
            items = sorted(items, key=lambda it: -it[2])[:top_n]

        items.sort(key=cle_tri_numerique if tout_numerique else (lambda it: -it[1]))

        labels = [str(it[0]) for it in items]
        valeurs = [it[1] for it in items]
        return labels, valeurs

    def dessinerGraphiquePersonnalise(self, champ_x, metrique_y):
        labels, valeurs = self.donneesGraphiquePersonnalise(champ_x, metrique_y)
        figure = Figure(figsize=(6, 5))
        ax = figure.add_subplot(111)
        if labels:
            ax.bar(labels, valeurs)
        ax.set_xlabel(champ_x)
        ax.set_ylabel(metrique_y)
        ax.set_title(f"{metrique_y} par {champ_x}")
        if "%" in metrique_y:
            ax.set_ylim(0, 100)
        ax.tick_params(axis="x", rotation=60)
        figure.tight_layout()
        return figure

    # -- tableau de bord par defaut ---------------------------------------- #

    def dessinerRepartitionLangues(self):
        return self.dessinerGraphiquePersonnalise("Langue", METRIQUE_NB_DOCUMENTS)

    def dessinerRepartitionAnnees(self):
        return self.dessinerGraphiquePersonnalise("Annee", METRIQUE_NB_DOCUMENTS)

    def confianceMoyenneParChamp(self):
        champs = self.champsDisponibles()
        resultat = {}
        for champ in champs:
            confiances = [
                d["confiances"][champ] for d in self.cache.documents().values()
                if champ in d["confiances"]
            ]
            resultat[champ] = mean(confiances) * 100 if confiances else 0
        return dict(sorted(resultat.items(), key=lambda kv: kv[1]))

    def dessinerConfianceMoyenneParChamp(self):
        donnees = self.confianceMoyenneParChamp()
        figure = Figure(figsize=(6, 5))
        ax = figure.add_subplot(111)
        ax.bar(list(donnees.keys()), list(donnees.values()))
        ax.set_ylim(0, 100)
        ax.set_ylabel("Confiance moyenne (%)")
        ax.set_title("Confiance moyenne du modele par champ")
        ax.tick_params(axis="x", rotation=90)
        figure.tight_layout()
        return figure

    def dessinerPourcentageFait(self):
        fait = self.pourcentageFait()
        figure = Figure(figsize=(5, 5))
        ax = figure.add_subplot(111)
        ax.pie([fait, 100 - fait], labels=["Fait", "Non fait"], autopct="%1.1f%%")
        ax.set_title(f"Realisation des fiches ({self.nombreDeDocuments()} documents)")
        figure.tight_layout()
        return figure

    def dessinerRatioHumainParCaracteristique(self):
        champs = self.champsDisponibles()
        ratios = {}
        for champ in champs:
            docs = [d for d in self.cache.documents().values() if champ in d["champs"]]
            if not docs:
                ratios[champ] = 0
                continue
            edites = sum(1 for d in docs if champ in d["champs_edites"])
            ratios[champ] = edites / len(docs) * 100
        ratios = dict(sorted(ratios.items(), key=lambda kv: kv[1]))
        figure = Figure(figsize=(6, 5))
        ax = figure.add_subplot(111)
        ax.set_ylim(0, 100)
        ax.bar(list(ratios.keys()), list(ratios.values()))
        ax.set_ylabel("Correction humaine (%)")
        ax.set_title("Taux de correction humaine par champ")
        ax.set_xlabel("Champs")
        ax.tick_params(axis="x", rotation=90)
        figure.tight_layout()
        return figure

    def dessinerNombreDeCorrectionsParFichier(self):
        valeurs = [len(d["champs_corriges"]) for d in self.cache.documents().values()]
        figure = Figure(figsize=(6, 5))
        ax = figure.add_subplot(111)
        if valeurs:
            ax.hist(valeurs, bins=range(0, max(valeurs) + 2), align="left", rwidth=0.8)
        ax.set_xlabel("Nombre de champs corriges")
        ax.set_ylabel("Nombre de fichiers")
        ax.set_title("Distribution des corrections humaines par fichier")
        figure.tight_layout()
        return figure


if __name__ == "__main__":
    stat = Statistique()
    print(f"{stat.nombreDeDocuments()} documents en cache")
    print(f"{stat.pourcentageFait():.1f}% de fiches terminees")
    print(f"{stat.ratioRealisationHumaine() * 100:.1f}% de champs corriges a la main")
    print("Langues :", stat.donneesGraphiquePersonnalise("Langue", METRIQUE_NB_DOCUMENTS))
    print("Annees  :", stat.donneesGraphiquePersonnalise("Annee", METRIQUE_NB_DOCUMENTS))