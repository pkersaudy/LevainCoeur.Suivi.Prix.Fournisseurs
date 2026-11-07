# Les alias ne tiennent pas compte du fournisseur

Quoi : `pipeline/matcher.py:48` indexe les alias par libellé seul, alors que le dictionnaire a une colonne
`Fournisseur`.

Pourquoi : `product.md` retient « la même désignation du même fournisseur » ; deux fournisseurs peuvent écrire le même
libellé pour deux produits différents.

Où : `pipeline/matcher.py:48`, `:60`, `:83`.
