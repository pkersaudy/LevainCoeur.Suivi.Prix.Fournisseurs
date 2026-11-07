---
governs: [pipeline/router.py, pipeline/extractors/]
---
# extraction

Transformer le PDF d'un fournisseur en lignes d'articles brutes, sans les interpréter. La désignation reste celle de la
facture, car elle devient la clé d'alias ; le prix et l'unité restent ceux facturés. Le choix entre XML et texte suit la
[décision 2](../decisions.md). Ajouter un fournisseur reste un petit travail : un extracteur et son entrée dans la
liste.

Hors du module : convertir les unités, reconnaître la matière, les factures scannées, les avoirs et la TVA.

- Les 3 factures Transgourmet de juin 2026 donnent 2, 6 et 15 lignes, lues dans leur XML ; à vérifier à la main.
- Chaque ligne porte son fournisseur et la date de la facture ; à vérifier à la main.
- Un PDF qu'aucun extracteur ne reconnaît donne un message qui nomme le fichier, et les autres factures du lot passent ;
  à vérifier à la main.

Écarts connus : [Distralis](../issues/extracteur-distralis.md),
[lignes non reconnues perdues](../issues/lignes-non-reconnues.md).
