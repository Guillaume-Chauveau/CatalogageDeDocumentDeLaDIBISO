import unittest

from Fiche import Fiche


class FicheIndexMappingTests(unittest.TestCase):
    def testMultipleFieldIndicesPointToMultipleCaracteristique(self):
        self.assertEqual(Fiche.listeDesNomDeCaracteristiques[Fiche.INDICECHAMPSCIENTIFIQUE], "Indexation Rameau")
        self.assertEqual(Fiche.listeDesNomDeCaracteristiques[Fiche.INDICEAUTEUR], "Premier Auteur")
        self.assertEqual(Fiche.listeDesNomDeCaracteristiques[Fiche.INDICECOAUTEUR], "Co-Auteur")
        self.assertEqual(Fiche.listeDesNomDeCaracteristiques[Fiche.INDICEROLEAUTEUR], "Role Auteur")
        self.assertEqual(Fiche.listeDesNomDeCaracteristiques[Fiche.INDICEROLECOAUTEUR], "Role CoAuteur")
        self.assertEqual(Fiche.listeDesNomDeCaracteristiques[Fiche.INDICEAUTEURSECONDAIRE], "Auteur Secondaire")
        self.assertEqual(Fiche.listeDesNomDeCaracteristiques[Fiche.INDICEROLEAUTEURSECONDAIRE], "Role Auteur Secondaire")


if __name__ == "__main__":
    unittest.main()
