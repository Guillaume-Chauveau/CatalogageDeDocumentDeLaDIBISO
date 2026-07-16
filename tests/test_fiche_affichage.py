import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from Fiche import Fiche


def test_extraire_valeurs_collection_remplit_les_champs_manquants():
    fiche = Fiche.__new__(Fiche)
    fiche._majusculeEnDebutDeCaracteristique = lambda text: text

    result = fiche._extraireValeursCollection("")

    assert result == ("", "", "", "")


def test_extraire_valeurs_collection_gere_une_valeur_partielle():
    fiche = Fiche.__new__(Fiche)
    fiche._majusculeEnDebutDeCaracteristique = lambda text: text

    result = fiche._extraireValeursCollection("Article test|Collection test")

    assert result == ("Article test", "Collection test", "", "")
