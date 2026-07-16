import sys
from PySide6 import QtWidgets
from PySide6.QtUiTools import QUiLoader
from PySide6 import QtGui, QtWidgets
from PySide6 import QtCore
import os
import unicodedata

import Caracteristique as c
import CaracteristiqueMultiple as cm


def get_app_dir():
    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        return os.path.abspath(sys._MEIPASS)
    return os.path.dirname(os.path.abspath(__file__))


APP_DIR = get_app_dir()


class Fiche:
    window=None
    listeDesCaracteristiques=[]
    listeDesNomDeCaracteristiques=["Article","Titre","Complement du titre","Auteur","Numero du volume","Collection","Ville","Editeur","Mention d'edition","Annee","Volume","Illustration","Dimension","Indexation Rameau","Premier Auteur","Co-Auteur","Role Auteur","Role CoAuteur","Auteur Secondaire","Role Auteur Secondaire","Nom de la Collectivite","Role de la Collectivite"]
    listeDesNomDeCaracteristiquesMultiple=["Indexation Rameau","Premier Auteur","Role Auteur","Co-Auteur","Role CoAuteur","Auteur Secondaire","Role Auteur Secondaire","Collection"]
    chemain=""
    nomDuFichier=""
    INDICECHAMPSCIENTIFIQUE=13
    INDICEAUTEUR=14
    INDICEROLEAUTEUR=16
    INDICECOAUTEUR=15
    INDICEROLECOAUTEUR=17
    INDICEAUTEURSECONDAIRE=18
    INDICEROLEAUTEURSECONDAIRE=19
    INDICECOLLECTION=5
    chemainScan=""

    def __init__(self, nomDuFichier, w, afficherAuteur, afficherChamps, afficherCollection, chemainScan):
        self.window = w
        self.afficherAuteur = afficherAuteur
        self.afficherChamps = afficherChamps
        self.afficherCollection = afficherCollection
        self.chemain = os.path.join(APP_DIR, "Doc", str(nomDuFichier))
        self.chemainOrigine = os.path.join(APP_DIR, "LLMOutput", str(nomDuFichier))
        self.chemainScan = os.path.join(APP_DIR, chemainScan, str(nomDuFichier))
        self.nomDuFichier = nomDuFichier
        self.formulaireCollection = None
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
                elif nom == "Collection":
                    field.clicked.connect(lambda checked, f=self: self.afficherCollection(f))
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
    def getValeursFormulaireCollection(self):
        form = getattr(self, "formulaireCollection", None)
        if form is not None and hasattr(form, "getValeurs"):
            return form.getValeurs()
        return ""

    @staticmethod
    def _parseProba(proba):
        """
        Convertit la confiance lue dans le .txt (format produit par
        convert_json_to_txt4.py : float sur l'échelle 0-1, ex. '0.8734',
        ou chaîne vide si aucune confiance n'a été calculée) en un entier
        0-100 utilisable par les widgets (dot / progress bar).
        """
        if proba is None or proba == "" or proba == "None":
            return 0
        try:
            valeur = float(proba)
        except ValueError:
            return 0
        # Les scores viennent en 0-1 (fmt_confidence), mais on tolère aussi
        # une valeur déjà en 0-100 (ex. ancien format, ou "100").
        if valeur <= 1:
            valeur *= 100
        return round(valeur)

    def lecture(self,page):
        print(self.chemainOrigine)
        pageL= page+".txt"
        print(f"lecture de la page: {pageL}")
        source_path = os.path.join(APP_DIR, "Doc", pageL)
        if not os.path.exists(source_path):
            source_path = os.path.join(APP_DIR, "LLMOutput", pageL)
        with open(source_path, "r", encoding="utf-8") as f:
            for line in f:
                print(line)
                labelText, fieldText, proba, edit = line.strip().split("$")
                for caracteristique in self.listeDesCaracteristiques:
                    if caracteristique.isCaracteristique(labelText):
                        caracteristique.setValeur(fieldText)
                        caracteristique.setProba(self._parseProba(proba))
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
                if labelText == "Traducteur":
                    self.listeDesCaracteristiques[self.INDICEAUTEURSECONDAIRE].valeur.append(fieldText)
                    self.listeDesCaracteristiques[self.INDICEROLEAUTEURSECONDAIRE].valeur.append("Traducteur")
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
        text = ""
        self.nettoyerCaracteristiques()

        article = self._majusculeEnDebutDeCaracteristique(self.getValeurParNom("Article"))
        titre = self._majusculeEnDebutDeCaracteristique(self.getValeurParNom("Titre"))
        auteur = self._majusculeEnDebutDeCaracteristique(self.getValeurParNom("Auteur"))
        complementTitre = self._majusculeEnDebutDeCaracteristique(self.getValeurParNom("Complement du titre"))
        numeroVolume = self._majusculeEnDebutDeCaracteristique(self.getValeurParNom("Numero du volume"))
        ville = self._majusculeEnDebutDeCaracteristique(self.getValeurParNom("Ville"))
        editeur = self._majusculeEnDebutDeCaracteristique(self.getValeurParNom("Editeur"))
        annee = self._majusculeEnDebutDeCaracteristique(self.getValeurParNom("Annee"))
        volume = self._majusculeEnDebutDeCaracteristique(self.getValeurParNom("Volume"))
        illustration = self._majusculeEnDebutDeCaracteristique(self.getValeurParNom("Illustration"))
        dimension = self._majusculeEnDebutDeCaracteristique(self.getValeurParNom("Dimension"))
        indexationRameau =self.getCaracteristiqueParNom("Indexation Rameau")
        premierAuteur = self.listeDesCaracteristiques[self.INDICEAUTEUR].valeur
        print("teste premierAuteur:", premierAuteur)
        coAuteur = self.listeDesCaracteristiques[self.INDICECOAUTEUR].valeur
        fonctionAuteur = self.listeDesCaracteristiques[self.INDICEROLEAUTEUR].valeur
        fonctionCoauteur = self.listeDesCaracteristiques[self.INDICEROLECOAUTEUR].valeur
        auteurSecondaire = self.listeDesCaracteristiques[self.INDICEAUTEURSECONDAIRE].valeur
        fonctionAuteurSecondaire = self.listeDesCaracteristiques[self.INDICEROLEAUTEURSECONDAIRE].valeur
        collectivite = self._majusculeEnDebutDeCaracteristique(self.getValeurParNom("Nom de la Collectivite"))
        fonctionCollectivite = self._majusculeEnDebutDeCaracteristique(self.getValeurParNom("Fonction de la Collectivite"))
        mentionEdition = self._majusculeEnDebutDeCaracteristique(self.getValeurParNom("Mention d'edition"))

        valeursCollection = self.getValeursFormulaireCollection()
        articleFormulaireCollection = self._majusculeEnDebutDeCaracteristique(valeursCollection.split("|")[0])
        collection = self._majusculeEnDebutDeCaracteristique(valeursCollection.split("|")[1])
        section = self._majusculeEnDebutDeCaracteristique(valeursCollection.split("|")[2])
        reference = self._majusculeEnDebutDeCaracteristique(valeursCollection.split("|")[3])
        print(f"Valeurs du formulaire collection: {valeursCollection}")

        text="008 $aAax3\n104 ##$ak$bzy$cy$dba$ffre\n106 ##$ar\n181 ##$P01$ctxt\n182 ##$P01$cn\n183 ##$P01$anga\n"

        if article != "" or titre != "" or auteur != "" or complementTitre != "":
            text +=self._champs200(article, titre, auteur, complementTitre, numeroVolume, coAuteur, auteurSecondaire)

        if mentionEdition != "":
            text += "205 ##" + mentionEdition + "\n"

        if ville != "" or editeur != "" or annee != "":
            text += self._formatagePourVilleEditeurAnnee(ville, editeur, annee)
            text += "\n"

        if volume != "" or illustration != "" or dimension != "":
            text += self._champs215(volume, illustration, dimension)

        if collection or section:
            text += self._champs225(collection, section)
        if reference:
            text += f"410 ##$0@{reference}\n"
        if indexationRameau is not None and indexationRameau.getValeur() != "":
            text += ("606 ##$" + str(indexationRameau.getValeurIndexationRameau()) + "\n ")

        if premierAuteur != "" or fonctionAuteur != "":
            text +=self._champs700(premierAuteur, fonctionAuteur)

        if coAuteur != "" or fonctionCoauteur != "":
            text += self._champs701(coAuteur, fonctionCoauteur)

        if auteurSecondaire != "" or fonctionAuteurSecondaire != "":
            text += self._champs702(auteurSecondaire, fonctionAuteurSecondaire)

        if collectivite != "" or fonctionCollectivite != "":
            text += self._champs712(collectivite, fonctionCollectivite)
        #text = self._retirerLeDernierPointVigule(text)
        print(f"Affichage de la fiche: {titre} de {auteur} ({annee})")
        print(text)
        return text

    def _decouperMorceaux(self, *valeurs):
        morceauxParValeur = []
        for valeur in valeurs:
            if valeur is None:
                morceauxParValeur.append([])
            elif isinstance(valeur, (list, tuple, set)):
                morceauxParValeur.append([str(v).strip() for v in valeur if str(v).strip()])
            else:
                texte = str(valeur)
                morceauxParValeur.append([part.strip() for part in texte.split(";") if part.strip()])
        return morceauxParValeur

    def _champs712(self, collectivite, fonctionCollectivite):
        collectivite_morceaux, fonction_morceaux = self._decouperMorceaux(collectivite, fonctionCollectivite)
        resultats = []
        max_len = max([len(collectivite_morceaux), len(fonction_morceaux), 0])
        for i in range(max_len):
            text = "712 "
            if i < len(collectivite_morceaux) and collectivite_morceaux[i] != "":
                text += ("02$3" + str(collectivite_morceaux[i]))
            if i < len(fonction_morceaux) and fonction_morceaux[i] != "":
                text += ("$4" + str(fonction_morceaux[i]))
            if text != "712 ":
                resultats.append(text)
        return "\n".join(resultats)+"\n"

    def _champs702(self, auteurSecondaire, fonctionAuteurSecondaire):
        auteur_secondaire_morceaux, fonction_morceaux = self._decouperMorceaux(auteurSecondaire, fonctionAuteurSecondaire)
        resultats = []
        max_len = max([len(auteur_secondaire_morceaux), len(fonction_morceaux), 0])
        for i in range(max_len):
            text = "702 "
            if i < len(auteur_secondaire_morceaux) and auteur_secondaire_morceaux[i] != "":
                text += ("#1$3" + str(auteur_secondaire_morceaux[i]))
            if i < len(fonction_morceaux) and fonction_morceaux[i] != "":
                text += ("$4" + str(fonction_morceaux[i]))
            if text != "702 ":
                resultats.append(text)
        return "\n".join(resultats)+"\n"
    
    def _champs701(self, coAuteur, fonctionCoauteur):
        co_auteur_morceaux, fonction_morceaux = self._decouperMorceaux(coAuteur, fonctionCoauteur)
        resultats = []
        max_len = max([len(co_auteur_morceaux), len(fonction_morceaux), 0])
        for i in range(max_len):
            text = "701 "
            if i < len(co_auteur_morceaux) and co_auteur_morceaux[i] != "":
                text += ("#1$3" + str(co_auteur_morceaux[i]))
            if i < len(fonction_morceaux) and fonction_morceaux[i] != "":
                text += ("$4" + str(fonction_morceaux[i]))
            if text != "701 ":
                resultats.append(text)
        return "\n".join(resultats)+"\n"

    def _champs700(self, premierAuteur, fonctionAuteur):
        premier_auteur_morceaux, fonction_morceaux = self._decouperMorceaux(premierAuteur, fonctionAuteur)
        resultats = []
        max_len = max([len(premier_auteur_morceaux), len(fonction_morceaux), 0])
        for i in range(max_len):
            text = "700 "
            if i < len(premier_auteur_morceaux) and premier_auteur_morceaux[i] != "":
                text += ("#1$3" + str(premier_auteur_morceaux[i]))
            if i < len(fonction_morceaux) and fonction_morceaux[i] != "":
                text += ("$4" + str(fonction_morceaux[i]))
            if text != "700 ":
                resultats.append(text)
        return "\n".join(resultats)+"\n"
    
    def _champs225(self, collection, section):
        collection_morceaux, section_morceaux = self._decouperMorceaux(collection, section)
        resultats = []
        max_len = max([len(collection_morceaux), len(section_morceaux), 0])
        for i in range(max_len):
            text = "225 2#"
            if i < len(collection_morceaux) and collection_morceaux[i] != "":
                text += f"$a@{collection_morceaux[i]}"
            if i < len(section_morceaux) and section_morceaux[i] != "":
                text += f"$i{section_morceaux[i]}"
            if text != "225 2#":
                resultats.append(text)
        return "\n".join(resultats)+"\n"

    def _champs215(self, volume, illustration, dimension):
        volume_morceaux, illustration_morceaux, dimension_morceaux = self._decouperMorceaux(volume, illustration, dimension)
        resultats = []
        max_len = max([len(volume_morceaux), len(illustration_morceaux), len(dimension_morceaux), 0])
        for i in range(max_len):
            text = "215 ##"
            if i < len(volume_morceaux) and volume_morceaux[i] != "":
                text += ("$a" + str(volume_morceaux[i]))
            if i < len(illustration_morceaux) and illustration_morceaux[i] != "":
                text += ("$c" + str(illustration_morceaux[i]))
            if i < len(dimension_morceaux) and dimension_morceaux[i] != "":
                text += ("$d" + str(dimension_morceaux[i]))
            if text != "215 ##":
                resultats.append(text)
        return "\n".join(resultats)+"\n"

    def _champs200(self, article, titre, auteur, complementTitre, numeroVolume, coAuteur, auteurSecondaire):
        article_morceaux, titre_morceaux, auteur_morceaux, complement_morceaux, numero_volume_morceaux, co_auteur_morceaux, auteur_secondaire_morceaux = self._decouperMorceaux(article, titre, auteur, complementTitre, numeroVolume, coAuteur, auteurSecondaire)
        resultats = []
        max_len = max([len(article_morceaux), len(titre_morceaux), len(auteur_morceaux), len(complement_morceaux), len(numero_volume_morceaux), len(co_auteur_morceaux), len(auteur_secondaire_morceaux), 0])
        for i in range(max_len):
            article_val = article_morceaux[i] if i < len(article_morceaux) else ""
            titre_val = titre_morceaux[i] if i < len(titre_morceaux) else ""
            auteur_val = auteur_morceaux[i] if i < len(auteur_morceaux) else ""
            complement_val = complement_morceaux[i] if i < len(complement_morceaux) else ""
            numero_volume_val = numero_volume_morceaux[i] if i < len(numero_volume_morceaux) else ""
            co_auteur_val = co_auteur_morceaux[i] if i < len(co_auteur_morceaux) else ""
            auteur_secondaire_val = auteur_secondaire_morceaux[i] if i < len(auteur_secondaire_morceaux) else ""

            text = "200 "
            if article_val != "":
                text += ("0#$a" + str(article_val) + " @" + str(titre_val))
            else:
                text += ("1#$a@" + str(titre_val))
            if auteur_val != "":
                text += ("$f" + str(auteur_val))
                if co_auteur_val != "":
                    text += ("," + str(co_auteur_val))
                if auteur_secondaire_val != "":
                    text += ("," + str(auteur_secondaire_val))
            if complement_val != "":
                text += ("$e" + str(complement_val))
            if numero_volume_val != "":
                text += ("$h" + str(numero_volume_val))
            if text != "200 ":
                resultats.append(text)
        return "\n".join(resultats)+"\n"
    def _majusculeEnDebutDeCaracteristique(self, text):
        if isinstance(text, list):
            for i in range(len(text)):
                if text[i]:
                    text[i] = text[i][0].upper() + text[i][1:]
        else:
            if text:
                text = text[0].upper() + text[1:]
        return text

    def _retirerLeDernierPointVigule(self,text):
        while text.endswith("\n") or text.endswith(" "):
            text = text[:-1]
        if text.endswith(";"):
            return text[:-1]
        return text
    

    def _formatagePourVilleEditeurAnnee(self,ville,editeur,annee):
        ville = [v.strip() for v in ville.split(",") if v.strip()]
        editeur = [e.strip() for e in editeur.split(",") if e.strip()]
        annee = [a.strip() for a in annee.split(",") if a.strip()]
        text = ""
        for i in range(max(len(ville), len(editeur), len(annee))):
            text += "214 #0"
            if ville != "":
                text += ("$a" + str(ville[i]) if i < len(ville) else "")
            if editeur != "":
                text += ("$c" + str(editeur[i]) if i < len(editeur) else "")
            if annee != "":
                text += ("$d" + str(annee[i]) if i < len(annee) else "")
            text += ","
        text = text.rstrip(",")
        return text


    def ecriture(self):
        self.sauvgarde()
        self.exportation()

    def sauvgarde(self):
        chemaintmp=self.chemain+".txt"
        os.makedirs(os.path.dirname(chemaintmp), exist_ok=True)
        with open(chemaintmp, "w", encoding="utf-8") as f:
            for i in self.listeDesCaracteristiques:
                texte = i.getValeur()
                f.write(f"{self.window.gridLayout.itemAtPosition(i.id,1).widget().text()}${texte}${i.getProba()}${self.window.gridLayout.itemAtPosition(i.id,4).widget().text()}\n")

    def exportation(self):
        chemain=os.path.join(APP_DIR, "Sortie", str(self.nomDuFichier))
        chemain+=".txt"
        print (f"Exportation de la fiche:{chemain}")
        os.makedirs(os.path.dirname(chemain), exist_ok=True)
        with open(chemain,"w", encoding="utf-8") as f:
            f.write(self.affichage())

    def setImage(self):
        chemain=self.chemainScan
        chemainPNG=chemain+".png"
        chemainJPG=chemain+".jpg"
        chemainJPEG=chemain+".jpeg"
        if os.path.exists(chemainPNG):
            image = QtGui.QImage(chemainPNG)
        elif os.path.exists(chemainJPG):
            image = QtGui.QImage(chemainJPG)
        elif os.path.exists(chemainJPEG):
            image = QtGui.QImage(chemainJPEG)
        else:
            image= QtGui.QImage(os.path.join(APP_DIR, "Image", "PasDImage.png"))
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

    def _caractéristiqueARomanisée(self, Caractéristique):
        if Caractéristique is None:
            return ""
        if self._langueARomaninsée():
            if self._besoinDeRomanisée(self,Caractéristique):
                return Caractéristique+" Romanisée"
        return Caractéristique
    
    def _langueARomanisée(self):
        return self.langue in getlangueNonRomaine()

    def _besoinDeRomanisée(self,Caractéristique):
        return Caractéristique in getCaracéristiquesARomanisée()

def getCaracéristiquesARomanisée():
    return ["Titre","Complement du titre","Auteur","Numero du volume","Collection","Ville","Editeur","Mention d'edition","Illustration"]
def getlangueNonRomaine():
    return ["ar","fa","he","ja","ko","zh"]
def getListeDesNomDeCaracteristiquesMultiple():
    return ["Indexation Rameau","Premier Auteur","Role Auteur","Co-Auteur","Role CoAuteur","Auteur Secondaire","Role Auteur Secondaire"]
def getListeDesNomsDeCaracterisitiques():
    return ["Article","Titre","Complement du titre","Auteur","Numero du volume","Collection","Ville","Editeur","Mention d'edition","Annee","Volume","Illustration","Dimension","Indexation Rameau","Premier Auteur","Co-Auteur","Role Auteur","Role CoAuteur","Auteur Secondaire","Role Auteur Secondaire","Nom de la Collectivite","Role de la Collectivite"]