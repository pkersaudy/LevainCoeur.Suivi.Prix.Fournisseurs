# Le moteur tourne, mais ses résultats ne sont pas fiables

Quoi : le 2026-11-07, `python run.py --no-llm` va au bout de 7 PDF sur 8, 65 lignes. Le lot n'est pas celui de juin : ce
sont les factures reçues du 28/09 au 05/11/2026 (la date du nom `20260721_evolution_des_prix_ingredients.xlsx` est
fausse, dit le boulanger).

Où : `factures_a_traiter/`, non versionné.

## Tranché par le boulanger, à livrer

- Plus aucune acceptation par embeddings : ils ne font que proposer des candidats au LLM ou au boulanger. Mesuré :
  `JAUNE OEUF` -> `Blanc d'oeuf liquide`, `Panais` -> `Rhurbarbe` à 0,95, 6 des 8 premières lignes acceptées fausses,
  parce que `Cat.1 France` pèse plus que le produit. À écrire en décision, elle remplace le palier 2 de la décision 3.
- Un alias n'est retenu qu'après validation humaine : `run.py` apprend aujourd'hui les embeddings et le LLM, et l'erreur
  se propage ensuite à 1,00. Voir [écriture sans validation](ecriture-sans-validation.md).
- Boissons et consommables ignorés ([product.md](../product.md)). Reste à choisir comment : la base a déjà une catégorie
  `Emballage` avec du film alimentaire.

## Reste à mesurer ou à bâtir

- Rapprochement avec Gemini : `gemini-3.8-flash` en 503 ou 504 sur tous les appels du 2026-11-07, un seul appel a
  répondu, avant correction du code. L'arbitrage n'a pas été évalué.
- Crèmerie : le marqueur `Crèmerie` n'est pas dans le PDF, qui n'a que `cremeriedelarance@live.fr` ; extraction non
  essayée.
- Team Ouest (`FACTURE_19693635_A3B.pdf`, 3 pages) : aucun extracteur, peut-être le même sujet que
  [Distralis](extracteur-distralis.md).
- Subéry : les poids de ligne ne servent pas, `Courge Potimarron 15 Pièces` reste à 1,04 la pièce pour 1,30 €/kg réel.
- Normalisation : `SAUCISSE TOULOUSE VPF 125G X 8`, une barquette de 1 kg à 8,98 €, donne 71,85 €/kg
  ([issue](normalisation-incomplete.md)).
