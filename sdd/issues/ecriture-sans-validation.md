# Le moteur écrit sans validation, et pas dans le bon fichier

Quoi : `run.py:42` envoie en base toute ligne rapprochée, sans que personne n'ait rien validé. Rien n'écrit le
`.xlsx` : `pipeline/writer.py` ne connaît que le CSV, et `openpyxl` n'est pas dans `requirements.txt`.

Pourquoi : contredit les décisions 1 et 5 et la règle « rien n'est écrit sans validation explicite » de `product.md`.

Où : `run.py`, `pipeline/writer.py`. Vu à l'adoption de SDD-Fabrik.
