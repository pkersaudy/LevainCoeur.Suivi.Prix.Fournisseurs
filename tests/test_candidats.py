"""Short-list des candidats, sur des libellés réels du 2026-11-07."""

import pytest

from pipeline.candidats import IndexCandidats

MATIERES = ["Sucre semoule", "Sucre glace", "Roquette", "Salade multi feuille", "Tournesol", "Oeuf seau 75/120"]
MATIERES += ["Melange Graine et Legumineuses", "Oeufs moyen coquille", "Oeufs liquides entier", "OEUF OVO"]


@pytest.fixture
def index():
    index = IndexCandidats()
    index.synchroniser([(m, m) for m in MATIERES])
    return index


@pytest.mark.parametrize(
    ("libelle", "matiere"),
    [
        ("SUCRE SEMOULE PATISSIERE 25 KG", "Sucre semoule"),
        ("Salade Roquette 2 x 500 g France", "Roquette"),
        ("GRAINE DE TOURNESOL DECORTIQUEE 5KG", "Tournesol"),
    ],
)
def test_la_matiere_qui_partage_les_mots_du_libelle_vient_en_tete(index, libelle, matiere):
    assert index.chercher(libelle, 10)[0][0] == matiere


def test_un_alias_valide_fait_venir_sa_matiere_en_tete_pour_un_libelle_voisin(index):
    index.synchroniser([("OEUF ECALE 43/53 SEAU X150 OVOTEAM", "Oeuf seau 75/120")])

    assert index.chercher("OEUF ECALE 53/63 FR S/AT POCHE 4X10 X3 OVOTEAM", 10)[0][0] == "Oeuf seau 75/120"


def test_chaque_matiere_ne_vient_qu_une_fois(index):
    index.synchroniser([("SUCRE SEMOULE 1 KG", "Sucre semoule")])

    candidats = [c for c, _ in index.chercher("SUCRE SEMOULE 25 KG", 10)]

    assert len(candidats) == len(set(candidats)) == len(MATIERES)
