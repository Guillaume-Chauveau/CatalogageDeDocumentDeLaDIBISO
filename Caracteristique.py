
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
        return self.valeur
    def setValeur(self,valeur):
        self.valeur=valeur
    def getProba(self):
        return self.proba
    def setProba(self, proba):
        self.proba = proba
    