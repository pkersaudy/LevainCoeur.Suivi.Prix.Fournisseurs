# Rapprocher vers les lignes du fichier Excel, pas vers la base de test

Quoi : le moteur rapproche vers les matières de `data/base_prix_matieres_premieres.csv`. Cette base ne sert que de test
et disparaîtra, dit le boulanger le 2026-11-07 : les références qui comptent sont les lignes du fichier
`AAAAMMJJ_evolution_des_prix_ingredients.xlsx` ([décision 1](../decisions.md)).

Pourquoi : les deux listes divergent. Mesuré le 2026-11-07 sur `data/20260721_evolution_des_prix_ingredients.xlsx` :
324 noms en colonne `Matière première` (329 lignes), 317 distincts. 72 ne sont que dans l'Excel, 49 que dans la base.
L'Excel a des doublons (`Lait Entier`, `Saumon fumé TR`, 7 au total), des espaces en trop (`LEVURE `, `Cacahuete `), deux
lignes proches (`Sel de Guérande` et `SEL GUERANDE`), et garde `Œuf entier liquide plein air 5KG`, déjà renommé sans
`5KG` dans la base.

Où : `Matcher` dans `pipeline/matcher.py`, et `review.py`, qui crée une matière dans la base. Lié à la question 4 de
[product.md](../product.md) et à [l'écriture validée dans le fichier](ecriture-sans-validation.md).
