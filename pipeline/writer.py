"""Écriture des résultats : append dans la base longue (historique de prix)
et alimentation de la file de revue pour les cas 'review'."""

from __future__ import annotations

import pandas as pd

from config import BASE_CSV, COLS_BASE, CSV_DECIMAL, CSV_ENCODING, CSV_SEP, REVIEW_CSV


def ajouter_a_base(lignes: list[dict]):
    if not lignes:
        return 0
    base = pd.read_csv(BASE_CSV, sep=CSV_SEP, decimal=CSV_DECIMAL, encoding=CSV_ENCODING)
    add = pd.DataFrame(lignes, columns=COLS_BASE)
    _ecrire_base(pd.concat([base, add], ignore_index=True))
    return len(add)


def rectifier_en_base(lignes: list[dict]):
    """Reporte la décision du boulanger sur les lignes que le LLM a écrites en base.
    Une ligne se repère par son libellé, son fournisseur et sa date."""
    if not lignes:
        return
    base = pd.read_csv(BASE_CSV, sep=CSV_SEP, decimal=CSV_DECIMAL, encoding=CSV_ENCODING)
    colonnes_rectifiees = ["Catégorie Matière première", "Matière première", "Statut correspondance"]
    for ligne in lignes:
        ecrites_par_le_llm = (
            (base["Statut correspondance"] == "llm")
            & (base["Matière d'origine"] == ligne["Matière d'origine"])
            & (base["Fournisseur"] == ligne["Fournisseur"])
            & (base["Date du prix"] == ligne["Date du prix"])
        )
        base.loc[ecrites_par_le_llm, colonnes_rectifiees] = [ligne[c] for c in colonnes_rectifiees]
    _ecrire_base(base)


def ajouter_a_revue(lignes: list[dict]):
    if not lignes:
        return 0
    df = pd.DataFrame(lignes)
    header = not REVIEW_CSV.exists()
    df.to_csv(REVIEW_CSV, sep=CSV_SEP, encoding=CSV_ENCODING, index=False, mode="a", header=header)
    return len(df)


def _ecrire_base(base: pd.DataFrame):
    trie = base.sort_values(
        ["Catégorie Matière première", "Matière première", "Fournisseur", "Date du prix"]
    ).reset_index(drop=True)
    trie.to_csv(BASE_CSV, sep=CSV_SEP, decimal=CSV_DECIMAL, encoding=CSV_ENCODING, index=False)
