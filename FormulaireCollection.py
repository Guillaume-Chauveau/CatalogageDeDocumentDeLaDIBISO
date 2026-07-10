from PySide6 import QtWidgets


class FormulaireCollection:
    _NOMS_CHAMPS = {
        "article": ("lineEdit", "Article", "article", "articleEdit", "lineEditArticle"),
        "collection": ("lineEdit_2", "Collection", "collection", "collectionEdit", "lineEditCollection"),
        "section": ("lineEdit_3", "Section", "section", "sectionEdit", "lineEditSection"),
        "reference": ("lineEdit_4", "Reference", "reference", "referenceEdit", "lineEditReference"),
    }

    def __init__(self, window, fiche=None):
        self.window = window
        self.fiche = fiche

        self.article = ""
        self.collection = ""
        self.section = ""
        self.reference = ""

        self._connecterSignaux()

        if self.fiche is not None:
            self.fiche.formulaireCollection = self

        self.remplirFormulaire()

    def _connecterSignaux(self):
        for attr in ("Valider", "Validation"):
            button = getattr(self.window, attr, None)
            if button is not None and hasattr(button, "clicked"):
                button.clicked.connect(self.sauvegarderFormulaire)

        for attr in ("Annuler", "Annulation"):
            button = getattr(self.window, attr, None)
            if button is not None and hasattr(button, "clicked"):
                button.clicked.connect(self.annulerCollection)

    def _get_widget(self, key):
        candidates = self._NOMS_CHAMPS[key]

        for name in candidates:
            widget = getattr(self.window, name, None)
            if isinstance(widget, QtWidgets.QLineEdit):
                return widget

        line_edits = self.window.findChildren(QtWidgets.QLineEdit)
        mapping = {
            "article": 0,
            "collection": 1,
            "section": 2,
            "reference": 3,
        }
        index = mapping.get(key, 0)
        if index < len(line_edits):
            return line_edits[index]

        print(f"[FormulaireCollection] widget introuvable pour {key}")
        return None

    def _set_text(self, key, value):
        widget = self._get_widget(key)
        if widget is not None:
            widget.setText(value or "")

    def recupererValeursDepuisWidgets(self):
        article = self._get_widget("article")
        collection = self._get_widget("collection")
        section = self._get_widget("section")
        reference = self._get_widget("reference")

        return {
            "article": article.text().strip() if article is not None else "",
            "collection": collection.text().strip() if collection is not None else "",
            "section": section.text().strip() if section is not None else "",
            "reference": reference.text().strip() if reference is not None else "",
        }

    def getValeurs(self):
        return {
            "article": self.article,
            "collection": self.collection,
            "section": self.section,
            "reference": self.reference,
        }

    def remplirFormulaire(self):
        if self.fiche is not None:
            self.article = self.fiche.getValeurParNom("Article") or ""
            self.collection = self.fiche.getValeurParNom("Collection") or ""

        self._set_text("article", self.article)
        self._set_text("collection", self.collection)
        self._set_text("section", self.section)
        self._set_text("reference", self.reference)

    def _sauvegarderDansFiche(self):
        if self.fiche is None:
            return

        if hasattr(self.fiche, "getCaracteristiqueParNom"):
            for nom, valeur in (
                ("Article", self.article),
                ("Collection", self.collection),
                ("Section", self.section),
                ("Reference", self.reference),
            ):
                caract = self.fiche.getCaracteristiqueParNom(nom)
                if caract is not None and hasattr(caract, "setValeur"):
                    caract.setValeur(valeur)

        if hasattr(self.fiche, "changeEdit"):
            self.fiche.changeEdit(self.fiche.INDICECOLLECTION)

        if hasattr(self.fiche, "updateButtons"):
            self.fiche.updateButtons()

    def sauvegarderFormulaire(self):
        valeurs = self.recupererValeursDepuisWidgets()
        print("[FormulaireCollection] valeurs lues:", valeurs)

        self.article = valeurs["article"]
        self.collection = valeurs["collection"]
        self.section = valeurs["section"]
        self.reference = valeurs["reference"]

        self._sauvegarderDansFiche()
        return valeurs

    def validerCollection(self):
        self.sauvegarderFormulaire()
        self.window.close()

    def annulerCollection(self):
        self.remplirFormulaire()
        self._sauvegarderDansFiche()
        self.window.close()