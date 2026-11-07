# Pipeline factures → base de prix matières premières

Transforme des factures PDF (multi-fournisseurs) en lignes datées dans une base
de prix longue, prête à alimenter votre tableur de marges (OnlyOffice).

## Logique de rapprochement (cascade)

Pour chaque ligne de facture, le libellé fournisseur est rapproché d'une matière
de base en 4 étages, du moins cher au plus cher :

1. **Alias exact** — dictionnaire `data/dictionnaire_alias.csv`. Gratuit, déterministe, éditable à la main.
2. **Embeddings** — similarité sémantique (cosinus) sur l'index. Accepté si score ≥ `SEUIL_AUTO`.
3. **LLM** — n'arbitre que les cas ambigus, et **seulement** sur les 5 candidats les plus proches (RAG).
4. **Revue humaine** — sinon, la ligne part dans `data/a_valider.csv`.

Tout rapprochement validé (étages 2, 3, 4) est **réinjecté comme alias** : le
système apprend et sollicite de moins en moins les embeddings et le LLM.

### Revectorisation incrémentale
L'index sémantique = noms canoniques **+** tous les alias connus. Les vecteurs
sont mis en cache (`data/embeddings_cache.parquet`). À chaque lancement, **seuls
les nouveaux alias** (ceux que vous venez d'ajouter au dictionnaire) sont encodés
et ajoutés à l'index. On ne ré-encode jamais tout.

## Installation
```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
echo "GEMINI_API_KEY=votre_cle" > .env      # pour le fallback LLM
```

## Utilisation
```bash
# 1. déposez vos PDF dans factures_a_traiter/  (ou passez les chemins en argument)
python run.py
python run.py --no-llm            # alias + embeddings seulement (zéro appel LLM)

# 2. traitez les cas incertains
#    remplissez la colonne "Matiere de base (a remplir)" de data/a_valider.csv
python review.py
```

## Ajouter un fournisseur
Créez un extracteur dans `pipeline/extractors/` (héritez de `Extractor`,
implémentez `peut_traiter` et `extraire` en renvoyant des `LigneFacture`), puis
ajoutez-le à la liste `EXTRACTEURS` dans `pipeline/extractors/__init__.py`.
- Facture **Factur-X** (XML embarqué) → repartez de `facturx_extractor.py`.
- PDF classique → repartez de `pdf_extractors.py` (extraction `pdfplumber` + regex).

## Attention
Les extracteurs `pdfplumber` (Minoterie, Subéry, Crèmerie) sont calés sur les
factures fournies : **vérifiez la sortie sur vos vrais PDF** et ajustez les regex.
Transgourmet passe par le XML Factur-X, donc fiable sans réglage.
Les prix sont normalisés en €/kg quand le conditionnement est lisible ; sinon la
ligne reste à la pièce/barquette (colonne *Unité de mesure*).

## Arborescence
```
config.py                 seuils, chemins, modèle
run.py                    point d'entrée (traite un dossier)
review.py                 validation humaine + apprentissage d'alias
pipeline/
  router.py               détection fournisseur -> extracteur
  matcher.py              cascade alias -> embeddings -> LLM -> revue
  embeddings.py           index sémantique + cache incrémental
  llm.py                  fallback Gemini (short-list RAG)
  normalize.py            prix -> €/kg
  writer.py               écriture base + file de revue
  extractors/             un extracteur par fournisseur
data/
  base_prix_matieres_premieres.csv
  dictionnaire_alias.csv
  embeddings_cache.parquet   (généré)
  a_valider.csv              (généré)
```
