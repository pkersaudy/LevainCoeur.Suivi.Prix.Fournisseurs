---
governs: [pipeline/normalize.py]
---
# normalisation

Ramener un prix facturé à l'unité de comparaison ([décision 6](../decisions.md)) à partir du seul libellé. Quand le
conditionnement ne se lit pas, le prix reste tel quel : mieux vaut une ligne à la pièce visible qu'un €/kg deviné.

Hors du module : choisir la ligne du fichier, et le prix fourni par la facture, qui n'est jamais corrigé ici.

- Un prix déjà au kg ou au litre ressort inchangé ; à vérifier à la main.
- 42,25 € le colis dont le libellé porte 5 KG donne 8,45 €/kg ; à vérifier à la main.
- Sans poids ni volume lisible, le prix et l'unité ressortent inchangés, sans conversion signalée ; à vérifier à la
  main.

Écart connu : [conversions incomplètes](../issues/normalisation-incomplete.md).
