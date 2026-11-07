# Décisions

1. **Le fichier de référence est le tableau `AAAAMMJJ_evolution_des_prix_ingredients.xlsx`**, une ligne par matière et
   une colonne de prix par fournisseur : l'application le compare et l'écrit. C'est le fichier que le boulanger relit.
   Rejected: la base longue CSV comme référence, illisible pour lui.

2. Superseded by 9.

3. Superseded by 10.

4. Superseded by 11.

5. **Aucun prix écrit sans validation humaine, facture à l'appui.** Juin 2026 a montré une erreur de facturation (filet
   de poulet Distralis à 14,927 €/kg au lieu de 8,55 €/kg, réglée par avoir) et des conditionnements trompeurs.
   Rejected: écrire seul au-dessus d'un seuil de confiance.

6. **Les prix se comparent dans l'unité de la ligne du fichier.** La proposition Transgourmet donne des prix au
   conditionnement (amandes effilées 42,25 € le colis de 5 kg, soit 8,45 €/kg) ; les œufs durs se ramènent au kilo avec
   48 g par œuf, convention choisie par le boulanger. Rejected: reprendre le prix facturé tel quel.

7. **L'unité Transgourmet se lit dans le texte du PDF, le reste de la ligne dans le XML.** Les 39 lignes des 2 factures
   d'octobre-novembre 2026 portent `unitCode=""` ; le texte donne l'unité des 37 articles (seuls les 2 `FRAIS DE
   FACTURATION` en sont absents). Rejected: tout lire dans le texte (décision 9) ; déduire l'unité du libellé, qui
   ne dit pas si `SUCRE 25 KG` est vendu au kilo ou au sac.

8. **L'arbitrage passe par Claude Haiku 5.5 avec le SDK `anthropic`, sa réponse limitée par un schéma JSON aux
   candidats.** `gemini-3.8-flash` a échoué en 503 ou 504 sur tous les appels du 2026-11-07, sauf un. Sur les 65 lignes
   réelles, Haiku 5.5 répond à tous les appels, en 1,5 s en moyenne, pour moins d'un centime au total, et aucune réponse
   n'est coupée (332 jetons au plus). Rejected: garder Gemini ; passer par `langchain-anthropic`, une couche de plus pour
   un seul appel ; Sonnet ou Opus, plus chers, sans besoin mesuré.

9. **Transgourmet et Distralis se lisent dans le XML Factur-X embarqué, les autres dans le texte du PDF.** Le XML au
   profil EN 16931 porte les lignes : 2, 6 et 15 chez Transgourmet en juin 2026, 25 et 14 en octobre-novembre, 39 sur la
   facture Distralis du 31/10/2026, dont le `unitCode` donne l'unité, identique au PDF sur les 39. Distralis n'était
   écarté que pour ses 2 factures de juin, au profil minimum, sans lignes ; Minoterie, Subéry et Crèmerie n'ont pas de
   XML. Rejected: un extracteur sur le texte Distralis, inutile tant que le XML porte les lignes ; extraire toutes les
   factures avec un LLM sur le texte brut (prototype `multiagentapp.py` : coûteux, non déterministe, invente ou perd des
   lignes).

10. Superseded by 11.

11. **Rapprochement en cascade : alias exact, puis LLM sur les 10 candidats les plus proches par n-grammes de
    caractères, puis le boulanger. Le score de proximité ne valide rien, et un choix du LLM sous 0,90 de confiance part
    en revue. À 0,90 ou plus, il va en base et reste en revue, en catégorie `llm matched`. Seule la revue humaine crée
    un alias : `oui` valide le choix, une autre matière corrige la ligne de base. Le dictionnaire d'alias est la seule
    vérité éditable : l'index se reconstruit en mémoire depuis la base et le dictionnaire, sans cache.** Le 2026-11-07,
    sur 70 libellés hors alias, boissons et consommables exclus, dont 46 ont une matière selon le boulanger : les
    n-grammes mettent la bonne matière dans les 10 premiers candidats pour les 46 (rang 7 au pire), les embeddings
    `paraphrase-multilingual-MiniLM-L12-v2` pour 19 des 43 premiers étiquetés (`SUCRE GLACE` au rang 157). Avec Claude
    Haiku 5.5, au seuil de 0,90 : 29 justes, aucun faux, 1 seul choix accepté parmi les 24 sans matière ; au seuil de
    0,80 : 35 justes, 2 faux, 4 acceptés à tort (`BATONNET FUME` -> `Saumon fumé TR`). Un alias validé fait venir sa
    matière en tête pour les libellés voisins : les 3 `OEUF ECALE` vont à `Oeuf seau 75/120` dès que l'un est validé.
    Rejected: les embeddings (rappel ci-dessus, PyTorch de 809 Mo à installer, cache de vecteurs à purger quand un alias
    disparaît) ; une base vectorielle (327 textes, 0,03 ms par recherche, le stockage n'était pas en cause) ; mélanger
    embeddings et n-grammes (26 sur 43 dans les 5 premiers, contre 42) ; envoyer les 294 matières au LLM (38 justes
    contre 37 à 0,80, 7 fois plus de jetons, et plus de candidats pour le boulanger sans LLM) ; montrer au LLM les
    libellés déjà validés de chaque candidat (32 justes contre 29 à 0,90, mais `Persil Plat` -> `Persil surg` accepté à
    0,90) ; garder un seuil bas avant le LLM (le score n'a plus la même échelle, et une ligne de plus coûte environ un
    centième de centime) ; `thefuzz` seul (prototype, seuil 80) ; un graphe LangGraph multi-agents (le flux est
    linéaire) ; ne jamais faire d'un choix du LLM un alias (tout reste en LLM, aucun exact à terme) ; des « colonnes de
    synonymes vectorisées » à éditer (des vecteurs ne se lisent ni ne se corrigent) ; valider en recopiant le nom (plus
    de saisie, la colonne `Valide (oui)` a été préférée par le boulanger).
