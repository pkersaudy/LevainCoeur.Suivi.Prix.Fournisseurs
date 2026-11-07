# La bonne matière n'arrive pas toujours jusqu'au LLM

Quoi : mesuré le 2026-11-07 avec Claude Haiku 5.5 sur les 65 lignes réelles, chacune avec ses 5 candidats d'embeddings.
Le LLM écarte bien les mauvais candidats (40 lignes sans choix, dont `Panais` -> `Rhurbarbe` à 0,95), mais la short-list
perd des matières qui existent : `Sucre semoule`, `Sel de Guérande`, `Jaune d'œuf plein air tetra 1L`, `Roquette`,
`Jambon Cuit`, `Cacahuetes`, `Levure`, `Aneth`, `Tournesol`, `Lait Entier`.

Pourquoi : ces lignes partent en revue alors qu'elles se reconnaissent à la lecture, et une matière proche peut être
choisie à la place : `Salade Roquette` -> `Salade multi feuille`, `GRAINE DE TOURNESOL` -> `Melange Graine et
Legumineuses`, `LAIT ENTIER BRICK 1 L` -> `Lait Entier cremerie de la rance`.

Vu le 2026-11-07 : `data/embeddings_cache.parquet` garde 22 vecteurs absents de la base et du dictionnaire, restes des
alias appris automatiquement (`Carotte Lavée Sac Cal.35+ 10 kg Cat.1 France` -> `Rhurbarbe`, `Panais 5 kg Cat.1 France`
-> `Rhurbarbe`, `Herbe Cello Aneth 30 g France` -> `Menthe fraiche`). `IndexSemantique.chercher` parcourt tout le cache :
ces erreurs restent candidates à un score proche de 1, et faussent les mesures de cette issue. À corriger d'abord, puis
à remesurer.

Où : `TOP_K` et `SEUIL_LLM` dans `config.py`, `pipeline/embeddings.py`. À mesurer : une short-list plus longue, à
presque rien par ligne avec Haiku 5.5 ; le contrat et la décision 10 limitent le LLM aux 5 plus proches.

Confiance : les 21 choix à 0,80 ou plus sont plausibles sauf le lait ci-dessus. Résultats jugés à la lecture, à faire
confirmer par le boulanger.
