# Le moteur n'a jamais tourné de bout en bout

Quoi : `run.py` et `review.py` n'ont été vérifiés qu'en syntaxe ; `sentence-transformers` et `factur-x` n'étaient pas
installables là où le code a été écrit.

Pourquoi : les regex de `pipeline/extractors/pdf_extractors.py` (Minoterie, Subéry, Crèmerie) sont calées à la main sur
les factures de juin 2026, et `_map_unite` de `facturx_extractor.py` n'a vu aucun vrai code d'unité.

Où : à mesurer sur les 9 factures de juin 2026 avant de bâtir l'interface dessus.
