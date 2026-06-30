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
                    labelText, fieldText, proba, edit = line.strip().split("$")   
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
    def ratioParCaracteristique(self,Caracteristique):
        compteurDeLaCaracteristique=0
        compteurDeLaCaracteristiqueHumaine=0
        for f in self.FichesFini:
            self.chemain = os.path.join(os.path.dirname(__file__), "Doc", str(f))
            with open(self.chemain, "r") as f:
                for line in f:
                    labelText, fieldText, proba, edit = line.strip().split("$")
                    if labelText==Caracteristique:
                        compteurDeLaCaracteristique+=1
                        if edit=="1":
                            compteurDeLaCaracteristiqueHumaine+=1
            f.close()
        if compteurDeLaCaracteristique==0:
            return 0
        return compteurDeLaCaracteristiqueHumaine/compteurDeLaCaracteristique
    
    ## renvoi un dictionnaire trier par caractistique où le model à le mieux fonctionner
    def caracteristiquesLesPlusAutomatique(self):
        liste=self.ratioParCaracteristiques()
        return dict(sorted(liste.items(), key=lambda item: item[1]))

    def desinnerRatioHumain(self):
        DicoCaracteristiquesLesPlusAutomatique=self.caracteristiquesLesPlusAutomatique()
        print(DicoCaracteristiquesLesPlusAutomatique)
        figure = Figure(figsize=(5, 5))
        ax = figure.add_subplot(111)
        ax.set_ylim(0, 1)
        ax.bar( list(DicoCaracteristiquesLesPlusAutomatique.keys()),list(DicoCaracteristiquesLesPlusAutomatique.values()))
        ax.set_ylabel('probabilité')
        ax.set_title('Ratio de Remplissage Humain')
        ax.set_xlabel('Caractéristiques')
        ax.tick_params(axis='x', rotation=90)
        figure.tight_layout()
        return figure

    def desinnerPourcentageFait(self):
        figure = Figure(figsize=(5, 5))
        ax = figure.add_subplot(111)
        ax.set_ylim(0, 100)
        ax.pie([self.pourcentageFait(),100-self.pourcentageFait()],labels=['Fait', 'Non fait'],autopct="%1.1f%%")
        ax.set_title('Pourcentage de réalisation des fiches')
        figure.tight_layout()
        return figure
    
    def _normaliserValeurPourComparaison(self, label, valeur):
        if valeur is None:
            return ""
        texte = valeur.strip()
        if label in F.getlisteDesCaracteristiquesMultiple():
            elements = [item.strip() for item in texte.split(",") if item.strip()]
            return tuple(sorted(elements))
        return texte

    def _lireCaracteristiques(self, chemin):
        resultat = {}
        if not os.path.exists(chemin):
            return resultat
        with open(chemin, "r", encoding="utf-8") as f:
            for line in f:
                parts = line.strip().split("$", 3)
                if len(parts) != 4:
                    continue
                labelText, fieldText, proba, edit = parts
                resultat[labelText] = fieldText
        return resultat

    def calculerNombreDErreurParCaracteristique(self):
        ## fonction qui calcule le nombre moyen d'erreur par caractéristique en comparant les fiches de sortie(/Doc) avec les fiches d'entrée(/LLMOutput)
        erreurs = {nom: 0 for nom in F.getlisteDesNoms()}
        totaux = {nom: 0 for nom in F.getlisteDesNoms()}

        for fichier in self.Fiches:
            chemin_doc = os.path.join(os.path.dirname(__file__), "Doc", str(fichier))
            chemin_llm = os.path.join(os.path.dirname(__file__), "LLMOutput", str(fichier))
            if not os.path.exists(chemin_llm):
                continue

            donnees_doc = self._lireCaracteristiques(chemin_doc)
            donnees_llm = self._lireCaracteristiques(chemin_llm)

            for nom in F.getlisteDesNoms():
                if nom not in donnees_doc or nom not in donnees_llm:
                    continue
                totaux[nom] += 1
                valeur_doc = self._normaliserValeurPourComparaison(nom, donnees_doc[nom])
                valeur_llm = self._normaliserValeurPourComparaison(nom, donnees_llm[nom])
                if valeur_doc != valeur_llm:
                    erreurs[nom] += 1

        return {
            nom: (erreurs[nom] / totaux[nom]) if totaux[nom] else 0
            for nom in F.getlisteDesNoms()
        }
    
    def dessinerNombreDErreurParCaracteristique(self):
        erreurs = self.calculerNombreDErreurParCaracteristique()
        figure = Figure(figsize=(5, 5))
        ax = figure.add_subplot(111)
        #ax.set_ylim(0, 1)
        ax.bar(list(erreurs.keys()), list(erreurs.values()))
        ax.set_ylabel('probabilité d\'erreurs')
        ax.set_title('Nombre moyen d\'erreurs par caractéristique')
        ax.set_xlabel('Caractéristiques')
        ax.tick_params(axis='x', rotation=90)
        figure.tight_layout()
        return figure

    def calculerNombreDeCaracteristiqueCorrigeParFichierParFichier(self):
        erreurs = {}
        for fichier in self.Fiches:
            cheminDoc = os.path.join(os.path.dirname(__file__), "Doc", str(fichier))
            cheminLLM = os.path.join(os.path.dirname(__file__), "LLMOutput", str(fichier))
            if not os.path.exists(cheminLLM):
                continue

            donneesDoc = self._lireCaracteristiques(cheminDoc)
            donneesLLM = self._lireCaracteristiques(cheminLLM)

            erreursFichier = 0
            totalCaracteristiques = 0

            for nom in F.getlisteDesNoms():
                if nom not in donneesDoc or nom not in donneesLLM:
                    continue
                totalCaracteristiques += 1
                valeurDoc = self._normaliserValeurPourComparaison(nom, donneesDoc[nom])
                valeurLLM = self._normaliserValeurPourComparaison(nom, donneesLLM[nom])
                if valeurDoc != valeurLLM:
                    erreursFichier += 1

            def _remouveExtension(filename):
                return os.path.splitext(filename)[0]
            
            erreurs[_remouveExtension(fichier)] = erreursFichier if totalCaracteristiques else 0

        return erreurs
    
    def dessinerNombreDeCaracteristiqueCorrigeParFichier(self):
        erreurs = self.calculerNombreDeCaracteristiqueCorrigeParFichierParFichier()
        print(erreurs)
        valeurs = list(erreurs.values())
        occurrences = [valeurs.count(valeur) for valeur in valeurs]
        figure = Figure(figsize=(5, 5))
        ax = figure.add_subplot(111)
        ax.set_ylim(0, 21) #à voir si relement utile
        ax.scatter(occurrences, valeurs)
        ax.set_ylabel('Nombre de caractéristiques corrigées')
        ax.set_title('Nombre de caractéristiques corrigées par fichier')
        ax.set_xlabel('Nombre de fichiers')
        ax.tick_params(axis='x', rotation=15)
        figure.tight_layout()
        return figure

if __name__ == "__main__":
    S=Statistique()
    print(S.caracteristiquesLesPlusAutomatique())
    print("pourcentage de réalisation: "+str(S.pourcentageFait()))
    print(str(S.getRatioHumain())+"% de remplisage humain")