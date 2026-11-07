# Remplacer Gemini par Claude Haiku 5.5 pour l'arbitrage

Quoi : idée du boulanger, une clé API Anthropic et `claude-haiku-5-5` à la place de `gemini-3.8-flash` dans
`pipeline/llm.py`.

Pourquoi : Gemini a échoué en 503 ou 504 sur tous les appels mesurés le 2026-11-07, sauf un. Or, sans acceptation par
embeddings, le LLM porte tout le rapprochement automatique.

Où : `pipeline/llm.py`, `config.py`, `requirements.txt`, avant ou avec le retrait des embeddings. À écrire en décision.
Le format JSON imposé peut limiter la réponse aux candidats. À évaluer sur les lignes réelles avant de s'y fier.
