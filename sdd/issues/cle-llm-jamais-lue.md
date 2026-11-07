# La clé du LLM n'est jamais lue dans .env

Quoi : `python-dotenv` est dans `requirements.txt`, mais aucun fichier n'appelle `load_dotenv`. La clé de `.env`
n'arrive donc pas à `pipeline/llm.py:32`, qui lève `RuntimeError` au premier cas ambigu.

Pourquoi : cette exception n'est pas rattrapée, et arrête le lot avant `run.py:66` : aucune ligne n'est écrite en base,
alors que `run.py:54` a déjà enregistré des alias. Seul `--no-llm` l'évite.

Où : `config.py` ou le point d'entrée, `pipeline/llm.py:32`.
