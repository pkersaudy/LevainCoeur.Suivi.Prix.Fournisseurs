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
    out = pd.concat([base, add], ignore_index=True)
    out = out.sort_values(
        ["Catégorie Matière première", "Matière première", "Fournisseur", "Date du prix"]
    ).reset_index(drop=True)
    out.to_csv(BASE_CSV, sep=CSV_SEP, decimal=CSV_DECIMAL, encoding=CSV_ENCODING, index=False)
    return len(add)


def ajouter_a_revue(lignes: list[dict]):
    if not lignes:
        return 0
    df = pd.DataFrame(lignes)
    header = not REVIEW_CSV.exists()
    df.to_csv(REVIEW_CSV, sep=CSV_SEP, encoding=CSV_ENCODING, index=False, mode="a", header=header)
    return len(df)
