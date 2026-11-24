
class Caracteristique:
    def __init__(self,id ,nom , valeur="",edite=False, proba=0):
        self.nom = nom
        self.id = id
        self.valeur = valeur
        self.edite=edite
        self.proba = proba

    def isCaracteristiqueEdite(self):
        return self.edite
    def setCaracteristiqueEdite(self):
        self.edite=True
    def isCaracteristique(self,nom):
        return self.nom==nom
    def getValeur(self):
        if self.valeur is None:
            return ""
        if isinstance(self.valeur, (list, tuple, set)):
            return ", ".join(str(v).strip() for v in self.valeur if str(v).strip())
        return str(self.valeur)
    def setValeur(self,valeur):
        if valeur is None:
            self.valeur = ""
        elif isinstance(valeur, (list, tuple, set)):
            self.valeur = [str(v).strip() for v in valeur if str(v).strip()]
        else:
            self.valeur = str(valeur).strip()
    def getProba(self):
        return self.proba
    def setProba(self, proba):
        self.proba = proba
    