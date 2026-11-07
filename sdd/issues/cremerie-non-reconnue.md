# La facture de la Crèmerie n'est pas reconnue

Quoi : `Facture FA00006844.pdf` (29/10/2026) correspond à la Crèmerie de la Rance, confirmé par le boulanger, mais
`router_facture` répond « Aucun extracteur ne reconnait », et ses lignes sont perdues.

Pourquoi : `CremerieExtractor.marqueur` cherche `Crèmerie`, absent du texte. Le nom est sans doute dans le logo, une
image ; le texte n'a que `cremeriedelarance@live.fr` et `La Ferme de la Renaudais`.

Où : `pipeline/extractors/pdf_extractors.py:121`.

Mesuré le 2026-11-07 : appelé directement, l'extracteur lit la date et les 14 lignes de la facture, ramenées à 4
produits (`LAIT ENTIERPASTEURISE` à 0,80 €/L, `CREME FRAICHE LIQUIDE 5L` à 4,15 €/L, `FROMAGE BLANC`, `LAIT RIBOT`).
Seul le marqueur est à changer, pour `cremeriedelarance`, avec un test sur ce texte.
