"""LLM de secours : arbitre uniquement les cas ambigus, avec la short-list
d'embeddings comme candidats (RAG). Ne voit jamais les 130 matieres, seulement
les TOP_K plus proches -> rapide et bon marche."""

from __future__ import annotations

import json
import os
import re

from config import LLM_API_KEY_ENV, LLM_MODEL


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

    from langchain_core.prompts import ChatPromptTemplate
    from langchain_google_genai import ChatGoogleGenerativeAI

    llm = ChatGoogleGenerativeAI(model=LLM_MODEL, google_api_key=key)
    prompt = ChatPromptTemplate.from_messages([("system", SYSTEME), ("human", "{input}")])
    entree = f"Libelle facture : {libelle}\nCategorie probable : {categorie}\nCandidats : {candidats}"
    resp = (prompt | llm).invoke({"input": entree})
    texte = getattr(resp, "content", None) or getattr(resp, "text", "")  # selon version LangChain

    m = re.search(r"\{.*\}", texte, re.DOTALL)
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
