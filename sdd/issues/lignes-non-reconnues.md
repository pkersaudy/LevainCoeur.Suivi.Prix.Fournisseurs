# Les lignes non reconnues sont perdues en silence

Quoi : `pipeline/extractors/pdf_extractors.py:6` promet qu'une ligne non reconnue part en revue, mais les extracteurs
font `continue` (`:59`, `:93`, `:124`) et elle disparaît.

Pourquoi : `product.md` veut montrer les lignes non reconnues à part ; une matière peut échapper au suivi sans que rien
ne le signale. Il faudra aussi distinguer ces lignes de celles qui ne sont pas des articles (totaux, en-têtes).

Où : `pipeline/extractors/pdf_extractors.py`.
