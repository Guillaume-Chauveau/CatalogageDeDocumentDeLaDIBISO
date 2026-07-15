from math import sqrt
import json
import os
from pathlib import Path

from PySide6 import QtWidgets
from PySide6 import QtGui, QtWidgets

class Parametre:
    listeParametreFixe =["Article","Titre","Auteur","Complement du titre","Numero du volume","Ville","Editeur","Annee","Illustration","Taille","Champ Scientifique","Premier Auteur","Co-Auteur","Role Auteur","Role CoAuteur","Auteur Secondaire","Role Auteur Secondaire","Nom de la Collectivite","Role de la Collectivite"]
    listeParametreHebdo =["TesteHebdo1","TesteHebdo2","TesteHebdo3","TesteHebdo4","TesteHebdo5","TesteHebdo6","TesteHebdo7","TesteHebdo8","TesteHebdo9","TesteHebdo10"]
    listeParametreClassique =["TesteClassique1","TesteClassique2","TesteClassique3","TesteClassique4","TesteClassique5","TesteClassique6","TesteClassique7","TesteClassique8","TesteClassique9","TesteClassique10"]
    listeAfficher = []
    listeDesCocher =["Article"]
    
    # Chemin du fichier caché pour stocker le CodeConnexionAPI
    @staticmethod
    def _getConfigFile():
        config_dir = Path.home() / ".app_config"
        config_dir.mkdir(exist_ok=True)
        return config_dir / "config.json"
    
    CONFIG_FILE = _getConfigFile()
    def __init__(self,w):
        self.window=w
        self.window.setWindowTitle("Liste des paramètres")
        self.chargerCodeConnexionAPI()

    def chargerCodeConnexionAPI(self):
        """Charge le CodeConnexionAPI depuis le fichier caché"""
        try:
            if self.CONFIG_FILE.exists():
                with open(self.CONFIG_FILE, 'r') as f:
                    config = json.load(f)
                    code = config.get("CodeConnexionAPI", "")
                    self.window.CodeConnexionAPI.setText(code)
        except Exception as e:
            print(f"Erreur lors du chargement du CodeConnexionAPI: {e}")

    def sauvegarderCodeConnexionAPI(self):
        """Sauvegarde le CodeConnexionAPI dans un fichier caché"""
        try:
            code = self.window.CodeConnexionAPI.text()
            config = {}
            
            # S'assurer que le répertoire parent existe
            self.CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)
            
            # Charger la config existante si elle existe
            if self.CONFIG_FILE.exists():
                try:
                    with open(self.CONFIG_FILE, 'r') as f:
                        config = json.load(f)
                except Exception as load_error:
                    print(f"Avertissement: impossible de charger la config existante: {load_error}")
                    config = {}
            
            # Mettre à jour avec la nouvelle valeur
            config["CodeConnexionAPI"] = code
            
            # Sauvegarder
            with open(self.CONFIG_FILE, 'w') as f:
                json.dump(config, f, indent=2)
            
            # Rendre le fichier caché sur Windows
            if os.name == 'nt':  # Windows
                try:
                    os.system(f'attrib +h "{self.CONFIG_FILE}"')
                except Exception as attr_error:
                    print(f"Avertissement: impossible de rendre le fichier caché: {attr_error}")
            
            print(f"CodeConnexionAPI sauvegardé avec succès dans {self.CONFIG_FILE}")
            
        except Exception as e:
            print(f"Erreur lors de la sauvegarde du CodeConnexionAPI: {e}")
    
    def getCodeConnexionAPI(self):
        """Retourne le CodeConnexionAPI"""
        return self.window.CodeConnexionAPI.text()

    def remiseAZero(self):
        for i in range(self.window.ListeParametre.count() - 1, -1, -1):
            item = self.window.ListeParametre.itemAt(i).widget()
            if isinstance(item, QtWidgets.QCheckBox):
                item.hide()

    def clearAll(self):
        self.remiseAZero()
        self.window.ParametreCommun.setChecked(False)
        self.window.ParametreHebdomadaire.setChecked(False)
        self.window.ParametreClassique.setChecked(False)

    def afficherLaListe(self):
        self.remiseAZero()
        nbColonne = self.calculeTaille()
        id=0
        for i in self.listeAfficher:
            item = QtWidgets.QCheckBox(i)
            item.clicked.connect(lambda: self.clickValeur())
            if i in self.listeDesCocher:
                item.setChecked(True)
            else:
                item.setChecked(False)
            self.window.ListeParametre.addWidget(item,id//nbColonne,id%nbColonne)
            id+=1
           
    def ajouterParametreFixe(self):
        for i in self.listeParametreFixe:
            if i not in self.listeAfficher:
                self.listeAfficher.append(i)
        self.afficherLaListe()

    def ajouterParametreHebdo(self):
        for i in self.listeParametreHebdo:
            if i not in self.listeAfficher:
                self.listeAfficher.append(i)
        self.afficherLaListe()

    def ajouterParametreClassique(self):
        for i in self.listeParametreClassique:
            if i not in self.listeAfficher:
                self.listeAfficher.append(i)
        self.afficherLaListe()

    def supprimerParametreFixe(self):
        for i in self.listeParametreFixe:
            if i in self.listeAfficher:
                self.listeAfficher.remove(i)
        self.afficherLaListe()

    def supprimerParametreHebdo(self):
        for i in self.listeParametreHebdo:
            if i in self.listeAfficher:
                self.listeAfficher.remove(i)
        self.afficherLaListe()

    def supprimerParametreClassique(self):
        for i in self.listeParametreClassique:
            if i in self.listeAfficher:
                self.listeAfficher.remove(i)
        self.afficherLaListe()
    
    def calculeTaille(self):
        return round(sqrt(len(self.listeAfficher)))

    def clickClassique(self):
        if self.window.ParametreClassique.isChecked():
            self.ajouterParametreClassique()
        else:
            self.supprimerParametreClassique()
    
    def clickHebdo(self):
        if self.window.ParametreHebdomadaire.isChecked():
            self.ajouterParametreHebdo()
        else:
            self.supprimerParametreHebdo()
    
    def clickFixe(self):
        if self.window.ParametreCommun.isChecked():
            self.ajouterParametreFixe()
        else:
            self.supprimerParametreFixe()

    def clickVraiTout(self):
        if self.window.ToutVrai.isChecked():
            self.window.ToutFaux.setChecked(False)
            i=0
            while (self.window.ListeParametre.itemAt(i)):
                item = self.window.ListeParametre.itemAt(i).widget()
                if isinstance(item, QtWidgets.QCheckBox):
                    item.setChecked(True)
                i+=1
            self.listeDesCocher+=self.listeAfficher
            print(self.listeDesCocher)
                
                
    def clickFauxTout(self):
        if self.window.ToutFaux.isChecked():
            self.window.ToutVrai.setChecked(False)
            i=0
            while (self.window.ListeParametre.itemAt(i)):
                item = self.window.ListeParametre.itemAt(i).widget()
                if isinstance(item, QtWidgets.QCheckBox):
                    item.setChecked(False)
                i+=1
            self.listeDesCocher=[]

    def clickValeur(self):
        self.listeDesCocher = []
        i=0
        while (self.window.ListeParametre.itemAt(i)):
            item = self.window.ListeParametre.itemAt(i).widget()
            if isinstance(item, QtWidgets.QCheckBox):
                if item.isChecked() and not(item.text in self.listeDesCocher):
                    self.listeDesCocher.append(item.text())
            i+=1
        if (self.listeDesCocher==self.listeAfficher):
            self.window.ToutVrai.setChecked(True)
            self.window.ToutFaux.setChecked(False)
        elif(self.listeDesCocher==[]):
            self.window.ToutFaux.setChecked(True)
            self.window.ToutVrai.setChecked(False)
        else:
            self.window.ToutVrai.setChecked(False)
            self.window.ToutFaux.setChecked(False)
        print(self.listeDesCocher)

    def retour(self):
        self.sauvegarderCodeConnexionAPI()
        print(self.getCodeConnexionAPI())
        print(self.listeDesCocher)
        
def getCodeConnexionAPI():
    """Retourne le CodeConnexionAPI depuis le fichier caché"""
    config_file = Parametre._getConfigFile()
    try:
        if config_file.exists():
            with open(config_file, 'r') as f:
                config = json.load(f)
                return config.get("CodeConnexionAPI", "")
    except Exception as e:
        print(f"Erreur lors de la lecture du CodeConnexionAPI: {e}")
    return ""