"""Point d'entree : traite tous les PDF d'un dossier et enrichit la base.

    python run.py                 # traite le dossier factures_a_traiter/
    python run.py chemin.pdf ...  # traite des fichiers precis
    python run.py --no-llm        # desactive le fallback LLM (alias + embeddings seulement)

Flux par ligne : extraction -> normalisation EUR/kg -> matching cascade
-> ecriture base (si matched) ou file de revue (si review).
"""
from __future__ import annotations
import sys
from pathlib import Path

from config import INBOX, COLS_BASE
from pipeline.router import router_facture
from pipeline.matcher import Matcher
from pipeline.normalize import vers_prix_kg
from pipeline.writer import ajouter_a_base, ajouter_a_revue


def traiter(pdfs: list[Path], utiliser_llm: bool = True):
    matcher = Matcher()
    a_base, a_revue = [], []
    stats = {"alias": 0, "embeddings": 0, "llm": 0, "review": 0}

    for pdf in pdfs:
        print(f"\n=== {pdf.name} ===")
        try:
            facture = router_facture(pdf)
        except Exception as e:
            print(f"  [!] {e}")
            continue
        print(f"  Fournisseur : {facture.fournisseur} | date {facture.date_prix} "
              f"| {len(facture.lignes)} ligne(s)")

        for lg in facture.lignes:
            prix, unite, _ = vers_prix_kg(lg.prix_unitaire_ht, lg.unite, lg.designation)
            res = matcher.matcher(lg.designation, utiliser_llm=utiliser_llm)
            stats[res.methode] = stats.get(res.methode, 0) + 1

            if res.statut == "matched":
                a_base.append({
                    "Catégorie Matière première": matcher.cat.get(res.canonique, "Autres"),
                    "Matière première": res.canonique,
                    "Cout à l'unité": prix,
                    "Unité de mesure": unite,
                    "Fournisseur": lg.fournisseur,
                    "Date du prix": lg.date_prix,
                    "Matière d'origine": lg.designation,
                    "Statut correspondance": res.methode,
                })
                # apprentissage : embeddings/llm deviennent un alias exact pour la prochaine fois
                if res.methode in ("embeddings", "llm"):
                    matcher.apprendre_alias(lg.designation, res.canonique, lg.fournisseur, res.methode)
                print(f"    OK [{res.methode} {res.score:.2f}] {lg.designation!r} -> {res.canonique!r}")
            else:
                a_revue.append({
                    "Fournisseur": lg.fournisseur, "Date": lg.date_prix,
                    "Libelle facture": lg.designation, "Prix": prix, "Unite": unite,
                    "Candidats": " | ".join(f"{c} ({s:.2f})" for c, s in res.candidats),
                    "Matiere de base (a remplir)": "",
                })
                print(f"    ? [revue] {lg.designation!r} -> candidats: "
                      f"{[c for c, _ in res.candidats]}")

    n1 = ajouter_a_base(a_base)
    n2 = ajouter_a_revue(a_revue)
    print(f"\n--- Bilan --- base +{n1} | a valider +{n2} | detail methodes: {stats}")
    if n2:
        print("    -> completez data/a_valider.csv puis lancez : python review.py")


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("-")]
    no_llm = "--no-llm" in sys.argv
    if args:
        pdfs = [Path(a) for a in args]
    else:
        INBOX.mkdir(exist_ok=True)
        pdfs = sorted(INBOX.glob("*.pdf"))
    if not pdfs:
        print(f"Aucun PDF. Deposez des factures dans {INBOX}/ ou passez des chemins en argument.")
    else:
        traiter(pdfs, utiliser_llm=not no_llm)
