# Deux formats de date dans la base longue

Quoi : sur 405 lignes de `data/base_prix_matieres_premieres.csv`, 364 sont en `06-30-26` (mois d'abord) et 41 en
`jj/mm/aaaa`, le format des extracteurs. `pipeline/writer.py` les trie comme du texte.

Pourquoi : l'historique se trie mal et se lit mal. À traiter selon la question ouverte 5 de `product.md`, sur l'avenir
de cette base.

Où : `pipeline/writer.py`, `data/base_prix_matieres_premieres.csv`.
