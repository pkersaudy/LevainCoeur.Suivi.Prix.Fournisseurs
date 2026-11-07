# Pas d'extracteur Distralis

Quoi : Distralis est un fournisseur de la première version, mais `pipeline/extractors/` n'a rien pour lui.

Pourquoi : son `factur-x.xml` est au profil minimum, sans lignes d'articles (factures 19618693 et 19629960) ; il faut
lire le texte du PDF comme pour Minoterie. Le routeur actuel ne doit pas l'envoyer à l'extracteur Factur-X.

Où : `pipeline/extractors/`, `pipeline/router.py`.

Le routeur va plus loin que la décision 2 : `pipeline/extractors/facturx_extractor.py:31` choisit Factur-X sur le seul
nom de fichier (`facturx`, `_fx`), sans lire le profil.
