---
governs: [pipeline/router.py, pipeline/extractors/, tests/test_extraction.py]
---
# extraction

Transformer le PDF d'un fournisseur en lignes d'articles brutes, sans les interpréter. La désignation reste celle de la
facture, car elle devient la clé d'alias ; le prix et l'unité restent ceux facturés. Le choix entre XML et texte suit
les décisions [2](../decisions.md) et [7](../decisions.md). Ajouter un fournisseur reste un petit travail : un
extracteur et son entrée dans la liste.

Hors du module : convertir les unités, reconnaître la matière, les factures scannées, les avoirs et la TVA.

- Les 3 factures Transgourmet de juin 2026 donnent 2, 6 et 15 lignes, lues dans leur XML ; à vérifier à la main.
- Chaque ligne porte son fournisseur et la date de sa facture, jamais l'échéance, même si le PDF réunit plusieurs
  factures : [test_subery_lit_les_lignes_et_date_chaque_facture_du_pdf](../../tests/test_extraction.py),
  [test_minoterie_prend_la_date_de_facture_et_non_l_echeance](../../tests/test_extraction.py).
- Une ligne Transgourmet porte l'unité facturée de son PDF, et `unité` si elle n'y figure pas :
  [test_transgourmet_prend_l_unite_dans_le_texte_du_pdf](../../tests/test_extraction.py).
- La facture de la Crèmerie, dont le nom n'est que dans le logo, est reconnue, et ses lignes répétées ne comptent qu'une
  fois : [test_cremerie_reconnue_a_son_adresse_mail_et_lignes_dedoublonnees](../../tests/test_extraction.py).
- Un PDF qu'aucun extracteur ne reconnaît donne un message qui nomme le fichier, et les autres factures du lot passent ;
  à vérifier à la main.

Écarts connus : [Distralis](../issues/extracteur-distralis.md),
[lignes non reconnues perdues](../issues/lignes-non-reconnues.md).
