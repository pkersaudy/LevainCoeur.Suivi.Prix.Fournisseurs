"""LLM de secours : arbitre uniquement les cas ambigus, avec la short-list
d'embeddings comme candidats (RAG). Ne voit jamais les 130 matières, seulement
les TOP_K plus proches -> rapide et bon marché."""

from __future__ import annotations

import json
import os
import re

from dotenv import load_dotenv

from config import LLM_API_KEY_ENV, LLM_MAX_RETRIES, LLM_MODEL, LLM_TIMEOUT_S, ROOT

load_dotenv(ROOT / ".env")


class LlmIndisponible(Exception):
    """Le service LLM ne répond pas : la décision revient au boulanger."""


def _api_key() -> str | None:
    for var in LLM_API_KEY_ENV:
        v = os.getenv(var)
        if v:
            return v
    return None


SYSTEME = """Tu es un expert en reconciliation de matieres premieres pour une boulangerie.
On te donne un libelle de facture fournisseur et une liste de matieres candidates de la base.
Choisis la matiere qui correspond, ou reponds "AUCUNE" si aucune ne convient.
Regle importante : "Sel de Guerande", "Sel fin", "Gros sel" sont des sels DIFFERENTS.
Reponds UNIQUEMENT en JSON: {"matiere_matched": "<nom exact d'un candidat ou AUCUNE>", "confiance": 0.0-1.0}
"""


def arbitrer_llm(libelle: str, candidats: list[str], categorie: str = "") -> tuple[str | None, float]:
    """Retourne (canonique choisi ou None, confiance)."""
    key = _api_key()
    if not key:
        raise RuntimeError(f"Cle API absente. Definissez une des variables {LLM_API_KEY_ENV} dans .env")

    from langchain_google_genai import ChatGoogleGenerativeAI
    from langchain_google_genai.chat_models import GoogleAPIError

    llm = ChatGoogleGenerativeAI(
        model=LLM_MODEL, google_api_key=key, timeout=LLM_TIMEOUT_S, max_retries=LLM_MAX_RETRIES
    )
    entree = f"Libelle facture : {libelle}\nCategorie probable : {categorie}\nCandidats : {candidats}"
    try:
        resp = llm.invoke([("system", SYSTEME), ("human", entree)])
    except GoogleAPIError as e:
        raise LlmIndisponible(str(e)) from e

    m = re.search(r"\{.*\}", resp.text, re.DOTALL)
    if not m:
        return None, 0.0
    try:
        data = json.loads(m.group(0))
    except json.JSONDecodeError:
        return None, 0.0
    choix = data.get("matiere_matched")
    conf = float(data.get("confiance", 0.0))
    if not choix or choix.upper() == "AUCUNE" or choix not in candidats:
        return None, conf
    return choix, conf
