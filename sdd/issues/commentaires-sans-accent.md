# Corriger les commentaires sans accent

Quoi : remettre les accents dans les commentaires et les docstrings de tout le code Python hors `sdd/`, dans un batch
dédié. Aucune chaîne du code ne change : ni les données (noms de colonnes CSV comme `"Libelle facture"`), ni les messages
affichés (choix du 7 novembre 2026).

Pourquoi : `sdd/coding-style.md` veut le français accentué et sa correction quand un fichier est retouché. Le batch Ruff
a retouché tous les fichiers sans le faire, pour ne pas noyer son diff.

Où : vu par exemple dans `config.py` (« editable a la main », « deposez vos PDF »).
