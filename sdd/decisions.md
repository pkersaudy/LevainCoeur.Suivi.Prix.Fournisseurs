# Décisions

1. **Le fichier de référence est le tableau `AAAAMMJJ_evolution_des_prix_ingredients.xlsx`**, une ligne par matière et
   une colonne de prix par fournisseur : l'application le compare et l'écrit. C'est le fichier que le boulanger relit.
   Rejected: la base longue CSV comme référence, illisible pour lui.

2. **Transgourmet se lit dans le XML Factur-X embarqué, les autres dans le texte du PDF.** Les 3 factures Transgourmet de
   juin 2026 portent un `factur-x.xml` au profil EN 16931 avec leurs lignes (2, 6 et 15) ; les 2 factures Distralis ont
   un `factur-x.xml` au profil minimum, sans aucune ligne ; Minoterie, Subéry et Crèmerie n'en ont pas. Le choix suit
   donc le profil lu, pas la seule présence du XML. Rejected: extraire toutes les factures avec un LLM sur le texte brut
   (prototype `multiagentapp.py` : coûteux, non déterministe, invente ou perd des lignes).

3. **Rapprochement en cascade : alias exact, puis embeddings, puis LLM sur les 5 candidats les plus proches, puis le
   boulanger.** Les libellés fournisseurs sont trop loin des noms du fichier pour une distance de caractères :
   « Herbe Cello Menthe 30g France » pour « Menthe fraiche », « FAR. BLE BIO MEULE BISE FR 25 KG » pour
   « Blé Bio Meule Bise T80 ». Rejected: `thefuzz` seul (prototype, seuil 80) ; tout confier au LLM (coût, résultats
   variables) ; un graphe LangGraph multi-agents (le flux est linéaire, 10 factures par mois ne le justifient pas).

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
   FACTURATION` en sont absents). Rejected: tout lire dans le texte (décision 2) ; déduire l'unité du libellé, qui
   ne dit pas si `SUCRE 25 KG` est vendu au kilo ou au sac.
