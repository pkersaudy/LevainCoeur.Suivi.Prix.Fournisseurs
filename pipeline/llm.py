"""LLM de secours : arbitre uniquement les cas ambigus, avec la short-list
d'embeddings comme candidats (RAG). Ne voit jamais les 130 matières, seulement
les TOP_K plus proches -> rapide et bon marché."""

from __future__ import annotations

import json
import os

import anthropic
from dotenv import load_dotenv

from config import LLM_API_KEY_ENV, LLM_MAX_RETRIES, LLM_MAX_TOKENS, LLM_MODEL, LLM_TIMEOUT_S, ROOT

load_dotenv(ROOT / ".env")

SYSTEME = """Tu es un expert en réconciliation de matières premières pour une boulangerie.
On te donne un libellé de facture fournisseur et une liste de matières candidates de la base.
Choisis la matière qui correspond, ou réponds "AUCUNE" si aucune ne convient.
Règle importante : "Sel de Guérande", "Sel fin", "Gros sel" sont des sels DIFFÉRENTS.
"""


class LlmIndisponible(Exception):
    """Le service LLM ne répond pas : la décision revient au boulanger."""


def arbitrer_llm(libelle: str, candidats: list[str], categorie: str = "") -> tuple[str | None, float]:
    """Retourne (canonique choisi ou None, confiance)."""
    key = os.getenv(LLM_API_KEY_ENV)
    if not key:
        raise RuntimeError(f"Clé API absente. Définissez {LLM_API_KEY_ENV} dans .env")

    client = anthropic.Anthropic(api_key=key, timeout=LLM_TIMEOUT_S, max_retries=LLM_MAX_RETRIES)
    entree = f"Libellé facture : {libelle}\nCatégorie probable : {categorie}\nCandidats : {candidats}"
    try:
        reponse = client.messages.create(
            model=LLM_MODEL,
            max_tokens=LLM_MAX_TOKENS,
            system=SYSTEME,
            messages=[{"role": "user", "content": entree}],
            output_config={"format": {"type": "json_schema", "schema": _schema_reponse(candidats)}},
        )
    except anthropic.APIError as e:
        raise LlmIndisponible(str(e)) from e

    if reponse.stop_reason != "end_turn":  # réponse coupée ou refusée : pas de JSON à lire
        return None, 0.0
    data = json.loads(next(bloc.text for bloc in reponse.content if bloc.type == "text"))
    choix = data["matiere_matched"]
    conf = float(data["confiance"])
    if choix not in candidats:
        return None, conf
    return choix, conf


def _schema_reponse(candidats: list[str]) -> dict:
    """Schéma JSON qui limite la réponse aux candidats, ou à AUCUNE."""
    return {
        "type": "object",
        "properties": {
            "matiere_matched": {"type": "string", "enum": [*candidats, "AUCUNE"]},
            "confiance": {"type": "number"},
        },
        "required": ["matiere_matched", "confiance"],
        "additionalProperties": False,
    }
