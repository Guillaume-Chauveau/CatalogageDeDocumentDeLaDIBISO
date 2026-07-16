import sys
from PySide6 import QtWidgets
from PySide6 import QtGui, QtWidgets
from PySide6.QtCore import QThread, Signal
from PySide6.QtWidgets import QFileDialog
from pathlib import Path
import shutil
import os

from Parametre import getCodeConnexionAPI

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "Backend"))
from document_processor import process_single_image, process_image_batch


class OcrWorker(QThread):
    finished_ok = Signal(list)
    failed = Signal(str)

    def __init__(self, mode, scan_dir, filenames, api_key):
        super().__init__()
        self.mode = mode
        self.scan_dir = scan_dir
        self.filenames = filenames or []
        self.api_key = api_key

    def run(self):
        try:
            if self.mode == "batch":
                stems = process_image_batch(self.scan_dir, self.api_key)
            else:
                stems = []
                for filename in self.filenames:
                    image_path = os.path.join(self.scan_dir, filename)
                    stems.append(process_single_image(image_path, self.api_key))
            self.finished_ok.emit(stems)
        except Exception as exc:
            self.failed.emit(str(exc))

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

if hasattr(sys, '_MEIPASS'):
    BASE_DIR = sys._MEIPASS

class ListeAFinir:
    Fiches = []
    FichesNonFinies =[]
    window=None
    repertoirDesScan =""
    _worker = None

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
    
    def _get_scan_dir(self):
        if os.path.isabs(self.repertoirDesScan):
            return self.repertoirDesScan
        return os.path.join(os.path.dirname(__file__), self.repertoirDesScan)

    def openFileDialog(self):
        dialog = QFileDialog(self.window)
        dialog.setDirectory(str(Path.home()))
        dialog.setFileMode(QFileDialog.FileMode.ExistingFiles)
        dialog.setNameFilter("Images (*.png *.jpg *.jpeg)")
        dialog.setViewMode(QFileDialog.ViewMode.List)
        if dialog.exec():
            filenames = dialog.selectedFiles()
            if filenames:
                copied = []
                scan_dir = self._get_scan_dir()
                os.makedirs(scan_dir, exist_ok=True)
                for origin in filenames:
                    filename = os.path.basename(origin)
                    destination = os.path.join(scan_dir, str(filename))
                    shutil.copy(origin, destination)
                    copied.append(str(filename))
                self._lancerTraitement(mode="image", filenames=copied)

    def _lancerTraitement(self, mode="image", filenames=None):
        api_key = getCodeConnexionAPI()
        if not api_key.strip():
            QtWidgets.QMessageBox.warning(
                self.window,
                "Clé API manquante",
                "Configurez votre clé API dans Paramètres avant d'analyser des documents.",
            )
            return

        if self._worker is not None and self._worker.isRunning():
            QtWidgets.QMessageBox.information(
                self.window,
                "Analyse en cours",
                "Un traitement est déjà en cours. Veuillez patienter.",
            )
            return

        self._set_processing_ui(True)
        self._worker = OcrWorker(mode, self._get_scan_dir(), filenames, api_key)
        self._worker.finished_ok.connect(self._apresTraitement)
        self._worker.failed.connect(self._enCasErreur)
        self._worker.start()

    def _set_processing_ui(self, active: bool):
        for name in ("AjouterUnFichier", "ChoisirUnNouveauDossierDeBase", "Reactualiser"):
            widget = getattr(self.window, name, None)
            if widget is not None:
                widget.setEnabled(not active)

    def _apresTraitement(self, stems):
        self._worker = None
        self._set_processing_ui(False)
        self.ajouterFicheAuto()
        self.ajouterFicheNonFinie()
        self.creerCatalogue()
        if stems:
            QtWidgets.QMessageBox.information(
                self.window,
                "Analyse terminée",
                f"{len(stems)} document(s) analysé(s) et ajouté(s) au catalogue.",
            )

    def _enCasErreur(self, message):
        self._worker = None
        self._set_processing_ui(False)
        QtWidgets.QMessageBox.critical(self.window, "Erreur d'analyse", message)
    
    def changerDeRepertoireDeScan(self,repertoire):
        self.repertoirDesScan=repertoire
    
    def choisirRepertoireDeScan(self, callback=None):
        dialog = QFileDialog(self.window)
        dialog.setDirectory(str(Path.home()))
        dialog.setFileMode(QFileDialog.FileMode.Directory)
        dialog.setViewMode(QFileDialog.ViewMode.List)
        if dialog.exec():
            directories = dialog.selectedFiles()
            if directories:
                self.changerDeRepertoireDeScan(directories[0])
                self.setAfficheDossier(directories[0])
                if callback is not None:
                    callback(self.repertoirDesScan)
                self._lancerTraitement(mode="batch")
                return
        self.creerCatalogue()
    
    def setAfficheDossier(self,valeur):
        self.window.AfficheDossier.setText(valeur)

    def _testImageExiste(self,filename):
        scan_dir = self._get_scan_dir()
        for extension in [".png", ".jpg", ".jpeg"]:
            if os.path.exists(os.path.join(scan_dir, os.path.splitext(filename)[0] + extension)):
                return True
        return False