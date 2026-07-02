import sys
from PySide6 import QtWidgets
from PySide6.QtUiTools import QUiLoader
from PySide6 import QtGui, QtWidgets
from PySide6 import QtCore
import os

class FormulaireAuteur:
    def __init__(self,window,fiche):
        self.window=window
        self.FormulaireAuteur_setup()
        self.fiche=fiche
        self.remplirFormulaire()

    def FormulaireAuteur_setup(self):
        self.window.setWindowTitle("Formulaire Auteur")
        self.window.AuteurPlus.clicked.connect(lambda: self.ajouterUnChamp("Auteur"))
        self.window.AuteurMoins.clicked.connect(lambda: self.removeLastRow("Auteur"))
        self.window.CoAuteurPlus.clicked.connect(lambda: self.ajouterUnChamp("CoAuteur"))
        self.window.CoAuteurMoins.clicked.connect(lambda: self.removeLastRow("CoAuteur"))
        self.window.SecondairePlus.clicked.connect(lambda: self.ajouterUnChamp("Secondaire"))
        self.window.SecondaireMoins.clicked.connect(lambda: self.removeLastRow("Secondaire"))
        self.window.Validez.clicked.connect(lambda: self.SauvegarderValeur())

    def remplirFormulaire(self):
        auteurValeurs = self.fiche.listeDesCaracteristiques[self.fiche.INDICEAUTEUR].valeur or []
        roleAuteurValeurs = self.fiche.listeDesCaracteristiques[self.fiche.INDICEROLEAUTEUR].valeur or []
        if not auteurValeurs:
            self.ajouterUnChamp("Auteur")
        else:
            for i in range(0, len(auteurValeurs)):
                self.window.formLayoutAuteur.addRow(QtWidgets.QLineEdit(),QtWidgets.QLineEdit())
                label1 = self.window.formLayoutAuteur.itemAt(i, QtWidgets.QFormLayout.LabelRole).widget()
                field1 = self.window.formLayoutAuteur.itemAt(i, QtWidgets.QFormLayout.FieldRole).widget()
                label1.setText(str(auteurValeurs[i]))
                field1.setText(str(roleAuteurValeurs[i]) if i < len(roleAuteurValeurs) else "")

        coAuteurValeurs = self.fiche.listeDesCaracteristiques[self.fiche.INDICECOAUTEUR].valeur or []
        roleCoAuteurValeurs = self.fiche.listeDesCaracteristiques[self.fiche.INDICEROLECOAUTEUR].valeur or []
        if not coAuteurValeurs:
            self.ajouterUnChamp("CoAuteur")
        else:
            for i in range(0,len(coAuteurValeurs)):
                self.window.formLayoutCoAuteur.addRow(QtWidgets.QLineEdit(),QtWidgets.QLineEdit())
                label1 = self.window.formLayoutCoAuteur.itemAt(i, QtWidgets.QFormLayout.LabelRole).widget()
                field1 = self.window.formLayoutCoAuteur.itemAt(i, QtWidgets.QFormLayout.FieldRole).widget()
                label1.setText(str(coAuteurValeurs[i]))
                field1.setText(str(roleCoAuteurValeurs[i]) if i < len(roleCoAuteurValeurs) else "")
        
        auteurSecondaireValeurs = self.fiche.listeDesCaracteristiques[self.fiche.INDICEAUTEURSECONDAIRE].valeur or []
        roleAuteurSecondaireValeurs = self.fiche.listeDesCaracteristiques[self.fiche.INDICEROLEAUTEURSECONDAIRE].valeur or []
        if not auteurSecondaireValeurs:
            self.ajouterUnChamp("Secondaire")
        else:
            for i in range(0,len(auteurSecondaireValeurs)):
                self.window.formLayoutAuteurSecondaire.addRow(QtWidgets.QLineEdit(),QtWidgets.QLineEdit())
                label1 = self.window.formLayoutAuteurSecondaire.itemAt(i, QtWidgets.QFormLayout.LabelRole).widget()
                field1 = self.window.formLayoutAuteurSecondaire.itemAt(i, QtWidgets.QFormLayout.FieldRole).widget()
                label1.setText(str(auteurSecondaireValeurs[i]))
                field1.setText(str(roleAuteurSecondaireValeurs[i]) if i < len(roleAuteurSecondaireValeurs) else "")
            
    def ajouterUnChamp(self,type):
        if type == "Auteur":
            self.window.formLayoutAuteur.addRow(QtWidgets.QLineEdit(),QtWidgets.QLineEdit()) 
        elif type == "CoAuteur":
            self.window.formLayoutCoAuteur.addRow(QtWidgets.QLineEdit(),QtWidgets.QLineEdit())
        elif type == "Secondaire":
            self.window.formLayoutAuteurSecondaire.addRow(QtWidgets.QLineEdit(),QtWidgets.QLineEdit())
        ##redimantionnement(w)
        
    def removeLastRow(self,type):
        if type == "Auteur":
            row=self.window.formLayoutAuteur.rowCount()
            if row > 0:
                self.window.formLayoutAuteur.removeRow(row-1)
        elif type == "CoAuteur":
            row=self.window.formLayoutCoAuteur.rowCount()
            if row > 0:
                self.window.formLayoutCoAuteur.removeRow(row-1)
        elif type == "Secondaire":
            row=self.window.formLayoutAuteurSecondaire.rowCount()
            if row > 0:
                self.window.formLayoutAuteurSecondaire.removeRow(row-1)
        ##redimantionnement(w)

    def redimantionnement(self):
    ##TODO
        pass

    def SauvegarderValeur(self):
        nvAuteurs = []
        nvRoleAuteurs = []
        nvCoAuteurs = []
        nvRoleCoAuteurs = []
        nvAuteursSecondaires = []
        nvRoleAuteursSecondaires = []
        for i in range(0,self.window.formLayoutAuteur.rowCount()):
            nvAuteurs.append(self.window.formLayoutAuteur.itemAt(i, QtWidgets.QFormLayout.LabelRole).widget().text())
            nvRoleAuteurs.append(self.window.formLayoutAuteur.itemAt(i, QtWidgets.QFormLayout.FieldRole).widget().text())
        if nvAuteurs != self.fiche.listeDesCaracteristiques[self.fiche.INDICEAUTEUR].valeur or nvRoleAuteurs != self.fiche.listeDesCaracteristiques[self.fiche.INDICEROLEAUTEUR].valeur:
            self.fiche.listeDesCaracteristiques[self.fiche.INDICEAUTEUR].setValeur(nvAuteurs)
            self.fiche.changeEdit(self.fiche.INDICEAUTEUR+1)
            self.fiche.listeDesCaracteristiques[self.fiche.INDICEROLEAUTEUR].setValeur(nvRoleAuteurs)
            self.fiche.changeEdit(self.fiche.INDICEROLEAUTEUR+1)

        for i in range(0,self.window.formLayoutCoAuteur.rowCount()):
            nvCoAuteurs.append(self.window.formLayoutCoAuteur.itemAt(i, QtWidgets.QFormLayout.LabelRole).widget().text())
            nvRoleCoAuteurs.append(self.window.formLayoutCoAuteur.itemAt(i, QtWidgets.QFormLayout.FieldRole).widget().text())
        if nvCoAuteurs != self.fiche.listeDesCaracteristiques[self.fiche.INDICECOAUTEUR].valeur or nvRoleCoAuteurs != self.fiche.listeDesCaracteristiques[self.fiche.INDICEROLECOAUTEUR].valeur:
            self.fiche.listeDesCaracteristiques[self.fiche.INDICECOAUTEUR].setValeur(nvCoAuteurs)
            self.fiche.changeEdit(self.fiche.INDICECOAUTEUR+1)
            self.fiche.listeDesCaracteristiques[self.fiche.INDICEROLECOAUTEUR].setValeur(nvRoleCoAuteurs)
            self.fiche.changeEdit(self.fiche.INDICEROLECOAUTEUR+1)

        for i in range(0,self.window.formLayoutAuteurSecondaire.rowCount()):
            nvAuteursSecondaires.append(self.window.formLayoutAuteurSecondaire.itemAt(i, QtWidgets.QFormLayout.LabelRole).widget().text())
            nvRoleAuteursSecondaires.append(self.window.formLayoutAuteurSecondaire.itemAt(i, QtWidgets.QFormLayout.FieldRole).widget().text())
        if nvAuteursSecondaires != self.fiche.listeDesCaracteristiques[self.fiche.INDICEAUTEURSECONDAIRE].valeur or nvRoleAuteursSecondaires != self.fiche.listeDesCaracteristiques[self.fiche.INDICEROLEAUTEURSECONDAIRE].valeur:
            self.fiche.listeDesCaracteristiques[self.fiche.INDICEAUTEURSECONDAIRE].setValeur(nvAuteursSecondaires)
            self.fiche.changeEdit(self.fiche.INDICEAUTEURSECONDAIRE+1)
            self.fiche.listeDesCaracteristiques[self.fiche.INDICEROLEAUTEURSECONDAIRE].setValeur(nvRoleAuteursSecondaires)
            self.fiche.changeEdit(self.fiche.INDICEROLEAUTEURSECONDAIRE+1)
        self.window.close()

        