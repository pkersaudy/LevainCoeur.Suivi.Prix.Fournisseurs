---
governs: [run.py, review.py, pipeline/writer.py, tests/test_ecriture.py]
depends: [extraction, normalisation, rapprochement]
risk: high
---
# ecriture

Enchaîner le traitement d'un lot de factures et porter tout ce qui écrit un prix. Une erreur ici fausse les marges du
boulanger sans bruit, d'où le quiz strict. Les règles d'écriture sont celles de [product.md](../product.md) ; le moteur
écrit aujourd'hui dans la base longue, et la cible est le fichier `.xlsx` ([décision 1](../decisions.md)).

Hors du module : l'interface, encore à bâtir.

- Une ligne incertaine part en file de revue avec ses candidats, et n'est pas perdue ; à vérifier à la main.
- Une ligne à rapprocher remplie rejoint la base et devient un alias :
  [test_une_ligne_a_rapprocher_remplie_rejoint_la_base_et_devient_un_alias](../../tests/test_ecriture.py).
- Une ligne de revue laissée vide reste en file et n'écrit rien, `oui` ne vaut que pour un choix du LLM :
  [test_une_ligne_de_revue_laissee_vide_reste_en_file](../../tests/test_ecriture.py),
  [test_oui_ne_valide_pas_une_ligne_sans_choix_du_llm](../../tests/test_ecriture.py).
- Un choix du LLM rejoint la base et la revue, sans devenir un alias :
  [test_un_choix_du_llm_rejoint_la_base_et_la_revue_sans_devenir_un_alias](../../tests/test_ecriture.py).
- Validé par `oui`, il devient un alias exact sans doubler la ligne de base ; corrigé, la ligne de base change de
  matière : [test_un_choix_du_llm_valide_devient_un_alias_exact_sans_doubler_la_base](../../tests/test_ecriture.py),
  [test_un_choix_du_llm_corrige_rectifie_la_base_et_l_alias](../../tests/test_ecriture.py).

Écarts connus : [écriture sans validation](../issues/ecriture-sans-validation.md),
[dates de la base](../issues/dates-base-longue.md).
