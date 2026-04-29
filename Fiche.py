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
    listeDesNom=["Article","Titre","Auteur","Complement du titre","Numero du volume","Ville","Editeur","Annee","Illustration","Taille","Champ Scientifique","Premier Auteur","Co-Auteur","Role Auteur","Role CoAuteur","Auteur Secondaire","Role Auteur Secondaire","Nom de la Collectivite","Role de la Collectivite"]
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

    def __init__(self,nomDuFichier,w, afficherAuteur, afficherChamps):
        self.window = w
        self.afficherAuteur = afficherAuteur
        self.afficherChamps = afficherChamps
        self.chemain = os.path.join(os.path.dirname(__file__), "Doc", str(nomDuFichier))
        self.chemainOrigine =os.path.join(os.path.dirname(__file__), "LLMOutput", str(nomDuFichier))
        self.nomDuFichier=nomDuFichier
        self.listeDesCaracteristiques = []
        ligne_index = [0, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19]
        for row, nom in zip(ligne_index, self.listeDesNom):
            #print(nom+ str(nom in self.listeDesCaracteristiquesMultiple))
            if nom in self.listeDesCaracteristiquesMultiple:
                 self.listeDesCaracteristiques.append(cm.CaracteristiqueMultiple(row, nom))
            else:
                self.listeDesCaracteristiques.append(c.Caracteristique(row, nom))
        # Replace QLineEdit with QPushButton for multiple characteristics
        for i in self.listeDesCaracteristiques:
            if isinstance(i, cm.CaracteristiqueMultiple):
                item = self.window.gridLayout.itemAtPosition(i.id, 2)
                if item:
                    widget = item.widget()
                    self.window.gridLayout.removeWidget(widget)
                    widget.deleteLater()
                    button = QtWidgets.QPushButton()
                    self.window.gridLayout.addWidget(button, i.id, 2)
                    if i.nom == "Champ Scientifique":
                        button.clicked.connect(lambda checked, f=self: self.afficherChamps(f))
                    else:
                        button.clicked.connect(lambda checked, f=self: self.afficherAuteur(f))
        # Replace QProgressBar with QLabel for dots
        for i in self.listeDesCaracteristiques:
            item = self.window.gridLayout.itemAtPosition(i.id, 3)
            if item:
                widget = item.widget()
                if isinstance(widget, QtWidgets.QProgressBar):
                    self.window.gridLayout.removeWidget(widget)
                    widget.deleteLater()
                    label = QtWidgets.QLabel("●")
                    self.window.gridLayout.addWidget(label, i.id, 3)
                    self.set_dot_color(label, i.getProba())
        # cache "edit"
        for i in self.listeDesCaracteristiques:
            edit_item = self.window.gridLayout.itemAtPosition(i.id, 4)
            if edit_item is not None:
                edit_widget = edit_item.widget()
                try:
                    edit_widget.hide()
                except Exception:
                    # If hide is not available, set invisible
                    edit_widget.setVisible(False)
        self.lecture(self.chemain)
        self.calculeDeLaBareCentrale()
        self.setImage()

    def __str__(self):        return f"Fiche: {self.listeDesCaracteristiques[1].getValeur()} de {self.listeDesCaracteristiques[2].getValeur()} ({self.listeDesCaracteristiques[7].getValeur()})"

    def lecture(self,page):
        print(self.chemainOrigine)
        pageL= page+".txt"
        print(f"lecture de la page: {pageL}")
        with open(pageL, "r") as f:
            for line in f:
                label_text, field_text, proba, edit = line.strip().split(":")
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
        if ((self.listeDesCaracteristiques[0].getValeur()!="") or (self.listeDesCaracteristiques[1].getValeur()!="") or (self.listeDesCaracteristiques[2].getValeur()!="")or(self.listeDesCaracteristiques[3].getValeur()!="")):
            text+="200 "
            if self.listeDesCaracteristiques[0].getValeur()!="":
                text+=("0#$a"+str(self.listeDesCaracteristiques[0].getValeur())+" @"+str(self.listeDesCaracteristiques[1].getValeur()))
            else:
                text+=("1#$a"+str(self.listeDesCaracteristiques[1].getValeur()))
            if self.listeDesCaracteristiques[2].getValeur()!="":
                text+=("$f"+str(self.listeDesCaracteristiques[2].getValeur()))
            if self.listeDesCaracteristiques[3].getValeur()!="":
                text+=("$e"+str(self.listeDesCaracteristiques[3].getValeur()))
            text+="; "
        if ((self.listeDesCaracteristiques[4].getValeur()!="") or (self.listeDesCaracteristiques[5].getValeur()!="") or (self.listeDesCaracteristiques[6].getValeur()!="")):
            text+=("210 ##")
            if self.listeDesCaracteristiques[4].getValeur()!="":
                text+=("$a"+str(self.listeDesCaracteristiques[4].getValeur()))
            if self.listeDesCaracteristiques[5].getValeur()!="":
                text+=("$c"+str(self.listeDesCaracteristiques[5].getValeur()))
            if self.listeDesCaracteristiques[6].getValeur()!="":
                text+=("$d"+str(self.listeDesCaracteristiques[6].getValeur()))
            text+="; "
        if ((self.listeDesCaracteristiques[4].getValeur()!="") or (self.listeDesCaracteristiques[5].getValeur()!="") or (self.listeDesCaracteristiques[6].getValeur()!="")):
            text+=("214 ##")
            if self.listeDesCaracteristiques[4].getValeur()!="":
                text+=("$a"+str(self.listeDesCaracteristiques[4].getValeur()))
            if self.listeDesCaracteristiques[5].getValeur()!="":
                text+=("$c"+str(self.listeDesCaracteristiques[5].getValeur()))
            if self.listeDesCaracteristiques[6].getValeur()!="":
                text+=("$d"+str(self.listeDesCaracteristiques[6].getValeur()))
            text+="; "
        if ((self.listeDesCaracteristiques[7].getValeur()!="") or (self.listeDesCaracteristiques[8].getValeur()!="")or (self.listeDesCaracteristiques[9].getValeur()!="")):
            text+="215 ##"
            if self.listeDesCaracteristiques[7].getValeur()!="":
                text+=("$a"+str(self.listeDesCaracteristiques[7].getValeur()))
            if self.listeDesCaracteristiques[8].getValeur()!="":
                text+=("$c"+str(self.listeDesCaracteristiques[8].getValeur()))
            if self.listeDesCaracteristiques[9].getValeur()!="":
                text+=("$d"+str(self.listeDesCaracteristiques[9].getValeur()))
            text+="; "
        if self.listeDesCaracteristiques[10].getValeur()!="":
            text+=("606 ##$"+str(self.listeDesCaracteristiques[10].getValeurChampsScientifique())+"; ")
        if ((self.listeDesCaracteristiques[11].getValeur()!="")or(self.listeDesCaracteristiques[13].getValeur()!="")):
            text+="700 "
            if self.listeDesCaracteristiques[11].getValeur()!="":
                text+=("#1$3"+str(self.listeDesCaracteristiques[11].getValeur()))
            if self.listeDesCaracteristiques[13].getValeur()!="":
                text+=("$40"+str(self.listeDesCaracteristiques[13].getValeur()))
            text+="; "
        if ((self.listeDesCaracteristiques[12].getValeur()!="")or(self.listeDesCaracteristiques[14].getValeur()!="")):
            text+="701 "
            if self.listeDesCaracteristiques[12].getValeur()!="":
                text+=("#1$3"+str(self.listeDesCaracteristiques[12].getValeur()))
            if self.listeDesCaracteristiques[14].getValeur()!="":
                text+=("$40"+str(self.listeDesCaracteristiques[14].getValeur()))
            text+="; "
        if ((self.listeDesCaracteristiques[15].getValeur()!="")or(self.listeDesCaracteristiques[16].getValeur()!="")):
            text+="702 "
            if self.listeDesCaracteristiques[15].getValeur()!="":
                text+=("#1$3"+str(self.listeDesCaracteristiques[15].getValeur()))
            if self.listeDesCaracteristiques[16].getValeur()!="":
                text+=("$4"+str(self.listeDesCaracteristiques[16].getValeur()))
            text+="; "
        if ((self.listeDesCaracteristiques[17].getValeur()!="")or(self.listeDesCaracteristiques[18].getValeur()!="")):
            text+="712 "
            if self.listeDesCaracteristiques[17].getValeur()!="":
                text+=("02$3"+str(self.listeDesCaracteristiques[17].getValeur()))
            if self.listeDesCaracteristiques[18].getValeur()!="":
                text+=("$4"+str(self.listeDesCaracteristiques[18].getValeur()))
        print(f"Affichage de la fiche: {self.listeDesCaracteristiques[1].getValeur()} de {self.listeDesCaracteristiques[2].getValeur()} ({self.listeDesCaracteristiques[7].getValeur()})")
        print (text)
        return text


    def ecriture(self):
        self.sauvgarde()
        self.exportation()

    def sauvgarde(self):
        chemaintmp=self.chemain+".txt"
        with open(chemaintmp, "w") as f:
            for i in self.listeDesCaracteristiques:
                texte = i.getValeur()
                f.write(f"{self.window.gridLayout.itemAtPosition(i.id,1).widget().text()}:{texte}:{i.getProba()}:{self.window.gridLayout.itemAtPosition(i.id,4).widget().text()}\n")

    def exportation(self):
        chemain=os.path.join(os.path.dirname(__file__), "Sortie", str(self.nomDuFichier))
        chemain+=".txt"
        print (f"Exportation de la fiche:{chemain}")
        with open(chemain,"w") as f:
            f.write(self.affichage())

    def setImage(self):
        chemain=os.path.join(os.path.dirname(__file__), "Scan", str(self.nomDuFichier))
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
    
    

def getlisteDesNoms():
    return ["Article","Titre","Auteur","Complement du titre","Numero du volume","Ville","Editeur","Annee","Illustration","Taille","Champ Scientifique","Premier Auteur","Co-Auteur","Role Auteur","Role CoAuteur","Auteur Secondaire","Role Auteur Secondaire","Nom de la Collectivite","Role de la Collectivite"]
