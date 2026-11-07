---
governs: [pipeline/matcher.py, pipeline/candidats.py, pipeline/llm.py, tests/test_llm.py, tests/test_candidats.py]
---
# rapprochement

Relier un libellé fournisseur à une matière, du moyen le moins cher au plus cher : la cascade de la
[décision 11](../decisions.md), avec le dictionnaire d'alias pour seule vérité éditable.
Dans le doute, la ligne revient au boulanger : un rapprochement faux coûte plus cher qu'une question.

Hors du module : extraire le libellé, convertir le prix, écrire quoi que ce soit dans la base.

- Un libellé déjà connu du dictionnaire est reconnu sans LLM ; à vérifier à la main.
- Les candidats sont les matières qui partagent le plus de fragments de mots avec le libellé, chacune une fois, et un
  alias validé rapproche sa matière des libellés voisins :
  [test_candidats.py](../../tests/test_candidats.py).
- Le LLM ne reçoit que le libellé et les candidats les plus proches, et une réponse hors de ces candidats est ignorée ;
  à vérifier à la main.
- Un score de proximité ne valide rien, même élevé : il passe par le LLM, ou part en revue avec le LLM coupé par
  `--no-llm` : [test_un_score_de_proximite_eleve_passe_par_le_llm](../../tests/test_llm.py),
  [test_un_score_de_proximite_eleve_ne_valide_rien](../../tests/test_llm.py).
- Un choix du LLM sous 0,90 de confiance part en revue :
  [test_un_choix_du_llm_sous_le_seuil_de_confiance_part_en_revue](../../tests/test_llm.py).
- Une panne du LLM n'arrête pas le lot, et ses lignes restantes partent en revue sans nouvel appel :
  [test_service_indisponible_envoie_le_lot_en_revue_sans_rappeler](../../tests/test_llm.py).
- Sel de Guérande, sel fin et gros sel restent trois matières ; à vérifier à la main.

Écarts connus : [alias sans fournisseur](../issues/alias-sans-fournisseur.md),
[clé LLM absente en cours de lot](../issues/cle-llm-jamais-lue.md),
[références du fichier Excel](../issues/references-du-fichier-excel.md).
