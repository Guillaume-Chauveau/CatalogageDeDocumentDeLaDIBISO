from math import sqrt
import json
import os
from pathlib import Path

from PySide6 import QtWidgets
from PySide6 import QtGui, QtWidgets

class Parametre:
    listeParametreFixe =["Article","Titre","Auteur","Complement du titre","Numero du volume","Ville","Editeur","Annee","Illustration","Dimension","Indexation Rameau","Premier Auteur","Co-Auteur","Role Auteur","Role CoAuteur","Auteur Secondaire","Role Auteur Secondaire","Nom de la Collectivite","Role de la Collectivite"]
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
        self.ajouterParametreFixe()
        self.afficherLaListe()
        self.chargerCodeConnexionAPI()

    def chargerCodeConnexionAPI(self):
        with open(".clef.txt", "r",encoding="utf-8") as f:
            self.window.CodeConnexionAPI.setText(f.read().strip())

    def sauvegarderCodeConnexionAPI(self):
        with open(".clef.txt", "w",encoding="utf-8") as f:
            f.write(self.window.CodeConnexionAPI.text())
    
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
        nbColonne = self.calculeDimension()
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

    def supprimerParametreClassique(self):
        for i in self.listeParametreClassique:
            if i in self.listeAfficher:
                self.listeAfficher.remove(i)
        self.afficherLaListe()
    
    def calculeDimension(self):
        return round(sqrt(len(self.listeAfficher)))

    def clickClassique(self):
        if self.window.ParametreClassique.isChecked():
            self.ajouterParametreClassique()
        else:
            self.supprimerParametreClassique()
    
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
    with open(".clef.txt", "r") as f:
        return f.read().strip()