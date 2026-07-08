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
    listeDesNomDeCaracteristiques=["Article","Titre","Complement du titre","Auteur","Numero du volume","Collection","Ville","Editeur","Mention d'edition","Annee","Volume","Illustration","Dimension","Indexation Rameau","Premier Auteur","Co-Auteur","Role Auteur","Role CoAuteur","Auteur Secondaire","Role Auteur Secondaire","Nom de la Collectivite","Role de la Collectivite"]
    listeDesNomDeCaracteristiquesMultiple=["Indexation Rameau","Premier Auteur","Role Auteur","Co-Auteur","Role CoAuteur","Auteur Secondaire","Role Auteur Secondaire"]
    chemain=""
    nomDuFichier=""
    INDICECHAMPSCIENTIFIQUE=13
    INDICEAUTEUR=14
    INDICEROLEAUTEUR=16
    INDICECOAUTEUR=15
    INDICEROLECOAUTEUR=17
    INDICEAUTEURSECONDAIRE=18
    INDICEROLEAUTEURSECONDAIRE=19
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
        self.ajoutTitreDeLaFenetre()

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
                if nom == "Indexation Rameau":
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
        dimension = self.getValeurParNom("Dimension")
        indexationRameau = self.getCaracteristiqueParNom("Indexation Rameau")
        premierAuteur = self.getValeurParNom("Auteur Principal")
        coAuteur = self.getValeurParNom("Co-Auteur")
        fonctionAuteur = self.getValeurParNom("Fonction Auteur")
        fonctionCoauteur = self.getValeurParNom("Fonction CoAuteur")
        auteurSecondaire = self.getValeurParNom("Auteur Secondaire")
        fonctionAuteurSecondaire = self.getValeurParNom("Fonction Auteur Secondaire")
        collectivite = self.getValeurParNom("Nom de la Collectivite")
        fonctionCollectivite = self.getValeurParNom("Fonction de la Collectivite")

        if article != "" or titre != "" or auteur != "" or complementTitre != "":
            text += "200 "
            if article != "":
                text += ("0#$a" + str(article) + " @" + str(titre))
            else:
                text += ("1#$a@" + str(titre))
            if auteur != "":
                text += ("$f" + str(auteur))
                if coAuteur != "":
                    text += ("," + str(coAuteur))
                if auteurSecondaire != "":
                    text += ("," + str(auteurSecondaire))
            if complementTitre != "":
                text += ("$e" + str(complementTitre))
            if numeroVolume != "":
                text += ("$h" + str(numeroVolume))
            text += ";\n"

        if ville != "" or editeur != "" or annee != "":
            text += "214 #0"
            if ville != "":
                text += ("$a" + str(ville))
            if editeur != "":
                text += ("$c" + str(editeur))
            if annee != "":
                text += ("$d" + str(annee))
            text += ";\n"

        if volume != "" or illustration != "" or dimension != "":
            text += "215 ##"
            if volume != "":
                text += ("$a" + str(volume))
            if illustration != "":
                text += ("$c" + str(illustration))
            if dimension != "":
                text += ("$d" + str(dimension))
            text += ";\n"

        if indexationRameau is not None and indexationRameau.getValeur() != "":
            text += ("606 ##$" + str(indexationRameau.getValeurIndexationRameau()) + ";\n ")

        if premierAuteur != "" or fonctionAuteur != "":
            text += "700 "
            if premierAuteur != "":
                text += ("#1$3" + str(premierAuteur))
            if fonctionAuteur != "":
                text += ("$40" + str(fonctionAuteur))
            text += ";\n"

        if coAuteur != "" or fonctionCoauteur != "":
            text += "701 "
            if coAuteur != "":
                text += ("#1$3" + str(coAuteur))
            if fonctionCoauteur != "":
                text += ("$40" + str(fonctionCoauteur))
            text += ";\n"

        if auteurSecondaire != "" or fonctionAuteurSecondaire != "":
            text += "702 "
            if auteurSecondaire != "":
                text += ("#1$3" + str(auteurSecondaire))
            if fonctionAuteurSecondaire != "":
                text += ("$4" + str(fonctionAuteurSecondaire))
            text += ";\n"

        if collectivite != "" or fonctionCollectivite != "":
            text += "712 "
            if collectivite != "":
                text += ("02$3" + str(collectivite))
            if fonctionCollectivite != "":
                text += ("$4" + str(fonctionCollectivite))
        text = self._retirerLeDernierPointVigule(text)
        print(f"Affichage de la fiche: {titre} de {auteur} ({annee})")
        print(text)
        return text

    def _retirerLeDernierPointVigule(self,text):
        while text.endswith("\n") or text.endswith(" "):
            text = text[:-1]
        if text.endswith(";"):
            return text[:-1]
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
            image= QtGui.QImage(os.path.join(os.path.dirname(__file__), "Image", "PasDImage.png"))
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
                if caracteristique.valeur:
                    caracteristique.setValeur(caracteristique.valeur)
            else:
                if isinstance(caracteristique.valeur, (list, tuple, set)):
                    caracteristique.setValeur(caracteristique.valeur)
                elif isinstance(caracteristique.valeur, str):
                    caracteristique.setValeur(caracteristique.valeur.strip())
        self.updateButtons()
        for caracteristique in self.listeDesCaracteristiques:
            fieldItem = self.window.gridLayout.itemAtPosition(caracteristique.id, 2)
            if fieldItem is not None:
                widget = fieldItem.widget()
                valeur = caracteristique.getValeur()
                if isinstance(widget, QtWidgets.QLineEdit):
                    widget.setText(valeur)
                elif isinstance(widget, QtWidgets.QPushButton):
                    widget.setText(valeur)

    def extrationDesDonnéeDuTitreDuFichier(self):
        # Extraction de la Dimension et du volume à partir du nom du fichier
        nomDuFichier = os.path.basename(self.nomDuFichier)
        nomSansExtention = os.path.splitext(nomDuFichier)[0]
        parts = nomSansExtention.split('#')
        if len(parts) == 2: # Normalement inutile, mais on le laisse en cas d'érreur lors de la saisie du nom du fichier
            Dimension = parts[1]
            self.getCaracteristiqueParNom("Dimension").setValeur(Dimension)
            # Mettre à jour les widgets correspondants
            DimensionWidget = self.window.gridLayout.itemAtPosition(self.getCaracteristiqueParNom("Dimension").id, 2).widget()
            if isinstance(DimensionWidget, QtWidgets.QLineEdit):
                DimensionWidget.setText(Dimension)
            self.changeEdit(self.getCaracteristiqueParNom("Dimension").id)
            
        elif len(parts) >= 3:
            Dimension = parts[1]
            volume = parts[2]
            self.getCaracteristiqueParNom("Dimension").setValeur(Dimension)
            self.getCaracteristiqueParNom("Volume").setValeur(volume)
            # Mettre à jour les widgets correspondants
            DimensionWidget = self.window.gridLayout.itemAtPosition(self.getCaracteristiqueParNom("Dimension").id, 2).widget()
            volumeWidget = self.window.gridLayout.itemAtPosition(self.getCaracteristiqueParNom("Volume").id, 2).widget()
            if isinstance(DimensionWidget, QtWidgets.QLineEdit):
                DimensionWidget.setText(Dimension)
                self.changeEdit(self.getCaracteristiqueParNom("Dimension").id)
            if isinstance(volumeWidget, QtWidgets.QLineEdit):
                volumeWidget.setText(volume)
                self.changeEdit(self.getCaracteristiqueParNom("Volume").id)

    def ajoutTitreDeLaFenetre(self):
        self.window.setWindowTitle(self.nomDuFichier)
        self.window.BoutonTitre.setText(self.nomDuFichier)
    
    def copieFileName(self):
        clipboard = QtWidgets.QApplication.clipboard()
        clipboard.setText(self.nomDuFichier)
        print(f"Nom du fichier copié dans le presse-papiers: {self.nomDuFichier}")
        
    
def getListeDesNomDeCaracteristiquesMultiple():
    return ["Indexation Rameau","Premier Auteur","Role Auteur","Co-Auteur","Role CoAuteur","Auteur Secondaire","Role Auteur Secondaire"]
def getListeDesNomsDeCaracterisitiques():
    return ["Article","Titre","Complement du titre","Auteur","Numero du volume","Collection","Ville","Editeur","Mention d'edition","Annee","Volume","Illustration","Dimension","Indexation Rameau","Premier Auteur","Co-Auteur","Role Auteur","Role CoAuteur","Auteur Secondaire","Role Auteur Secondaire","Nom de la Collectivite","Role de la Collectivite"]
