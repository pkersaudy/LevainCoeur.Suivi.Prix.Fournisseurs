# Le moteur tourne, mais ses résultats ne sont pas fiables

Quoi : le 2026-11-07, `python run.py --no-llm` lit 6 PDF sur 8, 65 lignes. Le lot n'est pas celui de juin : ce
sont les factures reçues du 28/09 au 05/11/2026 (la date du nom `20260721_evolution_des_prix_ingredients.xlsx` est
fausse, dit le boulanger).

Où : `factures_a_traiter/`, non versionné.

## Tranché par le boulanger, à livrer

- Plus aucune acceptation par embeddings : ils ne font que proposer des candidats au LLM ou au boulanger. Mesuré :
  `JAUNE OEUF` -> `Blanc d'oeuf liquide`, `Panais` -> `Rhurbarbe` à 0,95, 6 des 8 premières lignes acceptées fausses,
  parce que `Cat.1 France` pèse plus que le produit. À écrire en décision, elle remplace le palier 2 de la décision 3.
- Un alias n'est retenu qu'après validation humaine : `run.py` apprend aujourd'hui les embeddings et le LLM, et l'erreur
  se propage ensuite à 1,00. Voir [écriture sans validation](ecriture-sans-validation.md).
- Un choix du LLM sous 0,80 de confiance part en revue. Mesuré : les 4 choix à 0,60 sur les 65 lignes sont tous douteux
  ([candidats manquants](candidats-manquants.md)).
- Boissons et consommables ignorés ([product.md](../product.md)). Reste à choisir comment : la base a déjà une catégorie
  `Emballage` avec du film alimentaire. Distralis facture aussi du matériel, 3 lignes de code `MAL002` sur 39 le
  31/10/2026 (`CANDISSOIRE`, `CERCLE MOUSSE`, `MAIN ALUMINIUM`).

## Reste à mesurer ou à bâtir

- Rapprochement : mesuré avec Claude Haiku 5.5, voir [candidats manquants](candidats-manquants.md).
- Subéry : les poids de ligne ne servent pas, `Courge Potimarron 15 Pièces` reste à 1,04 la pièce pour 1,30 €/kg réel.
- Normalisation : `SAUCISSE TOULOUSE VPF 125G X 8`, une barquette de 1 kg à 8,98 €, donne 71,85 €/kg
  ([issue](normalisation-incomplete.md)).
