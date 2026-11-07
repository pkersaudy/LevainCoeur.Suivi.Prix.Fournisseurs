"""Validation humaine des lignes 'review'.

Ouvrez data/a_valider.csv, remplissez la colonne 'Matiere de base (a remplir)' :
  - avec un nom canonique existant  -> la ligne rejoint la base ET devient un alias appris
  - avec un NOUVEAU nom             -> nouvelle matière créée dans la base
  - laissez vide                    -> ignorée (hors périmètre)
Puis lancez : python review.py
"""

from __future__ import annotations

import pandas as pd

from config import CSV_ENCODING, CSV_SEP, REVIEW_CSV
from pipeline.matcher import Matcher
from pipeline.writer import ajouter_a_base


def main():
    if not REVIEW_CSV.exists():
        print("Rien a valider.")
        return
    df = pd.read_csv(REVIEW_CSV, sep=CSV_SEP, encoding=CSV_ENCODING)
    col = "Matiere de base (a remplir)"
    a_traiter = df[df[col].astype(str).str.strip() != ""]
    if a_traiter.empty:
        print("Aucune ligne remplie dans a_valider.csv.")
        return

    matcher = Matcher()
    lignes = []
    for _, r in a_traiter.iterrows():
        canon = str(r[col]).strip()
        cat = matcher.cat.get(canon, "Autres")
        statut = "matched (revue)" if canon in matcher.cat else "new (revue)"
        lignes.append(
            {
                "Catégorie Matière première": cat,
                "Matière première": canon,
                "Cout à l'unité": r["Prix"],
                "Unité de mesure": r["Unite"],
                "Fournisseur": r["Fournisseur"],
                "Date du prix": r["Date"],
                "Matière d'origine": r["Libelle facture"],
                "Statut correspondance": statut,
            }
        )
        # apprentissage : le libellé devient un alias pour la prochaine fois
        matcher.apprendre_alias(r["Libelle facture"], canon, r["Fournisseur"], "revue")

    n = ajouter_a_base(lignes)
    # on retire les lignes traitées de la file
    reste = df[df[col].astype(str).str.strip() == ""]
    reste.to_csv(REVIEW_CSV, sep=CSV_SEP, encoding=CSV_ENCODING, index=False)
    print(f"{n} ligne(s) integree(s) a la base et apprise(s) comme alias. {len(reste)} restante(s) a valider.")


if __name__ == "__main__":
    main()
