# Pipeline factures → base de prix matières premières

Transforme des factures PDF (multi-fournisseurs) en lignes datées dans une base
de prix longue, prête à alimenter votre tableur de marges (OnlyOffice).

## Logique de rapprochement (cascade)

Pour chaque ligne de facture, le libellé fournisseur est rapproché d'une matière
de base en 3 étages, du moins cher au plus cher :

1. **Alias exact** — dictionnaire `data/dictionnaire_alias.csv`. Gratuit, déterministe, éditable à la main.
2. **LLM** — choisit **seulement** parmi les 10 candidats les plus proches par n-grammes de caractères (RAG), retenu
   si sa confiance est ≥ `SEUIL_CONFIANCE_LLM`. Le score de proximité seul ne valide rien.
3. **Revue humaine** — sinon, la ligne part dans `data/a_valider.csv`.

Un choix du LLM va en base **et** reste dans `data/a_valider.csv`, en catégorie `llm matched`. Seule la revue humaine
**crée un alias** : une erreur de la machine ne devient jamais une vérité à 1,00, et un libellé validé est reconnu
exactement la fois suivante.

### Index des candidats
L'index = noms canoniques **+** tous les alias connus, reconstruit en mémoire à chaque lancement : un alias ajouté au
dictionnaire compte tout de suite, sans cache ni modèle à télécharger.

## Installation
```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
echo "ANTHROPIC_API_KEY=votre_cle" > .env      # pour le fallback LLM
```

## Utilisation
```bash
# 1. déposez vos PDF dans factures_a_traiter/  (ou passez les chemins en argument)
python run.py
python run.py --no-llm            # alias seulement, le reste part en revue (zéro appel LLM)

# 2. traitez les cas incertains
#    dans data/a_valider.csv, remplissez "Matiere de base (a remplir)" ;
#    pour une ligne "llm matched", écrivez oui dans "Valide (oui)", ou la bonne matière pour corriger
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
Transgourmet et Distralis passent par le XML Factur-X, donc fiables sans réglage.
Les prix sont normalisés en €/kg quand le conditionnement est lisible ; sinon la
ligne reste à la pièce/barquette (colonne *Unité de mesure*).

## Arborescence
```
config.py                 seuils, chemins, modèle LLM
run.py                    point d'entrée (traite un dossier)
review.py                 validation humaine + apprentissage d'alias
pipeline/
  router.py               détection fournisseur -> extracteur
  matcher.py              cascade alias -> LLM sur les candidats -> revue
  candidats.py            index des candidats par n-grammes
  llm.py                  fallback Claude Haiku (short-list RAG)
  normalize.py            prix -> €/kg
  writer.py               écriture base + file de revue
  extractors/             un extracteur par fournisseur
data/
  base_prix_matieres_premieres.csv
  dictionnaire_alias.csv
  a_valider.csv              (généré)
```
