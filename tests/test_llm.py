"""Arbitrage LLM, sans appel au service."""

import pandas as pd
import pytest
from langchain_core.messages import AIMessage
from langchain_google_genai import chat_models

from pipeline import llm, matcher
from pipeline.llm import arbitrer_llm


class IndexFactice:
    """Renvoie un candidat dans la zone d'arbitrage du LLM."""

    def synchroniser(self, paires):
        pass

    def chercher(self, libelle, top_k):
        return [("Carottes", 0.7)]


class ErreurService(chat_models.GoogleAPIError):
    def __init__(self):
        Exception.__init__(self, "503 UNAVAILABLE")


@pytest.fixture
def service(monkeypatch):
    """Remplace le client Gemini par un `invoke` donné, et compte ses appels."""
    appels = []

    def poser(invoke):
        class ClientFactice:
            def __init__(self, **_):
                pass

            def invoke(self, messages):
                appels.append(messages)
                return invoke()

        monkeypatch.setattr(chat_models, "ChatGoogleGenerativeAI", ClientFactice)
        monkeypatch.setattr("langchain_google_genai.ChatGoogleGenerativeAI", ClientFactice)
        monkeypatch.setenv("GEMINI_API_KEY", "factice")
        return appels

    return poser


def test_lit_une_reponse_en_blocs_de_contenu(service):
    bloc = {"type": "text", "text": '{"matiere_matched": "Carottes", "confiance": 0.9}'}
    service(lambda: AIMessage(content=[bloc]))

    assert arbitrer_llm("Carotte Lavée 5 kg", ["Carottes", "Rhurbarbe"]) == ("Carottes", 0.9)


def test_ignore_une_reponse_hors_des_candidats(service):
    service(lambda: AIMessage(content='{"matiere_matched": "Panais", "confiance": 0.9}'))

    assert arbitrer_llm("Panais 5 kg", ["Carottes"]) == (None, 0.9)


def test_service_indisponible_envoie_le_lot_en_revue_sans_rappeler(service, monkeypatch):
    def echec():
        raise ErreurService

    appels = service(echec)
    monkeypatch.setattr(matcher, "IndexSemantique", IndexFactice)
    monkeypatch.setattr(matcher.pd, "read_csv", lambda *_, **__: pd.DataFrame(columns=COLONNES))
    moteur = matcher.Matcher()

    resultats = [moteur.matcher(libelle) for libelle in ("Carotte 5 kg", "Panais 5 kg")]

    assert [r.statut for r in resultats] == ["review", "review"]
    assert len(appels) == 1


def test_le_prompt_systeme_passe_sans_gabarit(service):
    appels = service(lambda: AIMessage(content="AUCUNE"))

    arbitrer_llm("Libellé {avec} accolades", ["Carottes"])

    assert appels[0][0] == ("system", llm.SYSTEME)


COLONNES = ["Matière première", "Catégorie Matière première", "Alias fournisseur", "Matière de base"]
