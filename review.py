"""Validation humaine des lignes de data/a_valider.csv, puis : python review.py

Lignes "a rapprocher", pas encore en base. Remplissez 'Matiere de base (a remplir)' :
  - avec un nom canonique existant  -> la ligne rejoint la base ET devient un alias
  - avec un NOUVEAU nom             -> nouvelle matière créée dans la base
  - laissez vide                    -> reste en file

Lignes "llm matched", déjà en base sous le 'Choix LLM' :
  - écrivez oui dans 'Valide (oui)'         -> le choix devient un alias
  - ou remplissez 'Matiere de base (a remplir)' -> la ligne de base est corrigée, et ce nom devient l'alias
  - laissez vide                            -> reste en file, sans alias
"""

from __future__ import annotations

import pandas as pd

from config import CATEGORIE_LLM, CSV_ENCODING, CSV_SEP, REVIEW_CSV
from pipeline.matcher import Matcher
from pipeline.writer import ajouter_a_base, rectifier_en_base


def main():
    if not REVIEW_CSV.exists():
        print("Rien a valider.")
        return
    # sans keep_default_na=False, une cellule vide devient une matière nommée "nan"
    df = pd.read_csv(REVIEW_CSV, sep=CSV_SEP, encoding=CSV_ENCODING, keep_default_na=False)
    a_traiter = df[[bool(matiere_retenue(r)) for _, r in df.iterrows()]]
    if a_traiter.empty:
        print("Aucune ligne remplie dans a_valider.csv.")
        return

    matcher = Matcher()
    a_ajouter, a_rectifier = [], []
    for _, r in a_traiter.iterrows():
        canon = matiere_retenue(r)
        cat = matcher.cat.get(canon, "Autres")
        statut = "matched (revue)" if canon in matcher.cat else "new (revue)"
        lignes = a_rectifier if r["Categorie"] == CATEGORIE_LLM else a_ajouter
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

    n = ajouter_a_base(a_ajouter)
    rectifier_en_base(a_rectifier)
    # on retire les lignes traitées de la file
    reste = df.drop(a_traiter.index)
    reste.to_csv(REVIEW_CSV, sep=CSV_SEP, encoding=CSV_ENCODING, index=False)
    print(f"{n} ligne(s) ajoutee(s) a la base, {len(a_rectifier)} choix du LLM valide(s) ou corrige(s).")
    print(f"{len(a_traiter)} alias appris. {len(reste)} ligne(s) restante(s) a valider.")


def matiere_retenue(ligne: pd.Series) -> str:
    """Matière décidée par le boulanger : celle qu'il a écrite, sinon le choix du LLM s'il a dit oui, sinon rien."""
    ecrite = str(ligne["Matiere de base (a remplir)"]).strip()
    if ecrite:
        return ecrite
    if ligne["Categorie"] == CATEGORIE_LLM and str(ligne["Valide (oui)"]).strip().lower() == "oui":
        return ligne["Choix LLM"]
    return ""


if __name__ == "__main__":
    main()
