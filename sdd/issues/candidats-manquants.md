# La bonne matière n'arrive pas toujours jusqu'au LLM

Quoi : mesuré le 2026-11-07 avec Claude Haiku 5.5 sur les 65 lignes réelles, chacune avec ses 5 candidats d'embeddings.
Le LLM écarte bien les mauvais candidats (40 lignes sans choix, dont `Panais` -> `Rhurbarbe` à 0,95), mais la short-list
perd des matières qui existent : `Sucre semoule`, `Sel de Guérande`, `Jaune d'œuf plein air tetra 1L`, `Roquette`,
`Jambon Cuit`, `Cacahuetes`, `Levure`, `Aneth`, `Tournesol`, `Lait Entier`.

Pourquoi : ces lignes partent en revue alors qu'elles se reconnaissent à la lecture, et une matière proche peut être
choisie à la place : `Salade Roquette` -> `Salade multi feuille`, `GRAINE DE TOURNESOL` -> `Melange Graine et
Legumineuses`, `LAIT ENTIER BRICK 1 L` -> `Lait Entier cremerie de la rance`.

Où : `TOP_K` et `SEUIL_LLM` dans `config.py`, `pipeline/embeddings.py`. À mesurer : une short-list plus longue, à
presque rien par ligne avec Haiku 5.5 ; le contrat et la décision 3 limitent le LLM aux 5 plus proches.

Confiance : `matcher.py` accepte tout choix du LLM. Les 4 choix à 0,60 sont tous douteux, les 21 à 0,80 ou plus sont
plausibles sauf le lait ci-dessus. Le seuil à 0,80 est tranché : voir [le moteur](moteur-jamais-execute.md). Résultats
jugés à la lecture, à faire confirmer par le boulanger.
