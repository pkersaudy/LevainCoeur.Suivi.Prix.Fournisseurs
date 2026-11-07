"""Arbitrage LLM, sans appel au service."""

from types import SimpleNamespace

import anthropic
import pandas as pd
import pytest

from pipeline import matcher
from pipeline.llm import arbitrer_llm


class IndexFactice:
    """Renvoie un candidat dans la zone d'arbitrage du LLM."""

    def synchroniser(self, paires):
        pass

    def chercher(self, libelle, top_k):
        return [("Carottes", 0.7)]


def reponse(texte):
    """Réponse complète du service : Haiku 5.5 peut la faire précéder d'un bloc de réflexion."""
    blocs = [SimpleNamespace(type="thinking", thinking=""), SimpleNamespace(type="text", text=texte)]
    return SimpleNamespace(stop_reason="end_turn", content=blocs)


@pytest.fixture
def service(monkeypatch):
    """Remplace le client Anthropic par un `create` donné, et compte ses appels."""
    appels = []

    def poser(create):
        class ClientFactice:
            def __init__(self, **_):
                self.messages = SimpleNamespace(create=self.create)

            def create(self, **requete):
                appels.append(requete)
                return create()

        monkeypatch.setattr(anthropic, "Anthropic", ClientFactice)
        monkeypatch.setenv("ANTHROPIC_API_KEY", "factice")
        return appels

    return poser


def test_lit_la_reponse_apres_le_bloc_de_reflexion(service):
    service(lambda: reponse('{"matiere_matched": "Carottes", "confiance": 0.9}'))

    assert arbitrer_llm("Carotte Lavée 5 kg", ["Carottes", "Rhurbarbe"]) == ("Carottes", 0.9)


def test_ignore_une_reponse_hors_des_candidats(service):
    service(lambda: reponse('{"matiere_matched": "Panais", "confiance": 0.9}'))

    assert arbitrer_llm("Panais 5 kg", ["Carottes"]) == (None, 0.9)


def test_ignore_une_reponse_coupee(service):
    service(lambda: SimpleNamespace(stop_reason="max_tokens", content=[]))

    assert arbitrer_llm("Panais 5 kg", ["Carottes"]) == (None, 0.0)


def test_service_indisponible_envoie_le_lot_en_revue_sans_rappeler(service, monkeypatch):
    def echec():
        raise anthropic.APIConnectionError(request=None)

    appels = service(echec)
    monkeypatch.setattr(matcher, "IndexSemantique", IndexFactice)
    monkeypatch.setattr(matcher.pd, "read_csv", lambda *_, **__: pd.DataFrame(columns=COLONNES))
    moteur = matcher.Matcher()

    resultats = [moteur.matcher(libelle) for libelle in ("Carotte 5 kg", "Panais 5 kg")]

    assert [r.statut for r in resultats] == ["review", "review"]
    assert len(appels) == 1


COLONNES = ["Matière première", "Catégorie Matière première", "Alias fournisseur", "Matière de base"]
