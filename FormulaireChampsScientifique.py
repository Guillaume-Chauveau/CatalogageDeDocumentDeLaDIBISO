from PySide6 import QtWidgets
from PySide6 import QtGui, QtWidgets

class FormulaireChampsScientifique:
    def __init__(self,window,fiche):
        self.window=window
        self.formulaireChampsScientifique_setup()
        self.fiche=fiche
        self.chargerChampsScientifiques()
        self.remplirFormulaire()
    # Liste partagée des champs scientifiques
    champs_scientifiques = ["Champs Scientifique", "Physique"]

    def formulaireChampsScientifique_setup(self):
        self.window.setWindowTitle("Formulaire Champs Scientifique")
        self.window.ChampsScientifiquePlus.clicked.connect(lambda: self.ajouterUnChamp())
        self.window.ChampsScientifiqueMoins.clicked.connect(lambda: self.removeLastRow())
        self.window.NouveauChampsScientifiqueValider.clicked.connect(lambda: self.validerNouveauChamp())
        self.window.NouveauChampsScientifiqueAnnuler.clicked.connect(lambda: self.annulerNouveauChamp())      
        self.window.buttonBox.accepted.connect(lambda: self.sauvegarderFormulaire())

    def remplirFormulaire(self):
        for i in range(0, len(self.fiche.listeDesCaracteristiques[self.fiche.INDICECHAMPSCIENTIFIQUE].valeur)):
            self.window.ChampsScientifiqueListe.addWidget(QtWidgets.QComboBox())
            combo = self.window.ChampsScientifiqueListe.itemAt(i).widget()
            combo.addItems(self.champs_scientifiques)
            combo.setCurrentText(self.fiche.listeDesCaracteristiques[self.fiche.INDICECHAMPSCIENTIFIQUE].valeur[i])
    
    def sauvegarderFormulaire(self):
        champs_selectionnes = []
        for i in range(self.window.ChampsScientifiqueListe.count()):
            item = self.window.ChampsScientifiqueListe.itemAt(i)
            combo = item.widget()
            if isinstance(combo, QtWidgets.QComboBox):
                champs_selectionnes.append(combo.currentText())
        self.fiche.listeDesCaracteristiques[self.fiche.INDICECHAMPSCIENTIFIQUE].setValeur(champs_selectionnes)
        self.fiche.changeEdit(self.fiche.INDICECHAMPSCIENTIFIQUE+1)
        self.fiche.updateButtons()

    def ajouterUnChamp(self):
        combo = QtWidgets.QComboBox()
        combo.addItems(self.champs_scientifiques)
        self.window.ChampsScientifiqueListe.addWidget(combo)

    def removeLastRow(self):
        row = self.window.ChampsScientifiqueListe.count()
        if row > 0:
            item = self.window.ChampsScientifiqueListe.itemAt(row-1)
            widget = item.widget()
            self.window.ChampsScientifiqueListe.removeItem(item)
            widget.deleteLater()

    def validerNouveauChamp(self):
        nouveau = self.window.NouveauChampsScientifique.text().strip()
        if nouveau and nouveau not in self.champs_scientifiques:
            self.champs_scientifiques.append(nouveau)
            # Mettre à jour tous les comboBoxes existants
            self.updateAllCombos()
            self.window.NouveauChampsScientifique.clear()
            self.sauvegarderChampsScientifiques()

    def annulerNouveauChamp(self):
        self.NouveauChampsScientifique.clear()

    def updateAllCombos(self):
        # Mettre à jour les autres comboBoxes dans la liste
        for i in range(0,self.window.ChampsScientifiqueListe.count()):
            item = self.window.ChampsScientifiqueListe.itemAt(i)
            combo = item.widget()
            if isinstance(combo, QtWidgets.QComboBox):
                combo.clear()
                combo.addItems(self.champs_scientifiques)

    def sauvegarderChampsScientifiques(self):
        # Sauvegarder la liste des champs scientifiques dans un fichier
        with open("champs_scientifiques.txt", "w") as f:
            for champ in self.champs_scientifiques:
                f.write(champ + "\n")

    def chargerChampsScientifiques(self):
        # Charger la liste des champs scientifiques depuis un fichier
        try:
            with open("champs_scientifiques.txt", "r") as f:
                self.champs_scientifiques = [line.strip() for line in f if line.strip()]
                self.updateAllCombos()
        except FileNotFoundError:
            pass 