# Décisions

1. **Le fichier de référence est le tableau `AAAAMMJJ_evolution_des_prix_ingredients.xlsx`**, une ligne par matière et
   une colonne de prix par fournisseur : l'application le compare et l'écrit. C'est le fichier que le boulanger relit.
   Rejected: la base longue CSV comme référence, illisible pour lui.

2. Superseded by 9.

3. Superseded by 10.

4. **Le dictionnaire d'alias est la vérité éditable, les vecteurs ne sont qu'un cache.** Chaque rapprochement validé
   devient un alias ; seuls les textes nouveaux sont vectorisés. Rejected: des « colonnes de synonymes vectorisées » à
   éditer, des vecteurs ne se lisent ni ne se corrigent.

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

10. **Rapprochement en cascade : alias exact, puis LLM sur les 5 candidats les plus proches trouvés par les embeddings,
    puis le boulanger. Les embeddings ne valident rien, et un choix du LLM sous 0,80 de confiance part en revue. À 0,80
    ou plus, il va en base et reste en revue, en catégorie `llm matched`. Seule la revue humaine crée un alias : `oui`
    valide le choix, une autre matière corrige la ligne de base.** Les libellés fournisseurs sont trop loin des noms du fichier pour une distance de
    caractères : « Herbe Cello Menthe 30g France » pour « Menthe fraiche », « FAR. BLE BIO MEULE BISE FR 25 KG » pour
    « Blé Bio Meule Bise T80 ». Le 2026-11-07, sur les 65 premières lignes réelles, 6 des 8 premières lignes acceptées
    par les embeddings étaient fausses (`JAUNE OEUF` -> `Blanc d'oeuf liquide`, `Panais` -> `Rhurbarbe` à 0,95) et les 4
    choix du LLM à 0,60 étaient tous douteux ; un alias appris automatiquement rejouait ensuite l'erreur à 1,00.
    Rejected: `thefuzz` seul (prototype, seuil 80) ; tout confier au LLM (coût, résultats variables) ; un graphe
    LangGraph multi-agents (le flux est linéaire, 10 factures par mois ne le justifient pas) ; garder une acceptation
    par embeddings à un seuil plus haut (`Cat.1 France` pèse plus que le produit, l'erreur se mesure à 0,95) ; ne jamais
    faire d'un choix du LLM un alias (tout reste en LLM, aucun exact à terme) ; valider en recopiant le nom (plus de
    saisie, la colonne `Valide (oui)` a été préférée par le boulanger).
