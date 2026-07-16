import sys
import os
from PySide6 import QtCore, QtGui, QtWidgets
from PySide6.QtUiTools import QUiLoader
import ListeAFinir as Catalogue
import Fiche as f
import FormulaireAuteur as fa
import FormulaireChampsScientifique as FCs
import FormulaireCollection as fc
import Parametre as p
import Statistique as s
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas

BASE_DIR = os.path.dirname(__file__)
loader = QUiLoader()


class WindowManager:
    """Centralise l'affichage et la fermeture des fenêtres principales."""
    def __init__(self):
        self._windows = {}

    def register(self, name, obj):
        self._windows[name] = obj
        return obj

    def get(self, name, default=None):
        return self._windows.get(name, default)

    def close(self, name):
        obj = self._windows.pop(name, None)
        if obj is None:
            return None

        target = getattr(obj, "window", obj)
        if hasattr(target, "close"):
            try:
                target.close()
            except Exception:
                pass
        return obj

    def show(self, name, obj):
        if obj is None:
            return None

        self.close(name)
        self._windows[name] = obj

        target = getattr(obj, "window", obj)
        if hasattr(target, "setAttribute"):
            target.setAttribute(QtCore.Qt.WA_DeleteOnClose, False)
        if hasattr(target, "show"):
            target.show()

        return obj


window_manager = WindowManager()

currentCatalogue = None
currentFiche = None
currentParametre = None
currentStatistiques = None
currentRenduFormulaire = None
chemainScan = "Scan"  # Répertoire par défaut pour les scans

def mettreAJourChemainScan(repertoire):
    global chemainScan
    chemainScan = repertoire

def afficherUnFormulaire(w, page):
    global currentFiche, chemainScan
    if currentCatalogue is not None:
        chemainScan = currentCatalogue.repertoirDesScan

    formulairePath = os.path.join(BASE_DIR, "UI", "Formulaire.ui")
    formulaire = loader.load(formulairePath, None)
    currentFiche = f.Fiche(page, formulaire, afficherLeFormulaireAuteur, afficherLeFormulaireChampsScientifique,afficherLeFormulaireCollection, chemainScan)
    activerRedimensionnementDynamique(currentFiche)
    ajouterBoutonFormulaire(currentFiche)

    if w is not None:
        w.close()

    window_manager.show("fiche", currentFiche)
    print(currentFiche)

def afficherLesParametres():
    global currentParametre
    parametrePath = os.path.join(BASE_DIR, "UI", "Parametre.ui")
    parametre = loader.load(parametrePath, None)

    currentParametre = p.Parametre(parametre)
    currentParametre.window.ParametreCommun.clicked.connect(lambda: currentParametre.clickFixe())
    currentParametre.window.ParametreHebdomadaire.clicked.connect(lambda: currentParametre.clickHebdo())
    currentParametre.window.ParametreClassique.clicked.connect(lambda: currentParametre.clickClassique())
    currentParametre.window.ToutVrai.clicked.connect(lambda: currentParametre.clickVraiTout())
    currentParametre.window.ToutFaux.clicked.connect(lambda: currentParametre.clickFauxTout())
    currentParametre.window.Valider.clicked.connect(lambda: currentParametre.retour())
    currentParametre.window.Valider.clicked.connect(lambda: currentParametre.window.close())
    currentParametre.window.Annuler.clicked.connect(lambda: currentParametre.window.close())

    activerRedimensionnementDynamique(currentParametre)
    window_manager.show("parametre", currentParametre)

def activerRedimensionnementDynamique(w):
    # Accept either an object with a `.window` attribute (wrapper) or the window/widget itself
    win = getattr(w, 'window', w)

    # Cas 1: QMainWindow avec centralwidget
    if hasattr(win, "centralwidget") and win.centralwidget is not None:
        central = win.centralwidget
        central.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        
        layout = central.layout()
        if layout is None:
            layout = QtWidgets.QVBoxLayout(central)
            layout.setContentsMargins(0, 0, 0, 0)
            layout.setSpacing(0)
            central.setLayout(layout)
        
        # Configurer la frame
        if hasattr(win, "frame"):
            frame = win.frame
            frame.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
            
            # Vérifier que la frame est bien dans le layout
            if layout.indexOf(frame) < 0:
                layout.addWidget(frame)
            
            _configurer_enfants_layout(frame)
    
    # Cas 2: QDialog / QWidget contenant une `frame`
    elif hasattr(win, "frame"):
        layout = win.layout()
        if layout is None:
            layout = QtWidgets.QVBoxLayout(win)
            layout.setContentsMargins(0, 0, 0, 0)
            layout.setSpacing(0)
            win.setLayout(layout)
        
        frame = win.frame
        frame.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        
        # Vérifier que la frame est bien dans le layout
        if layout.indexOf(frame) < 0:
            layout.addWidget(frame)
        
        _configurer_enfants_layout(frame)

def _configurer_enfants_layout(widget):
    """Configurer les enfants d'un widget pour qu'ils s'étendent correctement."""
    if not hasattr(widget, "layout") or widget.layout() is None:
        return

    layout = widget.layout()

    if isinstance(layout, QtWidgets.QFormLayout):
        layout.setFieldGrowthPolicy(QtWidgets.QFormLayout.ExpandingFieldsGrow)

    for i in range(layout.count()):
        item = layout.itemAt(i)
        if item and item.widget():
            child = item.widget()

            if isinstance(child, QtWidgets.QLabel):
                child.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
                child.setWordWrap(True)
            elif isinstance(child, (QtWidgets.QFrame, QtWidgets.QWidget)):
                child.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)

            if i == 0 and isinstance(child, QtWidgets.QLabel) and hasattr(layout, "setStretch"):
                layout.setStretch(i, 1)

def ajouterBoutonFormulaire(w):
    def _on_validation():
        try:
            w.affichage()
        except Exception as exc:
            print(f"[Validation] Erreur dans affichage(): {exc}")

        try:
            w.ecriture()
        except Exception as exc:
            print(f"[Validation] Erreur dans ecriture(): {exc}")

        try:
            afficherRenduFormulaire(w)
        except Exception as exc:
            print(f"[Validation] Erreur dans afficherRenduFormulaire(): {exc}")

    w.window.Validation.clicked.connect(_on_validation)
    w.window.Validation.setToolTip("Exporte cette fiche au format Unimarc")

    w.window.Quiter.clicked.connect(lambda: afficherLeCatalogue(w.window, w.chemainScan))
    w.window.Quiter.setToolTip("Quite la page et retourne au menu de sélection du fichier")
    w.window.Restart.clicked.connect(lambda: w.lecture(w.chemain))
    w.window.Restart.clicked.connect(lambda: w.calculeDeLaBareCentrale())
    w.window.Restart.setToolTip("Charge la dernière sauvegarde")
    w.window.zoomInButton.clicked.connect(lambda: w.zoom(1.2))
    w.window.zoomOutButton.clicked.connect(lambda: w.zoom(0.8))
    w.window.zoomZero.clicked.connect(lambda: w.resetZoom())
    w.window.Sauvgarde.clicked.connect(lambda: w.sauvgarde())
    w.window.Sauvgarde.setToolTip("Effectu une sauvagede de l'état actuelle de la fiche")
    w.window.Reset.clicked.connect(lambda: w.lecture(w.chemainOrigine))
    w.window.Reset.clicked.connect(lambda: w.calculeDeLaBareCentrale())
    w.window.Reset.setToolTip("Charge les valeur initialle de cette fiche")
    w.window.BoutonTitre.clicked.connect(lambda: w.copieFileName())

    for i in range(0, w.window.gridLayout.rowCount()):
        if w.window.gridLayout.itemAtPosition(i, 2) is not None:
            field = w.window.gridLayout.itemAtPosition(i, 2).widget()
            if isinstance(field, QtWidgets.QLineEdit):
                field.textChanged.connect(lambda: w.changeEdit(w.actualiserValeur()))

def afficherRenduFormulaire(fiche=None):
    global currentRenduFormulaire

    parametrePath = os.path.join(BASE_DIR, "UI", "RenduFormulaire.ui")
    parametre = loader.load(parametrePath, None)

    if parametre is None:
        print("Erreur: impossible de charger RenduFormulaire.ui")
        return

    if hasattr(parametre, "setWindowTitle"):
        parametre.setWindowTitle("Rendu du formulaire")
    if hasattr(parametre, "resize"):
        parametre.resize(800, 600)
    if hasattr(parametre, "setAttribute"):
        parametre.setAttribute(QtCore.Qt.WA_DeleteOnClose, False)

    def _get_response_text():
        try:
            return parametre.Reponce.toPlainText()
        except Exception:
            try:
                return parametre.Reponce.text()
            except Exception:
                return ""

    try:
        rendu_text = fiche.affichage() if fiche is not None and hasattr(fiche, "affichage") else ""
    except Exception as exc:
        print(f"[Rendu] Erreur dans fiche.affichage(): {exc}")
        rendu_text = ""

    try:
        parametre.Reponce.setText(rendu_text)
    except Exception:
        try:
            parametre.Reponce.setPlainText(rendu_text)
        except Exception as exc:
            print(f"[Rendu] Impossible d'écrire dans Reponce: {exc}")

    parametre.BoutonCopier.clicked.connect(
        lambda: QtWidgets.QApplication.clipboard().setText(_get_response_text())
    )

    if fiche is not None:
        page = getattr(fiche, "nomDuFichier", None)
        if page is None:
            page = getattr(fiche, "page", None)

        parametre.BoutonFormulaire.clicked.connect(
            lambda: afficherUnFormulaire(getattr(fiche, "window", None), page)
        )
        parametre.BoutonHome.clicked.connect(
            lambda: afficherLeCatalogue(getattr(fiche, "window", None), getattr(fiche, "chemainScan", "Scan"))
        )
    else:
        parametre.BoutonFormulaire.clicked.connect(lambda: None)
        parametre.BoutonHome.clicked.connect(lambda: None)

    try:
        if fiche is not None and hasattr(fiche, "window") and fiche.window is not None:
            fiche.window.close()
    except Exception as exc:
        print(f"[Rendu] Erreur lors de la fermeture de la fiche: {exc}")

    currentRenduFormulaire = parametre

    # On ferme d'abord une éventuelle ancienne fenêtre de rendu
    window_manager.close("rendu")

    # On l'affiche explicitement
    window_manager.show("rendu", parametre)
    parametre.show()
    parametre.raise_()
    parametre.activateWindow()
    QtWidgets.QApplication.processEvents()

def afficherLeCatalogue(w=None, repertoire="Scan"):
    global currentCatalogue, chemainScan
    if currentCatalogue is not None and getattr(currentCatalogue, "repertoirDesScan", ""):
        repertoire = currentCatalogue.repertoirDesScan

    mettreAJourChemainScan(repertoire)
    print(f"Répertoire de scan utilisé pour le catalogue: {repertoire}")

    if w is not None:
        w.close()

    cataloguePath = os.path.join(BASE_DIR, "UI", "changementDePage.ui")
    catalogue = loader.load(cataloguePath, None)

    currentCatalogue = Catalogue.ListeAFinir(catalogue, repertoire)
    currentCatalogue.window.Reactualiser.clicked.connect(lambda: afficherLeCatalogue(currentCatalogue.window, repertoire))
    currentCatalogue.window.listWidget.currentItemChanged.connect(lambda: afficherUnFormulaire(currentCatalogue.window, currentCatalogue.window.listWidget.currentItem().text()))
    currentCatalogue.window.VoirFini.checkStateChanged.connect(lambda: currentCatalogue.creerCatalogue())
    currentCatalogue.window.Parametre.clicked.connect(lambda: afficherLesParametres())
    currentCatalogue.window.AjouterUnFichier.clicked.connect(lambda: currentCatalogue.openFileDialog())
    currentCatalogue.window.Statistique.clicked.connect(lambda: afficherLesStatistiques())
    currentCatalogue.window.ChoisirUnNouveauDossierDeBase.clicked.connect(lambda: currentCatalogue.choisirRepertoireDeScan(mettreAJourChemainScan))

    activerRedimensionnementDynamique(currentCatalogue)
    window_manager.show("catalogue", currentCatalogue)

def afficherLeFormulaireCollection(fiche=None):
    formulaireCollectionPath = os.path.join(BASE_DIR, "UI", "FormulaireCollection.ui")
    formulaireCollection = loader.load(formulaireCollectionPath, None)
    formulaireCollectionWindow = fc.FormulaireCollection(formulaireCollection, fiche)

    formulaireCollectionWindow.remplirFormulaire()
    activerRedimensionnementDynamique(formulaireCollectionWindow)
    window_manager.show("formulaire_collection", formulaireCollectionWindow)

def afficherLeFormulaireAuteur(fiche=None):
    formulaireAuteurPath = os.path.join(BASE_DIR, "UI", "FormulaireAuteur.ui")
    formulaireAuteur = loader.load(formulaireAuteurPath, None)
    formulaireAuteurWindow = fa.FormulaireAuteur(formulaireAuteur,fiche)

    activerRedimensionnementDynamique(formulaireAuteurWindow)
    window_manager.show("formulaire_auteur", formulaireAuteurWindow)

def afficherLeFormulaireChampsScientifique(fiche=None):
    formulaireChampsScientifiquePath = os.path.join(BASE_DIR, "UI", "FormulaireChampsScientifique.ui")
    formulaireChampsScientifique = loader.load(formulaireChampsScientifiquePath, None)
    formulaireChampsScientifiqueWindow = FCs.FormulaireChampsScientifique(formulaireChampsScientifique,fiche)

    activerRedimensionnementDynamique(formulaireChampsScientifiqueWindow)
    window_manager.show("formulaire_champs", formulaireChampsScientifiqueWindow)

def afficherLesStatistiques():
    global currentStatistiques
    statistiquesPath = os.path.join(BASE_DIR, "UI", "Statistiques.ui")
    statistiques = loader.load(statistiquesPath, None)

    statistiques.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)

    statistiques.Retour.clicked.connect(lambda: statistiques.close())
    statistiques.Retour.clicked.connect(lambda: afficherLeCatalogue(currentCatalogue.window, currentCatalogue.repertoirDesScan))

    centralWidget = QtWidgets.QWidget()
    gridL = QtWidgets.QGridLayout()
    centralWidget.setLayout(gridL)
    statistiques.setCentralWidget(centralWidget)
    gridL.setContentsMargins(5, 5, 64, 64)
    gridL.setSpacing(10)
    gridL.setColumnStretch(0, 1)
    gridL.setColumnStretch(1, 1)
    gridL.setRowStretch(0, 1)
    gridL.setRowStretch(1, 1)

    def _ajouterCanvas(figure):
        canvas = FigureCanvas(figure)
        canvas.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        canvas.setMinimumSize(300, 280)
        return canvas

    canvasRatioRéalisationHumaine = _ajouterCanvas(s.Statistique().desinnerRatioHumain())
    canvasPourcentageFait = _ajouterCanvas(s.Statistique().desinnerPourcentageFait())
    canvasNombreErreursParCatacteristique = _ajouterCanvas(s.Statistique().dessinerNombreDErreurParCaracteristique())
    canvasNombreErreursParFichier = _ajouterCanvas(s.Statistique().dessinerNombreDeCaracteristiqueCorrigeParFichier())

    gridL.addWidget(canvasRatioRéalisationHumaine, 0, 0, 1, 1)
    gridL.addWidget(canvasPourcentageFait, 0, 1, 1, 1)
    gridL.addWidget(canvasNombreErreursParCatacteristique, 1, 0, 1, 1)
    gridL.addWidget(canvasNombreErreursParFichier, 1, 1, 1, 1)

    for canvas in (canvasRatioRéalisationHumaine, canvasPourcentageFait, canvasNombreErreursParCatacteristique, canvasNombreErreursParFichier):
        canvas.draw()

    statistiques.resize(1500, 950)
    currentStatistiques = statistiques
    window_manager.show("statistiques", statistiques)

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    afficherLeCatalogue()
    app.exec()