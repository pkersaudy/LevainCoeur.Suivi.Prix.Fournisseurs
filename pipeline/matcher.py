"""Rapprochement en cascade d'un libellé fournisseur vers une matière de base :

    1. alias exact      (dictionnaire, gratuit, déterministe)   -> méthode "alias"
    2. LLM              (candidats par n-grammes, confiance >= SEUIL_CONFIANCE_LLM) -> méthode "llm"
    3. sinon            -> "review" (file a_valider.csv)

Le score de proximité ne valide rien : il propose des candidats au LLM ou au boulanger.
Seule la revue humaine crée un alias, l'erreur d'une machine ne se propage pas à 1,00.
"""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from config import ALIAS_CSV, BASE_CSV, CSV_DECIMAL, CSV_ENCODING, CSV_SEP, SEUIL_CONFIANCE_LLM, TOP_K

from .candidats import IndexCandidats, norm


@dataclass
class Resultat:
    canonique: str | None
    methode: str  # alias | llm | review
    score: float
    statut: str  # matched | new | review
    candidats: list


class Matcher:
    def __init__(self):
        # matières de base (noms canoniques + catégorie)
        base = pd.read_csv(BASE_CSV, sep=CSV_SEP, decimal=CSV_DECIMAL, encoding=CSV_ENCODING)
        self.canoniques = sorted(base["Matière première"].dropna().unique().tolist())
        self.cat = dict(zip(base["Matière première"], base["Catégorie Matière première"]))

        # dictionnaire d'alias : {alias_normalise -> canonique}
        self.alias = (
            pd.read_csv(ALIAS_CSV, sep=CSV_SEP, encoding=CSV_ENCODING)
            if ALIAS_CSV.exists()
            else pd.DataFrame(columns=["Matière de base", "Alias fournisseur", "Fournisseur", "Statut"])
        )
        self.alias_index = {norm(a): c for a, c in zip(self.alias["Alias fournisseur"], self.alias["Matière de base"])}

        # index des candidats = canoniques + alias
        self.index = IndexCandidats()
        paires = [(c, c) for c in self.canoniques]
        paires += [
            (a, c) for a, c in zip(self.alias["Alias fournisseur"], self.alias["Matière de base"]) if isinstance(a, str)
        ]
        self.index.synchroniser(paires)
        self.llm_disponible = True

    def matcher(self, libelle: str, categorie: str = "", utiliser_llm: bool = True) -> Resultat:
        # 1) alias exact
        c = self.alias_index.get(norm(libelle))
        if c:
            return Resultat(c, "alias", 1.0, "matched", [])

        # 2) LLM sur la short-list des plus proches
        cands = self.index.chercher(libelle, TOP_K)
        if utiliser_llm and self.llm_disponible:
            from .llm import LlmIndisponible, arbitrer_llm

            try:
                choix, conf = arbitrer_llm(libelle, [c for c, _ in cands], categorie)
            except LlmIndisponible as e:
                # on ne repaie pas le délai à chaque ligne : le reste du lot part en revue
                print(f"  [!] LLM indisponible, le reste du lot part en revue : {e}")
                self.llm_disponible = False
            else:
                if choix and conf >= SEUIL_CONFIANCE_LLM:
                    return Resultat(choix, "llm", conf, "matched", cands)

        # 3) revue humaine
        return Resultat(None, "review", cands[0][1], "review", cands)

    def apprendre_alias(self, libelle: str, canonique: str, fournisseur: str, methode: str):
        """Ajoute un alias validé au dictionnaire + à l'index."""
        if norm(libelle) in self.alias_index:
            return
        self.alias_index[norm(libelle)] = canonique
        self.alias = pd.concat(
            [
                self.alias,
                pd.DataFrame(
                    [
                        {
                            "Matière de base": canonique,
                            "Alias fournisseur": libelle,
                            "Fournisseur": fournisseur,
                            "Statut": f"appris ({methode})",
                        }
                    ]
                ),
            ],
            ignore_index=True,
        )
        self.alias.to_csv(ALIAS_CSV, sep=CSV_SEP, encoding=CSV_ENCODING, index=False)
        self.index.synchroniser([(libelle, canonique)])
