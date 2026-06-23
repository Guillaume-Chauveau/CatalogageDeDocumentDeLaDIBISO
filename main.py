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

BASE_DIR = os.path.dirname(__file__)
loader = QUiLoader()
current_catalogue = None
current_fiche = None
current_parametre = None
current_statistiques = None

def afficherUnFormulaire(w, page):
    global current_fiche
    formulaire_path = os.path.join(BASE_DIR, "UI", "Formulaire.ui")
    formulaire = loader.load(formulaire_path, None)
    current_fiche = f.Fiche(page, formulaire, afficherLeFormulaireAuteur, afficherLeFormulaireChampsScientifique)
    activerRedimensionnementDynamique(current_fiche)
    ajouterBoutonFormulaire(current_fiche)
    w.close()
    print(current_fiche)
    current_fiche.window.show()

def afficherLesParametres():
    global current_parametre
    parametre_path = os.path.join(BASE_DIR, "UI", "Parametre.ui")
    parametre = loader.load(parametre_path, None)
    current_parametre = p.Parametre(parametre)
    current_parametre.window.ParametreCommun.clicked.connect(lambda: current_parametre.clickFixe())
    current_parametre.window.ParametreHebdomadaire.clicked.connect(lambda: current_parametre.clickHebdo())
    current_parametre.window.ParametreClassique.clicked.connect(lambda: current_parametre.clickClassique())
    current_parametre.window.ToutVrai.clicked.connect(lambda: current_parametre.clickVraiTout())
    current_parametre.window.ToutFaux.clicked.connect(lambda: current_parametre.clickFauxTout())
    current_parametre.window.Valider.clicked.connect(lambda: current_parametre.retour())
    current_parametre.window.Annuler.clicked.connect(lambda: current_parametre.window.close())

    activerRedimensionnementDynamique(current_parametre)
    current_parametre.window.show()

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
    w.window.Quiter.clicked.connect(lambda: afficherLeCatalogue(w.window))
    w.window.Restart.clicked.connect(lambda: w.lecture(w.chemain))
    w.window.Restart.clicked.connect(lambda:w.calculeDeLaBareCentrale())
    w.window.zoomInButton.clicked.connect(lambda: w.zoom(1.2))
    w.window.zoomOutButton.clicked.connect(lambda: w.zoom(0.8))
    w.window.zoomZero.clicked.connect(lambda: w.reset_zoom())
    w.window.Sauvgarde.clicked.connect(lambda: w.sauvgarde())
    w.window.Reset.clicked.connect(lambda: w.lecture(w.chemainOrigine))
    w.window.Reset.clicked.connect(lambda:w.calculeDeLaBareCentrale())
    for i in range(0,w.window.gridLayout.rowCount()):
        if w.window.gridLayout.itemAtPosition(i,2)!=None:
            field = w.window.gridLayout.itemAtPosition(i,2).widget()
            if isinstance(field, QtWidgets.QLineEdit):
                field.textChanged.connect(lambda: w.change_edit(w.actualiserValeur()))
            #print(f"connection entre le champ de texte et la fonction change_edit pour la ligne {i}")

def afficherRenduFormulaire(fiche=None):
    global current_Rendu
    parametre_path = os.path.join(BASE_DIR, "UI", "RenduFormulaire.ui")
    parametre = loader.load(parametre_path, None)

    def _get_response_text():
        try:
            return parametre.Reponce.toPlainText()
        except Exception:
            try:
                return parametre.Reponce.text()
            except Exception:
                return ""

    # Bouton Home: retour au catalogue
    parametre.BoutonHome.clicked.connect(lambda: afficherLeCatalogue(fiche.window))
    parametre.BoutonHome.clicked.connect(lambda: parametre.close())

    # Bouton Formulaire: revenir au formulaire courant
    if fiche is not None and hasattr(fiche, 'page'):
        parametre.BoutonFormulaire.clicked.connect(lambda: afficherUnFormulaire(current_catalogue.window, fiche.page))
    else:
        parametre.BoutonFormulaire.clicked.connect(lambda:afficherUnFormulaire(current_catalogue.window, current_catalogue.window.listWidget.currentItem().text()))
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

def afficherLeCatalogue(w=None):
    if w is not None:
        w.close()
    global current_catalogue
    catalogue_path = os.path.join(BASE_DIR, "UI", "changementDePage.ui")
    catalogue = loader.load(catalogue_path, None)
    current_catalogue = Catalogue.ListeAFinir(catalogue)
    current_catalogue.window.Reactualiser.clicked.connect(lambda: afficherLeCatalogue(current_catalogue.window))
    current_catalogue.window.listWidget.currentItemChanged.connect(lambda: afficherUnFormulaire(current_catalogue.window, current_catalogue.window.listWidget.currentItem().text()))
    current_catalogue.window.VoirFini.checkStateChanged.connect(lambda: current_catalogue.creerCatalogue())
    current_catalogue.window.Parametre.clicked.connect(lambda: afficherLesParametres())
    current_catalogue.window.AjouterUnFichier.clicked.connect(lambda: current_catalogue.openFileDialog())
    current_catalogue.window.AjouterUnFichier.clicked.connect(lambda: afficherLeCatalogue(current_catalogue.window))
    current_catalogue.window.Statistique.clicked.connect(lambda: afficherLesStatistiques())
    activerRedimensionnementDynamique(current_catalogue)
    
    current_catalogue.window.show()

def afficherLeFormulaireAuteur(fiche=None):
    formulaire_auteur_path = os.path.join(BASE_DIR, "UI", "FormulaireAuteur.ui")
    formulaire_auteur = loader.load(formulaire_auteur_path, None)
    formulaire_auteur_window = fa.FormulaireAuteur(formulaire_auteur,fiche)
    activerRedimensionnementDynamique(formulaire_auteur_window)
    formulaire_auteur_window.window.show()

def afficherLeFormulaireChampsScientifique(fiche=None):
    formulaire_champs_scientifique_path = os.path.join(BASE_DIR, "UI", "FormulaireChampsScientifique.ui")
    formulaire_champs_scientifique = loader.load(formulaire_champs_scientifique_path, None)
    formulaire_champs_scientifique_window = FC.FormulaireChampsScientifique(formulaire_champs_scientifique,fiche)
    activerRedimensionnementDynamique(formulaire_champs_scientifique_window)
    formulaire_champs_scientifique_window.window.show()

def afficherLesStatistiques():
    global current_statistiques
    statistiques_path = os.path.join(BASE_DIR, "UI", "Statistiques.ui")
    statistiques = loader.load(statistiques_path, None)
    activerRedimensionnementDynamique(statistiques)
    statistiques.Retour.clicked.connect(lambda: statistiques.close())
    statistiques.show()
    current_statistiques = statistiques

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    afficherLeCatalogue()
    app.exec()