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
        self.window.Validez.clicked.connect(lambda: self.retourConsole())

    def remplirFormulaire(self):
        for i in range(0, self.fiche.listeDesCaracteristiques[self.fiche.INDICEAUTEUR].valeur.__len__()):
            self.window.formLayoutAuteur.addRow(QtWidgets.QLineEdit(),QtWidgets.QLineEdit())
            label1 = self.window.formLayoutAuteur.itemAt(i, QtWidgets.QFormLayout.LabelRole).widget()
            field1 = self.window.formLayoutAuteur.itemAt(i, QtWidgets.QFormLayout.FieldRole).widget()
            label1.setText(self.fiche.listeDesCaracteristiques[self.fiche.INDICEAUTEUR].valeur[i])
            field1.setText(self.fiche.listeDesCaracteristiques[self.fiche.INDICEROLEAUTEUR].valeur[i])

        for i in range(0,self.fiche.listeDesCaracteristiques[self.fiche.INDICECOAUTEUR].valeur.__len__()):
            self.window.formLayoutCoAuteur.addRow(QtWidgets.QLineEdit(),QtWidgets.QLineEdit())
            label1 = self.window.formLayoutCoAuteur.itemAt(i, QtWidgets.QFormLayout.LabelRole).widget()
            field1 = self.window.formLayoutCoAuteur.itemAt(i, QtWidgets.QFormLayout.FieldRole).widget()
            label1.setText(self.fiche.listeDesCaracteristiques[self.fiche.INDICECOAUTEUR].valeur[i])
            field1.setText(self.fiche.listeDesCaracteristiques[self.fiche.INDICEROLECOAUTEUR].valeur[i])

        for i in range(0,self.fiche.listeDesCaracteristiques[self.fiche.INDICEAUTEURSECONDAIRE].valeur.__len__()):
            self.window.formLayoutAuteurSecondaire.addRow(QtWidgets.QLineEdit(),QtWidgets.QLineEdit())
            label1 = self.window.formLayoutAuteurSecondaire.itemAt(i, QtWidgets.QFormLayout.LabelRole).widget()
            field1 = self.window.formLayoutAuteurSecondaire.itemAt(i, QtWidgets.QFormLayout.FieldRole).widget()
            label1.setText(self.fiche.listeDesCaracteristiques[self.fiche.INDICEAUTEURSECONDAIRE].valeur[i])
            field1.setText(self.fiche.listeDesCaracteristiques[self.fiche.INDICEROLEAUTEURSECONDAIRE].valeur[i])
        
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
            self.fiche.listeDesCaracteristiques[self.fiche.INDICEAUTEUR].valeur = nvAuteurs
            self.fiche.change_edit(self.fiche.INDICEAUTEUR+1)
            self.fiche.listeDesCaracteristiques[self.fiche.INDICEROLEAUTEUR].valeur = nvRoleAuteurs
            self.fiche.change_edit(self.fiche.INDICEROLEAUTEUR+1)

        for i in range(0,self.window.formLayoutCoAuteur.rowCount()):
            nvCoAuteurs.append(self.window.formLayoutCoAuteur.itemAt(i, QtWidgets.QFormLayout.LabelRole).widget().text())
            nvRoleCoAuteurs.append(self.window.formLayoutCoAuteur.itemAt(i, QtWidgets.QFormLayout.FieldRole).widget().text())
        if nvCoAuteurs != self.fiche.listeDesCaracteristiques[self.fiche.INDICECOAUTEUR].valeur or nvRoleCoAuteurs != self.fiche.listeDesCaracteristiques[self.fiche.INDICEROLECOAUTEUR].valeur:
            self.fiche.listeDesCaracteristiques[self.fiche.INDICECOAUTEUR].valeur = nvCoAuteurs
            self.fiche.change_edit(self.fiche.INDICECOAUTEUR+1)
            self.fiche.listeDesCaracteristiques[self.fiche.INDICEROLECOAUTEUR].valeur = nvRoleCoAuteurs
            self.fiche.change_edit(self.fiche.INDICEROLECOAUTEUR+1)

        for i in range(0,self.window.formLayoutAuteurSecondaire.rowCount()):
            nvAuteursSecondaires.append(self.window.formLayoutAuteurSecondaire.itemAt(i, QtWidgets.QFormLayout.LabelRole).widget().text())
            nvRoleAuteursSecondaires.append(self.window.formLayoutAuteurSecondaire.itemAt(i, QtWidgets.QFormLayout.FieldRole).widget().text())
        if nvAuteursSecondaires != self.fiche.listeDesCaracteristiques[self.fiche.INDICEAUTEURSECONDAIRE].valeur or nvRoleAuteursSecondaires != self.fiche.listeDesCaracteristiques[self.fiche.INDICEROLEAUTEURSECONDAIRE].valeur:
            self.fiche.listeDesCaracteristiques[self.fiche.INDICEAUTEURSECONDAIRE].valeur = nvAuteursSecondaires
            self.fiche.change_edit(self.fiche.INDICEAUTEURSECONDAIRE+1)
            self.fiche.listeDesCaracteristiques[self.fiche.INDICEROLEAUTEURSECONDAIRE].valeur = nvRoleAuteursSecondaires
            self.fiche.change_edit(self.fiche.INDICEROLEAUTEURSECONDAIRE+1)


    def retourConsole(self):
        self.SauvegarderValeur()
        self.fiche.updateButtons()
        text=""
        for i in range(0,self.window.formLayoutAuteur.rowCount()):
            label1 = self.window.formLayoutAuteur.itemAt(i, QtWidgets.QFormLayout.LabelRole).widget()
            field1 = self.window.formLayoutAuteur.itemAt(i, QtWidgets.QFormLayout.FieldRole).widget()
            text+=f"Auteur {i+1}: {label1.text()} {field1.text()}\n"
        for i in range(0,self.window.formLayoutCoAuteur.rowCount()):
            label1 = self.window.formLayoutCoAuteur.itemAt(i, QtWidgets.QFormLayout.LabelRole).widget()
            field1 = self.window.formLayoutCoAuteur.itemAt(i, QtWidgets.QFormLayout.FieldRole).widget()
            text+=f"CoAuteur {i+1}: {label1.text()} {field1.text()}\n"
        for i in range(0,self.window.formLayoutAuteurSecondaire.rowCount()):
            label1 = self.window.formLayoutAuteurSecondaire.itemAt(i, QtWidgets.QFormLayout.LabelRole).widget()
            field1 = self.window.formLayoutAuteurSecondaire.itemAt(i, QtWidgets.QFormLayout.FieldRole).widget()
            text+=f"Secondaire {i+1}: {label1.text()} {field1.text()}\n"
        print(text)
        self.window.close()