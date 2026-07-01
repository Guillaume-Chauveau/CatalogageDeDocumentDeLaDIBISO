import sys
from PySide6 import QtWidgets
from PySide6.QtUiTools import QUiLoader
from PySide6 import QtGui, QtWidgets
from PySide6 import QtCore
import os
import unicodedata

import Caracteristique as c
import CaracteristiqueMultiple as cm

class Fiche:
    window=None
    listeDesCaracteristiques=[]
    listeDesNomDeCaracteristiques=["Article","Titre","Auteur","Complement du titre","Numero du volume","Ville","Editeur","Annee","Volume","Illustration","Taille","Champ Scientifique","Premier Auteur","Co-Auteur","Role Auteur","Role CoAuteur","Auteur Secondaire","Role Auteur Secondaire","Nom de la Collectivite","Role de la Collectivite"]
    listeDesNomDeCaracteristiquesMultiple=["Champ Scientifique","Premier Auteur","Role Auteur","Co-Auteur","Role CoAuteur","Auteur Secondaire","Role Auteur Secondaire"]
    chemain=""
    nomDuFichier=""
    INDICECHAMPSCIENTIFIQUE=10
    INDICEAUTEUR=11
    INDICEROLEAUTEUR=13
    INDICECOAUTEUR=12
    INDICEROLECOAUTEUR=14
    INDICEAUTEURSECONDAIRE=15
    INDICEROLEAUTEURSECONDAIRE=16
    chemainScan=""

    def __init__(self,nomDuFichier,w, afficherAuteur, afficherChamps,chemainScan ):
        self.window = w
        self.afficherAuteur = afficherAuteur
        self.afficherChamps = afficherChamps
        self.chemain = os.path.join(os.path.dirname(__file__), "Doc", str(nomDuFichier))
        self.chemainOrigine =os.path.join(os.path.dirname(__file__), "LLMOutput", str(nomDuFichier))
        self.chemainScan = os.path.join(os.path.dirname(__file__), chemainScan, str(nomDuFichier))
        self.nomDuFichier=nomDuFichier
        self.listeDesCaracteristiques = []
        self.creerLignesFormulaire()
        self.lecture(self.chemain)
        self.calculeDeLaBareCentrale()
        self.setImage()
        self.extrationDesDonnéeDuTitreDuFichier()

    def clearFormRows(self):
        for row in range(self.window.gridLayout.rowCount()):
            for col in range(1, 5):
                item = self.window.gridLayout.itemAtPosition(row, col)
                if item is not None:
                    widget = item.widget()
                    if widget is not None:
                        self.window.gridLayout.removeWidget(widget)
                        widget.deleteLater()

    def creerLignesFormulaire(self):
        self.clearFormRows()
        self.listeDesCaracteristiques = []
        for row, nom in enumerate(self.listeDesNomDeCaracteristiques):
            if nom in self.listeDesNomDeCaracteristiquesMultiple:
                caracteristique = cm.CaracteristiqueMultiple(row, nom)
            else:
                caracteristique = c.Caracteristique(row, nom)
            self.listeDesCaracteristiques.append(caracteristique)

            label = QtWidgets.QLabel(nom)
            if isinstance(caracteristique, cm.CaracteristiqueMultiple):
                field = QtWidgets.QPushButton()
                if nom == "Champ Scientifique":
                    field.clicked.connect(lambda checked, f=self: self.afficherChamps(f))
                else:
                    field.clicked.connect(lambda checked, f=self: self.afficherAuteur(f))
            else:
                field = QtWidgets.QLineEdit()

            dot = QtWidgets.QLabel("●")
            self._setDotColor(dot, caracteristique.getProba())

            edit = QtWidgets.QLineEdit("0")
            edit.setVisible(False)

            self.window.gridLayout.addWidget(label, row, 1)
            self.window.gridLayout.addWidget(field, row, 2)
            self.window.gridLayout.addWidget(dot, row, 3)
            self.window.gridLayout.addWidget(edit, row, 4)

    def __str__(self):        return f"Fiche: {self.getValeurParNom('Titre')} de {self.getValeurParNom('Auteur')} ({self.getValeurParNom('Annee')})"

    def getCaracteristiqueParNom(self, nom):
        for char in self.listeDesCaracteristiques:
            if char.isCaracteristique(nom):
                return char
        return None

    def getValeurParNom(self, nom):
        caracteristique = self.getCaracteristiqueParNom(nom)
        return caracteristique.getValeur() if caracteristique is not None else ""

    def lecture(self,page):
        print(self.chemainOrigine)
        pageL= page+".txt"
        print(f"lecture de la page: {pageL}")
        with open(pageL, "r") as f:
            for line in f:
                print(line)
                labelText, fieldText, proba, edit = line.strip().split("$")
                for caracteristique in self.listeDesCaracteristiques:
                    if caracteristique.isCaracteristique(labelText):
                        caracteristique.setValeur(fieldText)
                        caracteristique.setProba(int(proba) if proba != "None" else 0)
                        fieldItem = self.window.gridLayout.itemAtPosition(caracteristique.id, 2)
                        barItem = self.window.gridLayout.itemAtPosition(caracteristique.id, 3)
                        editItem = self.window.gridLayout.itemAtPosition(caracteristique.id, 4)

                        if fieldItem is not None:
                            widget = fieldItem.widget()
                            if isinstance(widget, QtWidgets.QPushButton):
                                widget.setText(caracteristique.getValeur())
                            else:
                                widget.setText(fieldText)
                        if barItem is not None:
                            bar = barItem.widget()
                            if isinstance(bar, QtWidgets.QLabel):
                                self._setDotColor(bar, caracteristique.getProba())
                        if editItem is not None:
                            editItem.widget().setText(edit)
                            if edit=="1":
                                   self.changeEdit(caracteristique.id)
        f.close()                         

    def changeColor(self,bar):
        value = bar.value()
        if value == 100:
            color = "cyan"
        elif value <= 30:
            color = "red"
        elif value <=50:
            color = "orange"
        elif value <= 75:
            color = "yellow"
        else:
            color = "green"
        bar.setStyleSheet("QProgressBar { border: 2px solid grey; border-radius: 5px; text-align: center; color: black;} \n QProgressBar::chunk { background-color: "+color+" ;}")


    def _setDotColor(self, widget, value):
        if value == 100:
            color = "cyan"
        elif value <= 30:
            color = "red"
        elif value <=50:
            color = "orange"
        elif value <= 75:
            color = "yellow"
        else:
            color = "green"
        if isinstance(widget, QtWidgets.QLabel):
            widget.setText("●")
            widget.setStyleSheet(f"color: {color}; font-size: 20px;")
        elif isinstance(widget, QtWidgets.QProgressBar):
            widget.setFormat("●")
            widget.setStyleSheet(f"QProgressBar {{ border: 2px solid grey; border-radius: 5px; text-align: center; color: {color}; font-size: 20px; }} QProgressBar::chunk {{ background-color: {color}; }}")
            widget.setValue(100)
            widget.setMaximum(100)
        

    def affichage(self):
        text=""
        self.nettoyerCaracteristiques()
        article = self.getValeurParNom("Article")
        titre = self.getValeurParNom("Titre")
        auteur = self.getValeurParNom("Auteur")
        complementTitre = self.getValeurParNom("Complement du titre")
        numeroVolume = self.getValeurParNom("Numero du volume")
        ville = self.getValeurParNom("Ville")
        editeur = self.getValeurParNom("Editeur")
        annee = self.getValeurParNom("Annee")
        volume = self.getValeurParNom("Volume")
        illustration = self.getValeurParNom("Illustration")
        taille = self.getValeurParNom("Taille")
        champsScientifique = self.getCaracteristiqueParNom("Champ Scientifique")
        premierAuteur = self.getValeurParNom("Premier Auteur")
        coAuteur = self.getValeurParNom("Co-Auteur")
        roleAuteur = self.getValeurParNom("Role Auteur")
        roleCoauteur = self.getValeurParNom("Role CoAuteur")
        auteurSecondaire = self.getValeurParNom("Auteur Secondaire")
        roleAuteurSecondaire = self.getValeurParNom("Role Auteur Secondaire")
        collectivite = self.getValeurParNom("Nom de la Collectivite")
        roleCollectivite = self.getValeurParNom("Role de la Collectivite")

        if article != "" or titre != "" or auteur != "" or complementTitre != "":
            text += "200 "
            if article != "":
                text += ("0#$a" + str(article) + " @" + str(titre))
            else:
                text += ("1#$a@" + str(titre))
            if auteur != "":
                text += ("$f" + str(auteur))
            if complementTitre != "":
                text += ("$e" + str(complementTitre))
            if numeroVolume != "":
                text += ("$h" + str(numeroVolume))
            text += "; "

        if  ville != "" or editeur != "":
            text += "210 ##"
            if ville != "":
                text += ("$a" + str(ville))
            if editeur != "":
                text += ("$c" + str(editeur))
            if annee != "":
                text += ("$d" + str(annee))
            text += "; "

        if ville != "" or editeur != "" or annee != "":
            text += "214 #0"
            if ville != "":
                text += ("$a" + str(ville))
            if editeur != "":
                text += ("$c" + str(editeur))
            if annee != "":
                text += ("$d" + str(annee))
            text += "; "

        if volume != "" or illustration != "" or taille != "":
            text += "215 ##"
            if volume != "":
                text += ("$a" + str(volume))
            if illustration != "":
                text += ("$c" + str(illustration))
            if taille != "":
                text += ("$d" + str(taille))
            text += "; "

        if champsScientifique is not None and champsScientifique.getValeur() != "":
            text += ("606 ##$" + str(champsScientifique.getValeurChampsScientifique()) + "; ")

        if premierAuteur != "" or roleAuteur != "":
            text += "700 "
            if premierAuteur != "":
                text += ("#1$3" + str(premierAuteur))
            if roleAuteur != "":
                text += ("$40" + str(roleAuteur))
            text += "; "

        if coAuteur != "" or roleCoauteur != "":
            text += "701 "
            if coAuteur != "":
                text += ("#1$3" + str(coAuteur))
            if roleCoauteur != "":
                text += ("$40" + str(roleCoauteur))
            text += "; "

        if auteurSecondaire != "" or roleAuteurSecondaire != "":
            text += "702 "
            if auteurSecondaire != "":
                text += ("#1$3" + str(auteurSecondaire))
            if roleAuteurSecondaire != "":
                text += ("$4" + str(roleAuteurSecondaire))
            text += "; "

        if collectivite != "" or roleCollectivite != "":
            text += "712 "
            if collectivite != "":
                text += ("02$3" + str(collectivite))
            if roleCollectivite != "":
                text += ("$4" + str(roleCollectivite))

        print(f"Affichage de la fiche: {titre} de {auteur} ({annee})")
        print(text)
        return text


    def ecriture(self):
        self.sauvgarde()
        self.exportation()

    def sauvgarde(self):
        chemaintmp=self.chemain+".txt"
        with open(chemaintmp, "w") as f:
            for i in self.listeDesCaracteristiques:
                texte = i.getValeur()
                f.write(f"{self.window.gridLayout.itemAtPosition(i.id,1).widget().text()}${texte}${i.getProba()}${self.window.gridLayout.itemAtPosition(i.id,4).widget().text()}\n")

    def exportation(self):
        chemain=os.path.join(os.path.dirname(__file__), "Sortie", str(self.nomDuFichier))
        chemain+=".txt"
        print (f"Exportation de la fiche:{chemain}")
        with open(chemain,"w") as f:
            f.write(self.affichage())

    def setImage(self):
        chemain=self.chemainScan
        chemainPNG=chemain+".png"
        chemainJPG=chemain+".jpg"
        if os.path.exists(chemainPNG):
            image = QtGui.QImage(chemainPNG)
        elif os.path.exists(chemainJPG):
            image = QtGui.QImage(chemainJPG)
        else:
            image= QtGui.QImage(os.path.join(os.path.dirname(__file__), "Image", "PasDImage.jpg"))
        scene = QtWidgets.QGraphicsScene()
        image = image.scaled((image.size()/4), QtCore.Qt.IgnoreAspectRatio, QtCore.Qt.SmoothTransformation)
        pixmap = QtGui.QPixmap.fromImage(image)
        item = QtWidgets.QGraphicsPixmapItem(pixmap)
        scene.addItem(item)
        scene.setSceneRect(pixmap.rect())
        self.window.graphicsView.setScene(scene)
        
    def zoom(self, factor):
        view = self.window.graphicsView
        view.scale(factor, factor)   

    def resetZoom(self):
        view = self.window.graphicsView
        view.resetTransform()

    def actualiserValeur(self):
        for i in self.listeDesCaracteristiques:
            fieldItem = self.window.gridLayout.itemAtPosition((i.id), 2)
            if fieldItem is not None:
                if fieldItem.widget().text() != i.getValeur():
                    i.setValeur(fieldItem.widget().text())
                    return i.id

    def changeEdit(self,i):
        print (f"Changement de l'edit de la ligne {i}")
        if i is not None:
            if self.window.gridLayout.itemAtPosition(i,4).widget().text()!="1":
                self.window.gridLayout.itemAtPosition(i,4).widget().setText("1")
                barWidget = self.window.gridLayout.itemAtPosition(i,3).widget()
                if isinstance(barWidget, QtWidgets.QLabel):
                    barWidget.setText("✓")
                    barWidget.setStyleSheet("color: cyan; font-size: 20px;")
                elif isinstance(barWidget, QtWidgets.QProgressBar):
                    barWidget.setFormat("✓")
                    barWidget.setStyleSheet("QProgressBar { border: 2px solid grey; border-radius: 5px; text-align: center; color: cyan; font-size: 20px; } QProgressBar::chunk { background-color: green; }")
                    barWidget.setValue(100)
                    barWidget.setMaximum(100)
                # Find the characteristic and set proba
                for char in self.listeDesCaracteristiques:
                    if char.id == i:
                        char.setProba(100)
                        break
                self.calculeDeLaBareCentrale()
            #utliser pour l'initialisation de la fiche, pour mettre les edits à 1 et les barres à ✓
            else:
                barWidget = self.window.gridLayout.itemAtPosition(i,3).widget()
                if isinstance(barWidget, QtWidgets.QLabel):
                    barWidget.setText("✓")
                    barWidget.setStyleSheet("color: cyan; font-size: 20px;")
        
    def updateButtons(self):
        for i in self.listeDesCaracteristiques:
            if isinstance(i, cm.CaracteristiqueMultiple):
                item = self.window.gridLayout.itemAtPosition(i.id, 2)
                if item:
                    widget = item.widget()
                    if isinstance(widget, QtWidgets.QPushButton):
                        widget.setText(i.getValeur())

    def calculeDeLaBareCentrale(self):
        total = sum(i.getProba() for i in self.listeDesCaracteristiques)
        average = total / len(self.listeDesCaracteristiques) if self.listeDesCaracteristiques else 0
        self.window.BarCentrale.setValue(average)
        self.changeColor(self.window.BarCentrale)

    def nettoyerCaracteristiques(self):
        for caracteristique in self.listeDesCaracteristiques:
            if isinstance(caracteristique, cm.CaracteristiqueMultiple):
                # Pour les caractéristiques multiples, nettoyer chaque élément de la liste
                if caracteristique.valeur:
                    caracteristique.valeur = [valeur.strip() for valeur in caracteristique.valeur if valeur.strip()]
            else:
                # Pour les caractéristiques simples, nettoyer la valeur
                if caracteristique.valeur:
                    caracteristique.valeur = caracteristique.valeur.strip()
        # Mettre à jour les boutons et les widgets après nettoyage
        self.updateButtons()
        for caracteristique in self.listeDesCaracteristiques:
            fieldItem = self.window.gridLayout.itemAtPosition(caracteristique.id, 2)
            if fieldItem is not None:
                widget = fieldItem.widget()
                if isinstance(widget, QtWidgets.QLineEdit):
                    widget.setText(caracteristique.getValeur())
                elif isinstance(widget, QtWidgets.QPushButton):
                    widget.setText(caracteristique.getValeur())

    def extrationDesDonnéeDuTitreDuFichier(self):
        # Extraction de la taille et du volume à partir du nom du fichier
        nomDuFichier = os.path.basename(self.nomDuFichier)
        nomSansExtention = os.path.splitext(nomDuFichier)[0]
        parts = nomSansExtention.split('#')
        if len(parts) == 2: # Normalement inutile, mais on le laisse en cas d'érreur lors de la saisie du nom du fichier
            taille = parts[1]
            self.getCaracteristiqueParNom("Taille").setValeur(taille)
            # Mettre à jour les widgets correspondants
            tailleWidget = self.window.gridLayout.itemAtPosition(self.getCaracteristiqueParNom("Taille").id, 2).widget()
            if isinstance(tailleWidget, QtWidgets.QLineEdit):
                tailleWidget.setText(taille)
        elif len(parts) >= 3:
            taille = parts[1]
            volume = parts[2]
            self.getCaracteristiqueParNom("Taille").setValeur(taille)
            self.getCaracteristiqueParNom("Volume").setValeur(volume)
            # Mettre à jour les widgets correspondants
            tailleWidget = self.window.gridLayout.itemAtPosition(self.getCaracteristiqueParNom("Taille").id, 2).widget()
            volumeWidget = self.window.gridLayout.itemAtPosition(self.getCaracteristiqueParNom("Volume").id, 2).widget()
            if isinstance(tailleWidget, QtWidgets.QLineEdit):
                tailleWidget.setText(taille)
            if isinstance(volumeWidget, QtWidgets.QLineEdit):
                volumeWidget.setText(volume)
        
    
def getlisteDesNomDeCaracteristiquesMultiple():
    return ["Champ Scientifique","Premier Auteur","Role Auteur","Co-Auteur","Role CoAuteur","Auteur Secondaire","Role Auteur Secondaire"]
def getlisteDesNomsDeCaracterisitiques():
    return ["Article","Titre","Auteur","Complement du titre","Numero du volume","Ville","Editeur","Annee","Volume","Illustration","Taille","Champ Scientifique","Premier Auteur","Co-Auteur","Role Auteur","Role CoAuteur","Auteur Secondaire","Role Auteur Secondaire","Nom de la Collectivite","Role de la Collectivite"]
