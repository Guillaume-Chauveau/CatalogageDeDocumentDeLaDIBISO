import Fiche as F
import os
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
##Todo: interface graphique pour illustré les résultat et l'intégration dans l'application

## classe pour la réalisation des statistique
class Statistique:

    def __init__(self):
        self.Fiches=os.listdir("./Doc")
        self.FichesFini= os.listdir("./Sortie")
        self.totalCaractéristique=0
        self.totalHumain=0
        self.getRatioHumain()

    ## renvoi le ratio de caractistique qui on été rempli par un humain  
    def getRatioHumain(self):
        for i in self.FichesFini:
            self.chemain = os.path.join(os.path.dirname(__file__), "Doc", str(i))
            with open(self.chemain, "r") as f:
                for line in f:
                    print(line)
                    label_text, field_text, proba, edit = line.strip().split("$")   
                    self.totalCaractéristique+=1
                    if edit=="1":
                        self.totalHumain+=1
            f.close()
        return self.totalHumain/self.totalCaractéristique
    
    ## renvoi le pourcentage de complétion des fiches (fiche complaite= fiche qui a eu une Sortie)
    def pourcentageFait(self):
        return ((len(self.FichesFini))*100/(len(self.Fiches)))
    
    ##fonction auxiliaire de caracteristiquesLesPlusAutomatique pour initialiser le dictionnaire et le remplire
    def ratioParCaracteristiques(self):
        d={}
        for i in F.getlisteDesNoms():
            d[i]=self.ratioParCaracteristique(i)
        return d
    

    ##fonction auxiliaire de caracteristiquesLesPlusAutomatique pour le calcule de la performance pour chaque caractéristique 
    def ratioParCaracteristique(self,c):
        cp=0
        cpH=0
        for f in self.FichesFini:
            self.chemain = os.path.join(os.path.dirname(__file__), "Doc", str(f))
            with open(self.chemain, "r") as f:
                for line in f:
                    label_text, field_text, proba, edit = line.strip().split("$")
                    if label_text==c:
                        cp+=1
                        if edit=="1":
                            cpH+=1
            f.close()
        if cp==0:
            return 0
        return cpH/cp
    
    ## renvoi un dictionnaire trier par caractistique où le model à le mieux fonctionner
    def caracteristiquesLesPlusAutomatique(self):
        liste=self.ratioParCaracteristiques()
        return dict(sorted(liste.items(), key=lambda item: item[1]))

    def desinnerRatioHumain(self):
        DicoCaracteristiquesLesPlusAutomatique=self.caracteristiquesLesPlusAutomatique()
        print(DicoCaracteristiquesLesPlusAutomatique)
        figure = Figure(figsize=(10, 6))
        ax = figure.add_subplot(111)
        ax.set_ylim(0, 1)
        ax.bar( list(DicoCaracteristiquesLesPlusAutomatique.keys()),list(DicoCaracteristiquesLesPlusAutomatique.values()))
        ax.set_ylabel('Pourcentage')
        ax.set_title('Ratio de Remplissage Humain')
        ax.set_xlabel('Caractéristiques')
        ax.tick_params(axis='x', rotation=90)
        figure.tight_layout()
        return figure

    def desinnerPourcentageFait(self):
        figure = Figure(figsize=(10, 6))
        ax = figure.add_subplot(111)
        ax.set_ylim(0, 100)
        ax.pie([self.pourcentageFait(),100-self.pourcentageFait()],labels=['Fait', 'Non fait'],autopct="%1.1f%%")
        ax.set_title('Pourcentage de réalisation des fiches')
        figure.tight_layout()
        return figure

if __name__ == "__main__":
    S=Statistique()
    print(S.caracteristiquesLesPlusAutomatique())
    print("pourcentage de réalisation: "+str(S.pourcentageFait()))
    print(str(S.getRatioHumain())+"% de remplisage humain")