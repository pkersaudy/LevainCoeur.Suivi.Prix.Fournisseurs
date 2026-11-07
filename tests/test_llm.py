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


@pytest.fixture
def moteur(monkeypatch):
    """Moteur sans dictionnaire ni base, avec l'index factice."""
    monkeypatch.setattr(matcher, "IndexSemantique", IndexFactice)
    monkeypatch.setattr(matcher.pd, "read_csv", lambda *_, **__: pd.DataFrame(columns=COLONNES))
    return matcher.Matcher()


def test_lit_la_reponse_apres_le_bloc_de_reflexion(service):
    service(lambda: reponse('{"matiere_matched": "Carottes", "confiance": 0.9}'))

    assert arbitrer_llm("Carotte Lavée 5 kg", ["Carottes", "Rhurbarbe"]) == ("Carottes", 0.9)


def test_ignore_une_reponse_hors_des_candidats(service):
    service(lambda: reponse('{"matiere_matched": "Panais", "confiance": 0.9}'))

    assert arbitrer_llm("Panais 5 kg", ["Carottes"]) == (None, 0.9)


def test_ignore_une_reponse_coupee(service):
    service(lambda: SimpleNamespace(stop_reason="max_tokens", content=[]))

    assert arbitrer_llm("Panais 5 kg", ["Carottes"]) == (None, 0.0)


def test_service_indisponible_envoie_le_lot_en_revue_sans_rappeler(moteur, service):
    def echec():
        raise anthropic.APIConnectionError(request=None)

    appels = service(echec)

    resultats = [moteur.matcher(libelle) for libelle in ("Carotte 5 kg", "Panais 5 kg")]

    assert [r.statut for r in resultats] == ["review", "review"]
    assert len(appels) == 1


@pytest.mark.parametrize(
    ("confiance", "statut"),
    [(0.79, "review"), (0.80, "matched")],
)
def test_un_choix_du_llm_sous_le_seuil_de_confiance_part_en_revue(moteur, service, confiance, statut):
    service(lambda: reponse(f'{{"matiere_matched": "Carottes", "confiance": {confiance}}}'))

    assert moteur.matcher("Carotte 5 kg").statut == statut


def test_un_score_d_embeddings_eleve_ne_valide_rien(moteur, monkeypatch):
    monkeypatch.setattr(moteur.index, "chercher", lambda *_: [("Rhurbarbe", 0.95)])

    resultat = moteur.matcher("Panais", utiliser_llm=False)

    assert (resultat.canonique, resultat.statut) == (None, "review")


def test_un_score_d_embeddings_eleve_passe_par_le_llm(moteur, service, monkeypatch):
    service(lambda: reponse('{"matiere_matched": "AUCUNE", "confiance": 0.9}'))
    monkeypatch.setattr(moteur.index, "chercher", lambda *_: [("Rhurbarbe", 0.95)])

    assert moteur.matcher("Panais").statut == "review"


COLONNES = ["Matière première", "Catégorie Matière première", "Alias fournisseur", "Matière de base"]
