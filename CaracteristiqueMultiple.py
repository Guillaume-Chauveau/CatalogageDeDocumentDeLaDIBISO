from Caracteristique import Caracteristique

class CaracteristiqueMultiple(Caracteristique):
    def __init__(self, id, nom, valeur=None, edite=False, proba=0):
        super().__init__(id, nom, valeur, edite, proba)
        self.valeur = [] if valeur is None else valeur

    def getValeur(self):
        return ", ".join(self.valeur) if self.valeur else ""

    def isCaracteristiqueEdite(self):
        return self.edite
    def setCaracteristiqueEdite(self):
        self.edite=True
    def isCaracteristique(self,nom):
        return self.nom==nom
    def setValeur(self, valeur):
        if isinstance(valeur, str):
            if valeur.startswith('{{'):
                self.valeur = [v.strip('{}') for v in valeur.split('}{') if v.strip('{}')]
            else:
                self.valeur = [v.strip() for v in valeur.split(',') if v.strip()]
        elif isinstance(valeur, list):
            self.valeur = valeur
        else:
            self.valeur = [str(valeur)]
    def supValeur(self,valeur):
        self.valeur.remove(valeur)
    def __str__(self):
        if self.valeur is None or len(self.valeur) == 0:
            return ""
        else:
            return "{{"+" | ".join(self.valeur)+"}}"
    
    def getValeurIndexationRameau(self):
        texte="{{"+self.valeur[0]+"}} | rameau"
        for i in range(1,len(self.valeur)):
            texte+=" | {{"+self.valeur[i]+"}} | rameau"
        return texte