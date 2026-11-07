---
governs: [pipeline/matcher.py, pipeline/embeddings.py, pipeline/llm.py]
---
# rapprochement

Relier un libellé fournisseur à une matière, du moyen le moins cher au plus cher : la cascade de la
[décision 3](../decisions.md), avec le dictionnaire d'alias pour seule vérité éditable ([décision 4](../decisions.md)).
Dans le doute, la ligne revient au boulanger : un rapprochement faux coûte plus cher qu'une question.

Hors du module : extraire le libellé, convertir le prix, écrire quoi que ce soit dans la base.

- Un libellé déjà connu du dictionnaire est reconnu sans embeddings ni LLM ; à vérifier à la main.
- Le LLM ne reçoit que le libellé et les candidats les plus proches, et une réponse hors de ces candidats est ignorée ;
  à vérifier à la main.
- Sous le seuil bas, ou le LLM coupé par `--no-llm`, la ligne incertaine part en revue ; à vérifier à la main.
- Sel de Guérande, sel fin et gros sel restent trois matières ; à vérifier à la main.

Écarts connus : [alias sans fournisseur](../issues/alias-sans-fournisseur.md),
[clé LLM jamais lue](../issues/cle-llm-jamais-lue.md).
