import sys
from PySide6 import QtWidgets
from PySide6 import QtGui, QtWidgets
from PySide6.QtCore import QThread, Signal, Qt
from PySide6.QtWidgets import QFileDialog
from pathlib import Path
import shutil
import os

from Parametre import getCodeConnexionAPI

base_dir = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(base_dir))
from Backend.bridge import process_single_image, process_single_image_consensus, process_image_batch, process_image_batch_consensus


class OcrWorker(QThread):
    finished_ok = Signal(list)
    failed = Signal(str)
    progress = Signal(int, int, str)  # (current, total, current_file)

    def __init__(self, mode, scan_dir, filenames, api_key):
        super().__init__()
        self.mode = mode
        self.scan_dir = scan_dir
        self.filenames = filenames or []
        self.api_key = api_key
        self._is_cancelled = False

    def cancel(self):
        """Arrête le traitement."""
        self._is_cancelled = True

    def run(self):
        try:
            stems = []
            
            if self.mode == "batch":
                # Implémentation du batch avec progression et annulation
                from pathlib import Path
                input_path = Path(self.scan_dir)
                image_extensions = {".jpg", ".jpeg", ".png", ".bmp", ".tiff"}
                
                # Récupérer les dossiers de sortie
                app_dir = Path(self.scan_dir).parent
                llm_output_dir = app_dir / "LLMOutput"
                doc_dir = app_dir / "Doc"
                
                # Filtrer les images : ignorer celles déjà traitées
                image_files = []
                for f in sorted(input_path.iterdir()):
                    if f.suffix.lower() in image_extensions:
                        # Vérifier si le fichier a déjà un résultat
                        result_llm = llm_output_dir / f"{f.stem}.txt"
                        result_doc = doc_dir / f"{f.stem}.txt"
                        if not (result_llm.exists() or result_doc.exists()):
                            image_files.append(f)
                
                total = len(image_files)
                for idx, image_file in enumerate(image_files, 1):
                    # Vérifier si annulation demandée
                    if self._is_cancelled:
                        break
                    
                    self.progress.emit(idx, total, image_file.name)
                    
                    try:
                        stem = process_single_image_consensus(
                            str(image_file),
                            self.api_key,
                            model_a="gemma-4-31b",
                            model_b="qwen-3.6-35b-instruct",
                            text_model="gpt-oss-120b",
                        )
                        stems.append(stem)
                    except Exception as exc:
                        print(f"Erreur lors du traitement de {image_file.name} : {exc}")
                        continue
            else:
                # Mode image : traitement des fichiers spécifiés
                stems = []
                total = len(self.filenames)
                for idx, filename in enumerate(self.filenames, 1):
                    # Vérifier si annulation demandée
                    if self._is_cancelled:
                        break
                    
                    self.progress.emit(idx, total, filename)
                    image_path = os.path.join(self.scan_dir, filename)
                    # Utilise le consensus avec deux modèles vision (Gemma + Qwen) + arbitrage
                    stems.append(process_single_image_consensus(
                        image_path,
                        self.api_key,
                        model_a="gemma-4-31b",
                        model_b="qwen-3.6-35b-instruct",
                        text_model="gpt-oss-120b",
                    ))
            
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
    _progress_dialog = None

    def __init__(self,w,repertoire):
        self.repertoirDesScan=repertoire
        self.window=w
        self.window.setWindowTitle("Catalogue de documents")
        self._progress_dialog = None
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
        print(api_key)
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
        self._worker.progress.connect(self._on_progress)
        
        # Calculer le nombre total d'images à traiter
        if mode == "batch":
            from pathlib import Path
            input_path = Path(self._get_scan_dir())
            app_dir = input_path.parent
            llm_output_dir = app_dir / "LLMOutput"
            doc_dir = app_dir / "Doc"
            image_extensions = {".jpg", ".jpeg", ".png", ".bmp", ".tiff"}
            
            # Compter seulement les images non traitées
            total_files = 0
            for f in input_path.iterdir():
                if f.suffix.lower() in image_extensions:
                    result_llm = llm_output_dir / f"{f.stem}.txt"
                    result_doc = doc_dir / f"{f.stem}.txt"
                    if not (result_llm.exists() or result_doc.exists()):
                        total_files += 1
        else:
            total_files = len(filenames) if filenames else 1
        
        # Créer la barre de progression
        self._progress_dialog = QtWidgets.QProgressDialog(
            "Analyse des images...", "Annuler", 0, total_files, self.window
        )
        self._progress_dialog.setWindowModality(Qt.WindowModality.WindowModal)
        self._progress_dialog.setWindowTitle("Traitement en cours")
        # Connecter le bouton "Annuler" pour arrêter le traitement
        self._progress_dialog.canceled.connect(self._on_cancel_clicked)
        self._progress_dialog.show()
        
        self._worker.start()

    def _set_processing_ui(self, active: bool):
        for name in ("AjouterUnFichier", "ChoisirUnNouveauDossierDeBase", "Reactualiser"):
            widget = getattr(self.window, name, None)
            if widget is not None:
                widget.setEnabled(not active)

    def _on_progress(self, current, total, filename):
        """Met à jour la barre de progression lors du traitement de chaque image."""
        if self._progress_dialog:
            self._progress_dialog.setMaximum(total)
            self._progress_dialog.setValue(current)
            self._progress_dialog.setLabelText(f"Traitement : {filename}\n({current}/{total})")
            # Forcer la mise à jour de l'interface
            QtWidgets.QApplication.processEvents()

    def _on_cancel_clicked(self):
        """Gère le clic sur le bouton Annuler."""
        if self._progress_dialog:
            # Changer le message et désactiver le bouton
            self._progress_dialog.setLabelText("⏹ Annulation en cours...\nAttente de la fin du fichier en cours...")
            self._progress_dialog.setCancelButton(None)  # Désactiver le bouton Annuler
        # Demander l'arrêt du worker
        if self._worker:
            self._worker.cancel()

    def _apresTraitement(self, stems):
        if self._progress_dialog:
            self._progress_dialog.close()
            self._progress_dialog = None
        self._worker = None
        self._set_processing_ui(False)
        self.ajouterFicheAuto()
        self.ajouterFicheNonFinie()
        self.creerCatalogue()
        
        if stems:
            message = f"{len(stems)} document(s) analysé(s) et ajouté(s) au catalogue.\n\n"
            message += "(Les documents déjà traités ont été ignorés.)"
            QtWidgets.QMessageBox.information(
                self.window,
                "Analyse terminée",
                message,
            )
        else:
            QtWidgets.QMessageBox.information(
                self.window,
                "Analyse terminée",
                "Aucun nouveau document à traiter.\n(Les documents déjà traités ont été ignorés.)",
            )

    def _enCasErreur(self, message):
        if self._progress_dialog:
            self._progress_dialog.close()
            self._progress_dialog = None
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