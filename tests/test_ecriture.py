"""Enchaînement d'un lot et revue humaine, sans PDF ni LLM."""

from types import SimpleNamespace

import pandas as pd
import pytest

import review
import run
from pipeline import matcher, writer
from pipeline.matcher import Resultat

FORMAT_BASE = {"sep": ";", "decimal": ",", "encoding": "utf-8-sig"}
LIBELLE = "Salade Mesclun 2 x 500 g France"


class IndexFactice:
    def synchroniser(self, paires):
        pass


@pytest.fixture
def fichiers(tmp_path, monkeypatch):
    """Base, dictionnaire et file de revue temporaires, avec une ligne écrite par le LLM en base."""
    base = tmp_path / "base.csv"
    alias = tmp_path / "alias.csv"
    file_revue = tmp_path / "a_valider.csv"
    ligne_base = {
        "Catégorie Matière première": "Légumes",
        "Matière première": "Salade multi feuille",
        "Cout à l'unité": 4.5,
        "Unité de mesure": "EUR/kg",
        "Fournisseur": "Subéry",
        "Date du prix": "2026-11-05",
        "Matière d'origine": LIBELLE,
        "Statut correspondance": "llm",
    }
    roquette = ligne_base | {
        "Matière première": "Roquette",
        "Matière d'origine": "Roquette",
        "Date du prix": "2026-01-01",
        "Statut correspondance": "exact",
    }
    pd.DataFrame([ligne_base, roquette]).to_csv(base, index=False, **FORMAT_BASE)
    monkeypatch.setattr(writer, "BASE_CSV", base)
    monkeypatch.setattr(matcher, "BASE_CSV", base)
    monkeypatch.setattr(matcher, "ALIAS_CSV", alias)
    monkeypatch.setattr(review, "REVIEW_CSV", file_revue)
    monkeypatch.setattr(matcher, "IndexCandidats", IndexFactice)
    return SimpleNamespace(base=base, alias=alias, file_revue=file_revue)


def ecrire_revue(fichiers, **cellules):
    ligne = {
        "Categorie": "llm matched",
        "Fournisseur": "Subéry",
        "Date": "2026-11-05",
        "Libelle facture": LIBELLE,
        "Prix": 4.5,
        "Unite": "EUR/kg",
        "Candidats": "Salade multi feuille (0.70)",
        "Choix LLM": "Salade multi feuille",
        "Valide (oui)": "",
        "Matiere de base (a remplir)": "",
    }
    pd.DataFrame([ligne | cellules]).to_csv(fichiers.file_revue, sep=";", encoding="utf-8-sig", index=False)


def lire_base(fichiers):
    return pd.read_csv(fichiers.base, **FORMAT_BASE)


def lignes_du_libelle(fichiers):
    base = lire_base(fichiers)
    return base[base["Matière d'origine"] == LIBELLE]


def test_un_choix_du_llm_rejoint_la_base_et_la_revue_sans_devenir_un_alias(monkeypatch):
    ligne = SimpleNamespace(
        designation="Carotte 5 kg", prix_unitaire_ht=5.0, unite="kg", fournisseur="Subéry", date_prix="2026-11-05"
    )
    alias_appris, ecrit, en_revue = [], [], []

    class MoteurFactice:
        def __init__(self):
            self.cat = {}

        def matcher(self, libelle, utiliser_llm):
            return Resultat("Carottes", "llm", 0.9, "matched", [("Carottes", 0.7)])

        def apprendre_alias(self, *alias):
            alias_appris.append(alias)

    facture = SimpleNamespace(fournisseur="Subéry", date_prix="", lignes=[ligne])
    monkeypatch.setattr(run, "Matcher", MoteurFactice)
    monkeypatch.setattr(run, "router_facture", lambda _: facture)
    monkeypatch.setattr(run, "ajouter_a_base", lambda lignes: ecrit.extend(lignes) or len(lignes))
    monkeypatch.setattr(run, "ajouter_a_revue", lambda lignes: en_revue.extend(lignes) or len(lignes))

    run.traiter([SimpleNamespace(name="facture.pdf")])

    assert [e["Matière première"] for e in ecrit] == ["Carottes"]
    assert [(r["Categorie"], r["Choix LLM"], r["Valide (oui)"]) for r in en_revue] == [("llm matched", "Carottes", "")]
    assert alias_appris == []


def test_un_choix_du_llm_valide_devient_un_alias_exact_sans_doubler_la_base(fichiers):
    ecrire_revue(fichiers, **{"Valide (oui)": "Oui"})

    review.main()

    assert lignes_du_libelle(fichiers)["Statut correspondance"].tolist() == ["matched (revue)"]
    resultat = matcher.Matcher().matcher(LIBELLE)
    assert (resultat.canonique, resultat.methode) == ("Salade multi feuille", "alias")
    assert pd.read_csv(fichiers.file_revue, sep=";", encoding="utf-8-sig").empty


def test_un_choix_du_llm_corrige_rectifie_la_base_et_l_alias(fichiers):
    ecrire_revue(fichiers, **{"Matiere de base (a remplir)": "Roquette"})

    review.main()

    assert lignes_du_libelle(fichiers)["Matière première"].tolist() == ["Roquette"]
    assert lignes_du_libelle(fichiers)["Cout à l'unité"].tolist() == [4.5]
    assert matcher.Matcher().matcher(LIBELLE).canonique == "Roquette"


def test_une_ligne_de_revue_laissee_vide_reste_en_file(fichiers):
    ecrire_revue(fichiers)

    review.main()

    assert not fichiers.alias.exists()
    assert "nan" not in lire_base(fichiers)["Matière première"].tolist()
    assert lignes_du_libelle(fichiers)["Statut correspondance"].tolist() == ["llm"]
    assert len(pd.read_csv(fichiers.file_revue, sep=";", encoding="utf-8-sig")) == 1


def test_oui_ne_valide_pas_une_ligne_sans_choix_du_llm(fichiers):
    ecrire_revue(fichiers, Categorie="a rapprocher", **{"Choix LLM": "", "Valide (oui)": "oui"})

    review.main()

    assert not fichiers.alias.exists()
    assert len(pd.read_csv(fichiers.file_revue, sep=";", encoding="utf-8-sig")) == 1


def test_une_ligne_a_rapprocher_remplie_rejoint_la_base_et_devient_un_alias(fichiers):
    ecrire_revue(
        fichiers, Categorie="a rapprocher", Fournisseur="Distralis", **{"Matiere de base (a remplir)": "Roquette"}
    )

    review.main()

    ajoutee = lire_base(fichiers).query("Fournisseur == 'Distralis'")
    assert ajoutee[["Matière première", "Statut correspondance"]].values.tolist() == [["Roquette", "matched (revue)"]]
    assert matcher.Matcher().matcher(LIBELLE).methode == "alias"
