# Conversions de conditionnement incomplètes

Quoi :
- `RE_X` (`pipeline/normalize.py:10`) n'est jamais utilisé : un lot de 24 bouteilles de 33 cl se divise par 0,33 L sans
  tenir compte des 24.
- La convention des œufs durs à 48 g (décision 6) n'existe pas dans le code.
- `run.py:37` jette l'indication de conversion, alors que `product.md` veut afficher le calcul.
- Tout se ramène au kg ou au litre sans regarder l'unité de la ligne du fichier.

Pourquoi : un mauvais diviseur donne un prix faux mais plausible.

Où : `pipeline/normalize.py`, `run.py:37`. À mesurer sur les libellés réels de juin 2026 avant de corriger.
