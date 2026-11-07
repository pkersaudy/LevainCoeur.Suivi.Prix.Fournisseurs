"""Index des candidats = noms canoniques + tous les alias connus, comparés par n-grammes de caractères.

Les libellés fournisseurs reprennent les mots des noms du fichier, abrégés ou en majuscules : `SUCRE SEMOULE
PATISSIERE 25 KG` pour `Sucre semoule`. Quelques centaines de textes se vectorisent en quelques millisecondes : l'index
se reconstruit à chaque ajout, sans cache ni modèle à télécharger.
"""

from __future__ import annotations

import re
import unicodedata

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer


def norm(s: str) -> str:
    s = str(s or "").strip().lower()
    s = "".join(c for c in unicodedata.normalize("NFD", s) if unicodedata.category(c) != "Mn")
    return re.sub(r"[^a-z0-9]+", " ", s).strip()


class IndexCandidats:
    def __init__(self):
        self.canonique_par_texte: dict[str, str] = {}

    def synchroniser(self, paires: list[tuple[str, str]]):
        """paires = [(texte, canonique)] : noms canoniques (texte==canonique)
        ET alias (texte=alias fournisseur, canonique=matière de base)."""
        self.canonique_par_texte.update(paires)
        self._canoniques = list(self.canonique_par_texte.values())
        self._vectoriseur = TfidfVectorizer(
            analyzer="char_wb", ngram_range=(3, 5), sublinear_tf=True, preprocessor=norm
        )
        self._matrice = self._vectoriseur.fit_transform(list(self.canonique_par_texte))

    def chercher(self, requete: str, top_k: int) -> list[tuple[str, float]]:
        """Retourne [(canonique, score cosinus)] triés, dédoublonnés par canonique."""
        scores = (self._matrice @ self._vectoriseur.transform([requete]).T).toarray().ravel()
        vus, res = set(), []
        for i in np.argsort(-scores):
            canon = self._canoniques[i]
            if canon in vus:
                continue
            vus.add(canon)
            res.append((canon, float(scores[i])))
            if len(res) >= top_k:
                break
        return res
