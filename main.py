import sys
from PySide6 import QtWidgets
from PySide6.QtUiTools import QUiLoader
from PySide6 import QtGui, QtWidgets
from PySide6 import QtCore
import os
import ListeAFinir as Catalogue
import Fiche as f
import FormulaireAuteur as fa
import FormulaireChampsScientifique as FC
import Parametre as p
import Statistique as s
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas

BASE_DIR = os.path.dirname(__file__)
loader = QUiLoader()
currentCatalogue = None
currentFiche = None
currentParametre = None
currentStatistiques = None
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
    currentFiche = f.Fiche(page, formulaire, afficherLeFormulaireAuteur, afficherLeFormulaireChampsScientifique, chemainScan)
    activerRedimensionnementDynamique(currentFiche)
    ajouterBoutonFormulaire(currentFiche)
    w.close()
    print(currentFiche)
    currentFiche.window.show()

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
    currentParametre.window.Annuler.clicked.connect(lambda: currentParametre.window.close())

    activerRedimensionnementDynamique(currentParametre)
    currentParametre.window.show()

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
    
    # Mettre un stretch factor élevé sur le premier item (généralement le contenu principal)
    for i in range(layout.count()):
        item = layout.itemAt(i)
        if item and item.widget():
            child = item.widget()
            # Pour les QLabel et autres widgets, mettre une policy Expanding
            if isinstance(child, QtWidgets.QLabel):
                child.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
                child.setWordWrap(True)
            elif isinstance(child, (QtWidgets.QFrame, QtWidgets.QWidget)):
                child.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
            
            # Mettre un stretch élevé sur le premier item s'il est un label ou un texte
            if i == 0 and isinstance(child, QtWidgets.QLabel):
                layout.setStretch(i, 1)

def ajouterBoutonFormulaire(w):
    w.window.Validation.clicked.connect(lambda: w.affichage())
    w.window.Validation.clicked.connect(lambda: w.ecriture())
    w.window.Validation.clicked.connect(lambda: afficherRenduFormulaire(w))
    w.window.Quiter.clicked.connect(lambda: afficherLeCatalogue(w.window, w.chemainScan))
    w.window.Restart.clicked.connect(lambda: w.lecture(w.chemain))
    w.window.Restart.clicked.connect(lambda:w.calculeDeLaBareCentrale())
    w.window.zoomInButton.clicked.connect(lambda: w.zoom(1.2))
    w.window.zoomOutButton.clicked.connect(lambda: w.zoom(0.8))
    w.window.zoomZero.clicked.connect(lambda: w.resetZoom())
    w.window.Sauvgarde.clicked.connect(lambda: w.sauvgarde())
    w.window.Reset.clicked.connect(lambda: w.lecture(w.chemainOrigine))
    w.window.Reset.clicked.connect(lambda:w.calculeDeLaBareCentrale())
    for i in range(0,w.window.gridLayout.rowCount()):
        if w.window.gridLayout.itemAtPosition(i,2)!=None:
            field = w.window.gridLayout.itemAtPosition(i,2).widget()
            if isinstance(field, QtWidgets.QLineEdit):
                field.textChanged.connect(lambda: w.changeEdit(w.actualiserValeur()))
            #print(f"connection entre le champ de texte et la fonction changeEdit pour la ligne {i}")

def afficherRenduFormulaire(fiche=None):
    global current_Rendu
    parametrePath = os.path.join(BASE_DIR, "UI", "RenduFormulaire.ui")
    parametre = loader.load(parametrePath, None)

    def _get_response_text():
        try:
            return parametre.Reponce.toPlainText()
        except Exception:
            try:
                return parametre.Reponce.text()
            except Exception:
                return ""

    # Bouton Home: retour au catalogue
    parametre.BoutonHome.clicked.connect(lambda: afficherLeCatalogue(fiche.window, fiche.chemainScan))
    parametre.BoutonHome.clicked.connect(lambda: parametre.close())

    # Bouton Formulaire: revenir au formulaire courant
    if fiche is not None and hasattr(fiche, 'page'):
        parametre.BoutonFormulaire.clicked.connect(lambda: afficherUnFormulaire(currentCatalogue.window, fiche.page))
    else:
        parametre.BoutonFormulaire.clicked.connect(lambda:afficherUnFormulaire(currentCatalogue.window, currentCatalogue.window.listWidget.currentItem().text()))
    parametre.BoutonHome.clicked.connect(lambda: parametre.close())
    # Remplir le champ de rendu avec le texte renvoyé par fiche.affichage()
    try:
        rendu_text = fiche.affichage() if fiche is not None else ""
    except Exception:
        rendu_text = ""

    try:
        # Si Reponce est un QTextEdit
        parametre.Reponce.setPlainText(rendu_text)
    except Exception:
        try:
            # Si Reponce est un QLabel ou similaire
            parametre.Reponce.setText(rendu_text)
        except Exception:
            pass

    # Bouton Copier: copie le texte du rendu dans le presse-papier
    parametre.BoutonCopier.clicked.connect(lambda: QtWidgets.QApplication.clipboard().setText(_get_response_text()))

    # Fermer la fiche source si elle est ouverte
    try:
        if fiche is not None and hasattr(fiche, 'window'):
            fiche.window.close()
    except Exception:
        pass

    activerRedimensionnementDynamique(parametre)
    parametre.show()

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
    currentCatalogue.window.AjouterUnFichier.clicked.connect(lambda: afficherLeCatalogue(currentCatalogue.window, repertoire))
    currentCatalogue.window.Statistique.clicked.connect(lambda: afficherLesStatistiques())
    currentCatalogue.window.ChoisirUnNouveauDossierDeBase.clicked.connect(lambda: currentCatalogue.choisirRepertoireDeScan(mettreAJourChemainScan))
    activerRedimensionnementDynamique(currentCatalogue)
    
    currentCatalogue.window.show()

def afficherLeFormulaireAuteur(fiche=None):
    formulaireAuteurPath = os.path.join(BASE_DIR, "UI", "FormulaireAuteur.ui")
    formulaireAuteur = loader.load(formulaireAuteurPath, None)
    formulaireAuteurWindow = fa.FormulaireAuteur(formulaireAuteur,fiche)
    activerRedimensionnementDynamique(formulaireAuteurWindow)
    formulaireAuteurWindow.window.show()

def afficherLeFormulaireChampsScientifique(fiche=None):
    formulaireChampsScientifiquePath = os.path.join(BASE_DIR, "UI", "FormulaireChampsScientifique.ui")
    formulaireChampsScientifique = loader.load(formulaireChampsScientifiquePath, None)
    formulaireChampsScientifiqueWindow = FC.FormulaireChampsScientifique(formulaireChampsScientifique,fiche)
    activerRedimensionnementDynamique(formulaireChampsScientifiqueWindow)
    formulaireChampsScientifiqueWindow.window.show()

def afficherLesStatistiques():
    global currentStatistiques
    statistiquesPath = os.path.join(BASE_DIR, "UI", "Statistiques.ui")
    statistiques = loader.load(statistiquesPath, None)
    
    # Configurer les size policies avant activerRedimensionnementDynamique
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

    def _ajouter_canvas(figure):
        canvas = FigureCanvas(figure)
        canvas.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        canvas.setMinimumSize(300, 280)
        return canvas

    canvasRatioRéalisationHumaine = _ajouter_canvas(s.Statistique().desinnerRatioHumain())
    canvasPourcentageFait = _ajouter_canvas(s.Statistique().desinnerPourcentageFait())
    canvasNombreErreursParCatacteristique = _ajouter_canvas(s.Statistique().dessinerNombreDErreurParCaracteristique())
    canvasNombreErreursParFichier = _ajouter_canvas(s.Statistique().dessinerNombreDeCaracteristiqueCorrigeParFichier())

    gridL.addWidget(canvasRatioRéalisationHumaine, 0, 0, 1, 1)
    gridL.addWidget(canvasPourcentageFait, 0, 1, 1, 1)
    gridL.addWidget(canvasNombreErreursParCatacteristique, 1, 0, 1, 1)
    gridL.addWidget(canvasNombreErreursParFichier, 1, 1, 1, 1)

    for canvas in (canvasRatioRéalisationHumaine, canvasPourcentageFait, canvasNombreErreursParCatacteristique, canvasNombreErreursParFichier):
        canvas.draw()

    statistiques.resize(1500, 950)
    statistiques.show()

    currentStatistiques = statistiques

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    afficherLeCatalogue()
    app.exec()