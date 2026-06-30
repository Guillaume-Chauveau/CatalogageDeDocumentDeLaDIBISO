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
    listeDesNom=["Article","Titre","Auteur","Complement du titre","Numero du volume","Ville","Editeur","Annee","Volume","Illustration","Taille","Champ Scientifique","Premier Auteur","Co-Auteur","Role Auteur","Role CoAuteur","Auteur Secondaire","Role Auteur Secondaire","Nom de la Collectivite","Role de la Collectivite"]
    listeDesCaracteristiquesMultiple=["Champ Scientifique","Premier Auteur","Role Auteur","Co-Auteur","Role CoAuteur","Auteur Secondaire","Role Auteur Secondaire"]
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
        for row, nom in enumerate(self.listeDesNom):
            if nom in self.listeDesCaracteristiquesMultiple:
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
            self.set_dot_color(dot, caracteristique.getProba())

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
                label_text, field_text, proba, edit = line.strip().split("$")
                for i in self.listeDesCaracteristiques:
                    if i.isCaracteristique(label_text):
                        i.setValeur(field_text)
                        i.setProba(int(proba) if proba != "None" else 0)
                        field_item = self.window.gridLayout.itemAtPosition(i.id, 2)
                        bar_item = self.window.gridLayout.itemAtPosition(i.id, 3)
                        edit_item = self.window.gridLayout.itemAtPosition(i.id, 4)

                        if field_item is not None:
                            widget = field_item.widget()
                            if isinstance(widget, QtWidgets.QPushButton):
                                widget.setText(i.getValeur())
                            else:
                                widget.setText(field_text)
                        if bar_item is not None:
                            bar = bar_item.widget()
                            if isinstance(bar, QtWidgets.QLabel):
                                self.set_dot_color(bar, i.getProba())
                        if edit_item is not None:
                            edit_item.widget().setText(edit)
                            if edit=="1":
                                   self.change_edit(i.id)
        f.close()                         

    def change_color(self,bar):
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


    def set_dot_color(self, widget, value):
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
        complement_titre = self.getValeurParNom("Complement du titre")
        numero_volume = self.getValeurParNom("Numero du volume")
        ville = self.getValeurParNom("Ville")
        editeur = self.getValeurParNom("Editeur")
        annee = self.getValeurParNom("Annee")
        volume = self.getValeurParNom("Volume")
        illustration = self.getValeurParNom("Illustration")
        taille = self.getValeurParNom("Taille")
        champs_scientifique = self.getCaracteristiqueParNom("Champ Scientifique")
        premier_auteur = self.getValeurParNom("Premier Auteur")
        coauteur = self.getValeurParNom("Co-Auteur")
        role_auteur = self.getValeurParNom("Role Auteur")
        role_coauteur = self.getValeurParNom("Role CoAuteur")
        auteur_secondaire = self.getValeurParNom("Auteur Secondaire")
        role_auteur_secondaire = self.getValeurParNom("Role Auteur Secondaire")
        collectivite = self.getValeurParNom("Nom de la Collectivite")
        role_collectivite = self.getValeurParNom("Role de la Collectivite")

        if article != "" or titre != "" or auteur != "" or complement_titre != "":
            text += "200 "
            if article != "":
                text += ("0#$a" + str(article) + " @" + str(titre))
            else:
                text += ("1#$a@" + str(titre))
            if auteur != "":
                text += ("$f" + str(auteur))
            if complement_titre != "":
                text += ("$e" + str(complement_titre))
            if numero_volume != "":
                text += ("$h" + str(numero_volume))
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

        if champs_scientifique is not None and champs_scientifique.getValeur() != "":
            text += ("606 ##$" + str(champs_scientifique.getValeurChampsScientifique()) + "; ")

        if premier_auteur != "" or role_auteur != "":
            text += "700 "
            if premier_auteur != "":
                text += ("#1$3" + str(premier_auteur))
            if role_auteur != "":
                text += ("$40" + str(role_auteur))
            text += "; "

        if coauteur != "" or role_coauteur != "":
            text += "701 "
            if coauteur != "":
                text += ("#1$3" + str(coauteur))
            if role_coauteur != "":
                text += ("$40" + str(role_coauteur))
            text += "; "

        if auteur_secondaire != "" or role_auteur_secondaire != "":
            text += "702 "
            if auteur_secondaire != "":
                text += ("#1$3" + str(auteur_secondaire))
            if role_auteur_secondaire != "":
                text += ("$4" + str(role_auteur_secondaire))
            text += "; "

        if collectivite != "" or role_collectivite != "":
            text += "712 "
            if collectivite != "":
                text += ("02$3" + str(collectivite))
            if role_collectivite != "":
                text += ("$4" + str(role_collectivite))

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

    def reset_zoom(self):
        view = self.window.graphicsView
        view.resetTransform()

    def actualiserValeur(self):
        for i in self.listeDesCaracteristiques:
            #print(f"Actualisation de la valeur de la ligne {i.id} : {i.getValeur()}")
            field_item = self.window.gridLayout.itemAtPosition((i.id), 2)
            #print(field_item)
            if field_item is not None:
                if field_item.widget().text() != i.getValeur():
                    i.setValeur(field_item.widget().text())
                    return i.id

    def change_edit(self,i):
        print (f"Changement de l'edit de la ligne {i}")
        if i is not None:
            if self.window.gridLayout.itemAtPosition(i,4).widget().text()!="1":
                self.window.gridLayout.itemAtPosition(i,4).widget().setText("1")
                bar_widget = self.window.gridLayout.itemAtPosition(i,3).widget()
                if isinstance(bar_widget, QtWidgets.QLabel):
                    bar_widget.setText("✓")
                    bar_widget.setStyleSheet("color: cyan; font-size: 20px;")
                elif isinstance(bar_widget, QtWidgets.QProgressBar):
                    bar_widget.setFormat("✓")
                    bar_widget.setStyleSheet("QProgressBar { border: 2px solid grey; border-radius: 5px; text-align: center; color: cyan; font-size: 20px; } QProgressBar::chunk { background-color: green; }")
                    bar_widget.setValue(100)
                    bar_widget.setMaximum(100)
                # Find the characteristic and set proba
                for char in self.listeDesCaracteristiques:
                    if char.id == i:
                        char.setProba(100)
                        break
                self.calculeDeLaBareCentrale()
            #utliser pour l'initialisation de la fiche, pour mettre les edits à 1 et les barres à ✓
            else:
                bar_widget = self.window.gridLayout.itemAtPosition(i,3).widget()
                if isinstance(bar_widget, QtWidgets.QLabel):
                    bar_widget.setText("✓")
                    bar_widget.setStyleSheet("color: cyan; font-size: 20px;")
        
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
        self.change_color(self.window.BarCentrale)

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
            field_item = self.window.gridLayout.itemAtPosition(caracteristique.id, 2)
            if field_item is not None:
                widget = field_item.widget()
                if isinstance(widget, QtWidgets.QLineEdit):
                    widget.setText(caracteristique.getValeur())
                elif isinstance(widget, QtWidgets.QPushButton):
                    widget.setText(caracteristique.getValeur())
    
    
def getlisteDesCaracteristiquesMultiple():
    return ["Champ Scientifique","Premier Auteur","Role Auteur","Co-Auteur","Role CoAuteur","Auteur Secondaire","Role Auteur Secondaire"]
def getlisteDesNoms():
    return ["Article","Titre","Auteur","Complement du titre","Numero du volume","Ville","Editeur","Annee","Volume","Illustration","Taille","Champ Scientifique","Premier Auteur","Co-Auteur","Role Auteur","Role CoAuteur","Auteur Secondaire","Role Auteur Secondaire","Nom de la Collectivite","Role de la Collectivite"]
