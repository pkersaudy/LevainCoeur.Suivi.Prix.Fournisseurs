# Le moteur tourne, mais ses résultats ne sont pas fiables

Quoi : le 2026-11-07, `python run.py --no-llm` lit 6 PDF sur 8, 65 lignes. Le lot n'est pas celui de juin : ce
sont les factures reçues du 28/09 au 05/11/2026 (la date du nom `20260721_evolution_des_prix_ingredients.xlsx` est
fausse, dit le boulanger).

Où : `factures_a_traiter/`, non versionné.

## Tranché par le boulanger, à livrer

- Boissons et consommables ignorés ([product.md](../product.md)). Reste à choisir comment : la base a déjà une catégorie
  `Emballage` avec du film alimentaire. Distralis facture aussi du matériel, 3 lignes de code `MAL002` sur 39 le
  31/10/2026 (`CANDISSOIRE`, `CERCLE MOUSSE`, `MAIN ALUMINIUM`).

## Reste à mesurer ou à bâtir

- Subéry : les poids de ligne ne servent pas, `Courge Potimarron 15 Pièces` reste à 1,04 la pièce pour 1,30 €/kg réel.
- Normalisation : `SAUCISSE TOULOUSE VPF 125G X 8`, une barquette de 1 kg à 8,98 €, donne 71,85 €/kg
  ([issue](normalisation-incomplete.md)).
