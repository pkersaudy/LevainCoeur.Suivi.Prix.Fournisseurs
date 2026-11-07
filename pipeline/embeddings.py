"""Index semantique = noms canoniques + tous les alias connus.

Point cle demande : la (re)vectorisation est INCREMENTALE.
- On garde un cache disque {texte -> vecteur}.
- A chaque lancement, on encode UNIQUEMENT les textes absents du cache
  (typiquement les nouveaux alias que vous venez d'ajouter au dictionnaire),
  puis on les ajoute a l'index. On ne re-encode jamais tout.
"""
from __future__ import annotations
from pathlib import Path
import numpy as np
import pandas as pd

from config import EMB_CACHE, EMBEDDING_MODEL


class IndexSemantique:
    def __init__(self, model_name: str = EMBEDDING_MODEL, cache_path: Path = EMB_CACHE):
        self.model_name = model_name
        self.cache_path = cache_path
        self._model = None
        # cache : DataFrame [texte, canonique, vecteur(list[float])]
        if cache_path.exists():
            self.cache = pd.read_parquet(cache_path)
        else:
            self.cache = pd.DataFrame(columns=["texte", "canonique", "vecteur"])
        self._matrix = None  # matrice numpy normalisee (construite a la volee)

    @property
    def model(self):
        if self._model is None:
            from sentence_transformers import SentenceTransformer   # import paresseux
            self._model = SentenceTransformer(self.model_name)
        return self._model

    def synchroniser(self, paires: list[tuple[str, str]]):
        """paires = [(texte, canonique)] : noms canoniques (texte==canonique)
        ET alias (texte=alias fournisseur, canonique=matiere de base).
        N'encode que les textes pas encore en cache."""
        connus = set(self.cache["texte"])
        nouveaux = [(t, c) for (t, c) in dict((t, c) for t, c in paires).items()
                    if t not in connus]
        if nouveaux:
            textes = [t for t, _ in nouveaux]
            vecs = self.model.encode(textes, normalize_embeddings=True)
            ajout = pd.DataFrame({
                "texte": textes,
                "canonique": [c for _, c in nouveaux],
                "vecteur": [v.astype("float32").tolist() for v in vecs],
            })
            self.cache = pd.concat([self.cache, ajout], ignore_index=True)
            self.cache.to_parquet(self.cache_path, index=False)
            print(f"  [embeddings] {len(nouveaux)} nouveau(x) vecteur(s) encode(s) "
                  f"(cache: {len(self.cache)} au total)")
        self._matrix = None  # invalide le cache matriciel

    def _M(self) -> np.ndarray:
        if self._matrix is None:
            self._matrix = np.array(self.cache["vecteur"].tolist(), dtype="float32")
        return self._matrix

    def chercher(self, requete: str, top_k: int = 5) -> list[tuple[str, float]]:
        """Retourne [(canonique, score_cosinus)] tries, dedoublonnes par canonique."""
        if len(self.cache) == 0:
            return []
        q = self.model.encode([requete], normalize_embeddings=True)[0]
        sims = self._M() @ q                      # cosinus (vecteurs normalises)
        ordre = np.argsort(-sims)
        vus, res = set(), []
        for i in ordre:
            canon = self.cache.iloc[i]["canonique"]
            if canon in vus:
                continue
            vus.add(canon)
            res.append((canon, float(sims[i])))
            if len(res) >= top_k:
                break
        return res
