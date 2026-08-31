import sys
import os
import traceback  # en haut du fichier, avec les autres imports

def _lancerStatistiquesAvecDiagnostic():
    try:
        print("clic reçu1")
        afficherLesStatistiques()
        print("clic reçu")
    except Exception as exc:
        traceback.print_exc()
        QMessageBox.critical(
            currentCatalogue.window,
            "Erreur Statistiques",
            f"{type(exc).__name__}: {exc}",
        )
# PyInstaller: le bundle n'inclut pas toujours le magasin CA SSL utilisé par httpx/openai.
if getattr(sys, "frozen", False):
    try:
        import certifi

        os.environ.setdefault("SSL_CERT_FILE", certifi.where())
        os.environ.setdefault("REQUESTS_CA_BUNDLE", certifi.where())
    except ImportError:
        pass

from PySide6 import QtCore, QtGui, QtWidgets
from PySide6.QtWidgets import QFileDialog,QMessageBox
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


from app_paths import get_resource_dir, add_scan_directory, bootstrap_scan_directories


BASE_DIR = get_resource_dir()
loader = QUiLoader()
bootstrap_scan_directories()


def enregistrerUnimarc(fenetre, obtenir_texte):
    """Enregistre le texte affiché dans le rendu au format .txt."""
    fichier, _ = QFileDialog.getSaveFileName(fenetre, "Enregistrer", "", "Texte (*.txt)")

    if not fichier:
        return

    try:
        with open(fichier, 'w', encoding='utf-8') as fichier_sortie:
            fichier_sortie.write(obtenir_texte())
        QMessageBox.information(fenetre, "Succès", "Fichier enregistré.")
    except Exception as exc:
        QMessageBox.critical(fenetre, "Erreur", str(exc))


class WindowManager:
    """Centralise l'affichage et la fermeture des fenêtres principales."""
    def __init__(self):
        self._windows = {}

    @staticmethod
    def _cible(obj):
        """obj peut être soit la fenêtre Qt elle-même, soit un wrapper
        (ex. currentCatalogue) exposant la fenêtre via .window.
        ATTENTION: tout QWidget possède nativement une méthode .window()
        (héritée de Qt) qui renvoie le widget de plus haut niveau. Donc
        getattr(obj, "window", obj) sur un QMainWindow "nu" (ex. la fenêtre
        Statistiques, chargée directement par loader.load) retombe sur cette
        méthode bound au lieu du obj par défaut -> hasattr(target, "show")
        est alors False et .show() n'est jamais appelé, silencieusement.
        On ne suit .window que si c'est vraiment un widget Qt (le cas des
        wrappers comme currentCatalogue.window), jamais une méthode."""
        interieur = getattr(obj, "window", None)
        if isinstance(interieur, QtWidgets.QWidget):
            return interieur
        return obj

    def register(self, name, obj):
        self._windows[name] = obj
        return obj

    def get(self, name, default=None):
        return self._windows.get(name, default)

    def close(self, name):
        obj = self._windows.pop(name, None)
        if obj is None:
            return None

        target = self._cible(obj)
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

        target = self._cible(obj)
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
chemainRepetoireDeTravail = "Scan"  # Répertoire par défaut pour les scans
chemainScan = "Scan"

def mettreAJourChemainScan(repertoire):
    global chemainRepetoireDeTravail
    chemainRepetoireDeTravail = repertoire
    if repertoire:
        add_scan_directory(repertoire)

def afficherUnFormulaire(w, page):
    global currentFiche, chemainRepetoireDeTravail
    if currentCatalogue is not None:
        chemainRepetoireDeTravail = currentCatalogue.repertoirDesScan

    formulairePath = os.path.join(BASE_DIR, "UI", "Formulaire.ui")
    formulaire = loader.load(formulairePath, None)
    
    currentFiche = f.Fiche(page, formulaire, afficherLeFormulaireAuteur, afficherLeFormulaireChampsScientifique,afficherLeFormulaireCollection, chemainRepetoireDeTravail)
    activerRedimensionnementDynamique(currentFiche)
    currentFiche.window.showMaximized()
    ajouterBoutonFormulaire(currentFiche)

    if w is not None:
        w.close()

    window_manager.show("fiche", currentFiche)

def afficherLesParametres():
    global currentParametre
    parametrePath = os.path.join(BASE_DIR, "UI", "Parametre.ui")
    parametre = loader.load(parametrePath, None)

    currentParametre = p.Parametre(parametre)

    def _valider_parametres():
        if currentParametre.retour():
            currentParametre.window.close()

    currentParametre.window.Valider.clicked.connect(_valider_parametres)
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

    scan_dir = getattr(w, "chemainScan", None) or getattr(w, "chemainDossierDeTravail", None) or "Scan"
    w.window.Quiter.clicked.connect(lambda: afficherLeCatalogue(w.window, scan_dir))
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
    w.window.Recalculer.clicked.connect(lambda: w.Regenerer())
    w.window.Recalculer.setToolTip("Relance l’analyse via l’API sur l’image courante")
    w.window.BoutonTitre.clicked.connect(lambda: w.copieFileName())

    for i in range(0, w.window.gridLayout.rowCount()):
        if w.window.gridLayout.itemAtPosition(i, 2) is not None:
            field = w.window.gridLayout.itemAtPosition(i, 2).widget()
            if isinstance(field, QtWidgets.QLineEdit):
                field.textChanged.connect(lambda: w.changeEdit(w.actualiserValeur()))

def afficherRenduFormulaire(fiche=None):
    global currentRenduFormulaire

    parametrePath = os.path.join(BASE_DIR, "UI", "RenduFormulaire.ui")
    rendu = loader.load(parametrePath, None)

    if rendu is None:
        print("Erreur: impossible de charger RenduFormulaire.ui")
        return

    if hasattr(rendu, "setWindowTitle"):
        rendu.setWindowTitle("Rendu du formulaire")
    if hasattr(rendu, "resize"):
        rendu.resize(800, 600)
    if hasattr(rendu, "setAttribute"):
        rendu.setAttribute(QtCore.Qt.WA_DeleteOnClose, False)

    def _get_response_text():
        try:
            return rendu.Reponce.toPlainText()
        except Exception:
            try:
                return rendu.Reponce.text()
            except Exception:
                return ""

    def _fermer_rendu_et_executer(action):
        try:
            window_manager.close("rendu")
            QtWidgets.QApplication.processEvents()
        except Exception as exc:
            print(f"[Rendu] Erreur lors de la fermeture de la fenêtre de rendu: {exc}")
        try:
            action()
        except Exception as exc:
            print(f"[Rendu] Erreur lors de l'exécution de l'action: {exc}")

    try:
        rendu_text = fiche.affichage() if fiche is not None and hasattr(fiche, "affichage") else ""
    except Exception as exc:
        print(f"[Rendu] Erreur dans fiche.affichage(): {exc}")
        rendu_text = ""

    try:
        rendu.Reponce.setText(rendu_text)
    except Exception:
        try:
            rendu.Reponce.setPlainText(rendu_text)
        except Exception as exc:
            print(f"[Rendu] Impossible d'écrire dans Reponce: {exc}")

    rendu.BoutonCopier.clicked.connect(
        lambda: QtWidgets.QApplication.clipboard().setText(_get_response_text())
    )

    if fiche is not None:
        page = getattr(fiche, "nomDuFichier", None)
        if page is None:
            page = getattr(fiche, "page", None)

        rendu.BoutonFormulaire.clicked.connect(
            lambda: _fermer_rendu_et_executer(
                lambda: afficherUnFormulaire(getattr(fiche, "window", None), page)
            )
        )
        rendu.BoutonHome.clicked.connect(
            lambda: _fermer_rendu_et_executer(
                lambda: afficherLeCatalogue(
                    getattr(fiche, "window", None),
                    getattr(fiche, "chemainScan", None) or getattr(fiche, "chemainDossierDeTravail", None) or "Scan",
                )
            )
        )
    else:
        rendu.BoutonFormulaire.clicked.connect(lambda: None)
        rendu.BoutonHome.clicked.connect(lambda: None)

    rendu.BoutonExporter.clicked.connect(
        lambda: enregistrerUnimarc(rendu, _get_response_text)
    )
    try:
        if fiche is not None and hasattr(fiche, "window") and fiche.window is not None:
            fiche.window.close()
    except Exception as exc:
        print(f"[Rendu] Erreur lors de la fermeture de la fiche: {exc}")

    currentRenduFormulaire = rendu

    window_manager.close("rendu")
    window_manager.show("rendu", rendu)
    rendu.show()
    rendu.raise_()
    rendu.activateWindow()
    QtWidgets.QApplication.processEvents()

def afficherLeCatalogue(w=None, repertoire="Scan"):
    global currentCatalogue, chemainRepetoireDeTravail
    if currentCatalogue is not None and getattr(currentCatalogue, "repertoirDesScan", ""):
        repertoire = currentCatalogue.repertoirDesScan

    mettreAJourChemainScan(repertoire)

    if w is not None:
        w.close()

    cataloguePath = os.path.join(BASE_DIR, "UI", "changementDePage.ui")
    catalogue = loader.load(cataloguePath, None)

    currentCatalogue = Catalogue.ListeAFinir(catalogue, repertoire)
    currentCatalogue.window.Reactualiser.clicked.connect(lambda: afficherLeCatalogue(currentCatalogue.window, repertoire))
    def _ouvrir_fiche_selectionnee():
        item = currentCatalogue.window.listWidget.currentItem()
        if item is None:
            return
        afficherUnFormulaire(currentCatalogue.window, item.text())

    currentCatalogue.window.listWidget.currentItemChanged.connect(lambda _cur, _prev: _ouvrir_fiche_selectionnee())
    currentCatalogue.window.VoirFini.checkStateChanged.connect(lambda: currentCatalogue.creerCatalogue())
    currentCatalogue.window.Parametre.clicked.connect(lambda: afficherLesParametres())
    currentCatalogue.window.AjouterUnFichier.clicked.connect(lambda: currentCatalogue.openFileDialog())
    currentCatalogue.window.Statistique.show()
    currentCatalogue.window.Statistique.setEnabled(True)
    currentCatalogue.window.Statistique.clicked.connect(lambda: _lancerStatistiquesAvecDiagnostic())
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

    # Une seule instance -> une seule passe de cache pour toute la fenêtre
    stat = s.Statistique()

    centralWidget = QtWidgets.QWidget()
    layoutPrincipal = QtWidgets.QVBoxLayout(centralWidget)
    layoutPrincipal.setContentsMargins(10, 10, 10, 40)
    layoutPrincipal.setSpacing(15)

    scrollArea = QtWidgets.QScrollArea()
    scrollArea.setWidgetResizable(True)
    scrollArea.setWidget(centralWidget)
    statistiques.setCentralWidget(scrollArea)

    gridL = QtWidgets.QGridLayout()
    layoutPrincipal.addLayout(gridL)
    gridL.setSpacing(10)
    for col in (0, 1):
        gridL.setColumnStretch(col, 1)
    for row in (0, 1):
        gridL.setRowStretch(row, 1)

    def _ajouterCanvas(figure, hauteur_min=280):
        canvas = FigureCanvas(figure)
        canvas.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        canvas.setMinimumSize(300, hauteur_min)
        canvas.draw()
        return canvas

    gridL.addWidget(_ajouterCanvas(stat.dessinerRepartitionLangues()), 0, 0)
    gridL.addWidget(_ajouterCanvas(stat.dessinerRepartitionAnnees()), 0, 1)
    gridL.addWidget(_ajouterCanvas(stat.dessinerConfianceMoyenneParChamp()), 1, 0)
    gridL.addWidget(_ajouterCanvas(stat.dessinerPourcentageFait()), 1, 1)

    # -- graphique personnalisable --------------------------------------
    barreControles = QtWidgets.QHBoxLayout()
    comboX = QtWidgets.QComboBox()
    comboX.addItems(stat.champsDisponibles())
    comboY = QtWidgets.QComboBox()
    comboY.addItems(stat.metriquesDisponibles())
    boutonTracer = QtWidgets.QPushButton("Tracer")
    boutonRafraichir = QtWidgets.QPushButton("Rafraîchir les données")

    barreControles.addWidget(QtWidgets.QLabel("Axe X :"))
    barreControles.addWidget(comboX)
    barreControles.addWidget(QtWidgets.QLabel("Axe Y :"))
    barreControles.addWidget(comboY)
    barreControles.addWidget(boutonTracer)
    barreControles.addWidget(boutonRafraichir)
    layoutPrincipal.addLayout(barreControles)

    conteneurCustom = QtWidgets.QVBoxLayout()
    layoutPrincipal.addLayout(conteneurCustom)

    def _tracerPersonnalise():
        while conteneurCustom.count():
            item = conteneurCustom.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        # Labels en X pivotés à 60° + potentiellement longs -> plus de hauteur
        # que les mini-graphiques du dashboard, sinon le texte est coupé.
        canvas = _ajouterCanvas(
            stat.dessinerGraphiquePersonnalise(comboX.currentText(), comboY.currentText()),
            hauteur_min=460,
        )
        conteneurCustom.addWidget(canvas)
        # Le contenu vient de changer de taille : on force le recalcul de la
        # zone défilable tout de suite, sinon le QScrollArea garde parfois
        # l'ancienne étendue jusqu'au prochain redimensionnement manuel.
        centralWidget.adjustSize()
        centralWidget.updateGeometry()
        scrollArea.updateGeometry()

    boutonTracer.clicked.connect(_tracerPersonnalise)
    boutonRafraichir.clicked.connect(lambda: (stat.rafraichir(), _tracerPersonnalise()))
    _tracerPersonnalise()

    # Taille fixe 1500x1200 = si l'écran (zone utile, hors barre des tâches)
    # est plus petit, le bas de la fenêtre -et donc le bas du scroll- est
    # hors écran et aucun défilement interne ne peut compenser. On plafonne
    # donc à la zone réellement disponible.
    ecran = QtWidgets.QApplication.primaryScreen()
    largeur_voulue, hauteur_voulue = 1500, 1200
    if ecran is not None:
        disponible = ecran.availableGeometry()
        largeur_voulue = min(largeur_voulue, disponible.width() - 40)
        hauteur_voulue = min(hauteur_voulue, disponible.height() - 40)
        statistiques.resize(largeur_voulue, hauteur_voulue)
        # S'assure que la fenêtre est bien positionnée dans la zone visible
        # (au cas où une position hors écran aurait été héritée).
        statistiques.move(disponible.topLeft())
    else:
        statistiques.resize(largeur_voulue, hauteur_voulue)

    currentStatistiques = statistiques
    window_manager.show("statistiques", statistiques)
    

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    afficherLeCatalogue()
    if not p.has_api_key():
        p.avertir_si_clef_api_manquante()
        afficherLesParametres()
    app.exec()