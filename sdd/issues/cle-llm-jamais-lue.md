# Une clé LLM absente arrête le lot en cours de route

Quoi : `pipeline/llm.py` lit `.env`, mais sans clé il lève `RuntimeError` au premier cas ambigu, pas au démarrage.

Pourquoi : la règle Errors de `coding-style.md` veut l'échec tout de suite ; ici, le lot en cours est perdu, alors que
`run.py` a déjà enregistré des alias. Seul `--no-llm` l'évite.

Où : `run.py`, qui sait seul si le LLM servira : à faire dans le lot qui retire l'apprentissage de `run.py`.
