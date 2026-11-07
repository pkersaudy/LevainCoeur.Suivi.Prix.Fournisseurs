---
governs: [run.py, review.py, pipeline/writer.py]
depends: [extraction, normalisation, rapprochement]
risk: high
---
# ecriture

Enchaîner le traitement d'un lot de factures et porter tout ce qui écrit un prix. Une erreur ici fausse les marges du
boulanger sans bruit, d'où le quiz strict. Les règles d'écriture sont celles de [product.md](../product.md) ; le moteur
écrit aujourd'hui dans la base longue, et la cible est le fichier `.xlsx` ([décision 1](../decisions.md)).

Hors du module : l'interface, encore à bâtir.

- Une ligne incertaine part en file de revue avec ses candidats, et n'est pas perdue ; à vérifier à la main.
- Une ligne de revue remplie rejoint la base et devient un alias ; à vérifier à la main.
- Une ligne de revue laissée vide reste en file ; à vérifier à la main.

Écarts connus : [écriture sans validation](../issues/ecriture-sans-validation.md),
[cellules vides en revue](../issues/review-cellules-vides.md), [dates de la base](../issues/dates-base-longue.md).
