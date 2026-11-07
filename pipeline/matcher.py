"""Rapprochement en cascade d'un libelle fournisseur vers une matiere de base :

    1. alias exact      (dictionnaire, gratuit, deterministe)   -> methode "alias"
    2. embeddings       (cosinus >= SEUIL_AUTO : on accepte)     -> methode "embeddings"
    3. LLM              (entre SEUIL_LLM et SEUIL_AUTO)          -> methode "llm"
    4. sinon            -> "review" (file a_valider.csv)

Les rapprochements surs (1/2/3 acceptes) sont reinjectes comme nouveaux alias
=> le systeme apprend et sollicite de moins en moins embeddings/LLM.
"""

from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass

import pandas as pd

from config import ALIAS_CSV, BASE_CSV, CSV_DECIMAL, CSV_ENCODING, CSV_SEP, SEUIL_AUTO, SEUIL_LLM, TOP_K

from .embeddings import IndexSemantique


def norm(s: str) -> str:
    s = str(s or "").strip().lower()
    s = "".join(c for c in unicodedata.normalize("NFD", s) if unicodedata.category(c) != "Mn")
    return re.sub(r"[^a-z0-9]+", " ", s).strip()


@dataclass
class Resultat:
    canonique: str | None
    methode: str  # alias | embeddings | llm | review
    score: float
    statut: str  # matched | new | review
    candidats: list


class Matcher:
    def __init__(self):
        # matieres de base (noms canoniques + categorie)
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

        # index semantique = canoniques + alias (revectorisation incrementale)
        self.index = IndexSemantique()
        paires = [(c, c) for c in self.canoniques]
        paires += [
            (a, c) for a, c in zip(self.alias["Alias fournisseur"], self.alias["Matière de base"]) if isinstance(a, str)
        ]
        self.index.synchroniser(paires)

    def matcher(self, libelle: str, categorie: str = "", utiliser_llm: bool = True) -> Resultat:
        # 1) alias exact
        c = self.alias_index.get(norm(libelle))
        if c:
            return Resultat(c, "alias", 1.0, "matched", [])

        # 2) embeddings
        cands = self.index.chercher(libelle, TOP_K)
        if cands and cands[0][1] >= SEUIL_AUTO:
            return Resultat(cands[0][0], "embeddings", cands[0][1], "matched", cands)

        # 3) LLM sur la short-list
        if utiliser_llm and cands and cands[0][1] >= SEUIL_LLM:
            from .llm import arbitrer_llm

            choix, conf = arbitrer_llm(libelle, [c for c, _ in cands], categorie)
            if choix:
                return Resultat(choix, "llm", conf, "matched", cands)

        # 4) revue humaine
        return Resultat(None, "review", cands[0][1] if cands else 0.0, "review", cands)

    def apprendre_alias(self, libelle: str, canonique: str, fournisseur: str, methode: str):
        """Ajoute un alias valide au dictionnaire + a l'index (incremental)."""
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
