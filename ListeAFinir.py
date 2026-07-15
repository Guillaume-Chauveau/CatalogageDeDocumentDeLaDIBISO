import sys
from PySide6 import QtWidgets
from PySide6 import QtGui, QtWidgets
from PySide6.QtWidgets import QFileDialog
from pathlib import Path
import shutil
import os

from Parametre import getCodeConnexionAPI

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

if hasattr(sys, '_MEIPASS'):
    BASE_DIR = sys._MEIPASS

class ListeAFinir:
    Fiches = []
    FichesNonFinies =[]
    window=None
    repertoirDesScan =""

    def __init__(self,w,repertoire):
        self.repertoirDesScan=repertoire
        self.window=w
        self.window.setWindowTitle("Catalogue de documents")
        self.ajouterFicheAuto()
        self.ajouterFicheNonFinie()
        self.creerCatalogueNonFini()
        self.setAfficheDossier(repertoire)
        

    def creerCatalogueNonFini(self):
        list=self.window.listWidget
        list.clear()
        for i in self.FichesNonFinies:
            self._ajouterItemAuCatalogue(list, i)

    def creerCatalogueComplet(self):
        list=self.window.listWidget
        list.clear()
        for i in self.Fiches:
            self._ajouterItemAuCatalogue(list, i)

    def _ajouterItemAuCatalogue(self, list_widget, nomFichier):
        item = QtWidgets.QListWidgetItem(self.retirerLextension(nomFichier))
        self._gestionIcon(nomFichier, item)
        list_widget.addItem(item)

    ## fonctions sur les icones
    def _gestionIcon(self, nomFichier, item):
        if not self._testImageExiste(nomFichier):
            self._ajoutIcon(item)
        else:
            self._retirerIcon(item)

    def _ajoutIcon(self, item):
        icon = self.window.style().standardIcon(
                QtWidgets.QStyle.StandardPixmap.SP_MessageBoxWarning
            )
        item.setIcon(icon)
        item.setToolTip("Aucune image associée")

    def _retirerIcon(self, item):
        item.setIcon(QtGui.QIcon())
        item.setToolTip("")
    ##fin des fonctions sur les icones    
    
    def retirerLextension(self,nomFichier):
        return os.path.splitext(nomFichier)[0]
    
    def creerCatalogue(self):
        if self.window.VoirFini.isChecked():
            self.creerCatalogueComplet()
        else:
            self.creerCatalogueNonFini()
    
    def getFiches(self):
        return self.Fiches
    
    def setFiches(self,fiches):
        self.Fiches = fiches

    def addFiche(self,fiche):
        self.Fiches.append(fiche)
    
    def ajouterFicheAuto(self):
        self.Fiches=os.listdir(os.path.join(BASE_DIR, "Doc"))

    def getFichesNonFinies(self):
        return self.FichesNonFinies

    def ajouterFicheNonFinie(self):
        FichesFini= os.listdir(os.path.join(BASE_DIR, "Sortie"))
        self.FichesNonFinies.clear()
        for i in self.Fiches:
            if i not in FichesFini:
                self.FichesNonFinies.append(i)
    
    def openFileDialog(self):
        dialog = QFileDialog(self.window)
        dialog.setDirectory(str(Path.home()))
        dialog.setFileMode(QFileDialog.FileMode.ExistingFiles)
        dialog.setNameFilter("Images (*.png *.jpg)")
        dialog.setViewMode(QFileDialog.ViewMode.List)
        if dialog.exec():
            filenames = dialog.selectedFiles()
            if filenames:
                for origin in filenames:
                    filename = os.path.basename(origin)

                    #fait une copie dans Scan
                    destination=os.path.join(os.path.dirname(__file__), self.repertoirDesScan, str(filename))
                    shutil.copy(origin, destination)
                    self._ajouterUnFichier(str(filename))
                    
    def _ajouterUnFichier(self,filename):
        ##Todo: appelé le LLM ici
        #créer le doc vide (solution tmp avant de faire appele au llm)
        self._ajouterUnFichierDansUnDossier(filename,"LLMOutput")
        self._ajouterUnFichierDansUnDossier(filename,"Doc")

    def _ajouterUnFichierDansUnDossier(self, filename,lieu):
        chemain=os.path.join(os.path.dirname(__file__), lieu, str(filename))
        chemain=chemain.replace(".png",".txt").replace(".jpg",".txt")
        with open(chemain,"w") as c:
            ##remplir le doc ici
            pass
    
    def changerDeRepertoireDeScan(self,repertoire):
        self.repertoirDesScan=repertoire
    
    def choisirRepertoireDeScan(self, callback=None):
        dialog = QFileDialog(self.window)
        dialog.setDirectory(str(Path.home()))
        dialog.setFileMode(QFileDialog.FileMode.Directory)
        dialog.setViewMode(QFileDialog.ViewMode.List)
        print(getCodeConnexionAPI())
        if dialog.exec():
            directories = dialog.selectedFiles()
            if directories:
                self.changerDeRepertoireDeScan(directories[0])
                self.setAfficheDossier(directories[0])
                self._lectureDeToutLesScanDansLeRepertoireCoutrant()
                
                if callback is not None:
                    callback(self.repertoirDesScan)
        self.creerCatalogue()

    def _lectureDeToutLesScanDansLeRepertoireCoutrant(self):
        for filename in os.listdir(os.path.join(BASE_DIR, self.repertoirDesScan)):
            if filename.endswith(".png") or filename.endswith(".jpg"):
                if filename not in self.Fiches:
                    self._ajouterUnFichier(filename)
    
    def setAfficheDossier(self,valeur):
        self.window.AfficheDossier.setText(valeur)

    def _testImageExiste(self,filename):
        for extension in [".png", ".jpg", ".jpeg"]:
            if os.path.exists(os.path.join(self.repertoirDesScan, os.path.splitext(filename)[0] + extension)):
                return True
        return False