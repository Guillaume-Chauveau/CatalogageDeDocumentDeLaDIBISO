import sys
from PySide6 import QtWidgets
from PySide6 import QtGui, QtWidgets
from PySide6.QtWidgets import QFileDialog
from pathlib import Path
import shutil
import os
class ListeAFinir:
    Fiches = []
    FichesNonFinies =[]
    window=None

    def __init__(self,w):
        self.window=w
        self.window.setWindowTitle("Catalogue de documents")
        self.ajouterFiche()
        self.ajouterFicheNonFinie()
        self.creerCatalogueNonFini()
        

    def creerCatalogueNonFini(self):
        list=self.window.listWidget
        list.clear()
        for i in self.FichesNonFinies:
            item = QtWidgets.QListWidgetItem(self.retirerLextension(i))
            list.addItem(item)

    def creerCatalogueComplet(self):
        list=self.window.listWidget
        list.clear()
        for i in self.Fiches:
            item = QtWidgets.QListWidgetItem(self.retirerLextension(i))
            list.addItem(item)
    
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
    
    def ajouterFiche(self):
        self.Fiches=os.listdir("./Doc")

    def getFichesNonFinies(self):
        return self.FichesNonFinies

    def ajouterFicheNonFinie(self):
        FichesFini= os.listdir("./Sorti")
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
                    destination=os.path.join(os.path.dirname(__file__), "Scan", str(filename))
                    shutil.copy(origin, destination)

                    
                    ##Todo: appelé le LLM ici
                    #créer le doc vide (solution tmp avant de faire appele au llm)
                    chemain=os.path.join(os.path.dirname(__file__), "LLMOutput", str(filename))
                    chemain=chemain.replace(".png",".txt").replace(".jpg",".txt")
                    with open(chemain,"w") as c:
                        ##remplir le doc ici
                        pass
                    chemain=os.path.join(os.path.dirname(__file__), "Doc", str(filename))
                    chemain=chemain.replace(".png",".txt").replace(".jpg",".txt")
                    with open(chemain,"w") as c:
                        ##remplir le doc ici
                        pass