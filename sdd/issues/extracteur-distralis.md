# Factures Distralis non lues

Quoi : les factures Distralis portent le nom `TEAM OUEST`, confirmé par le boulanger : Distralis dans le fichier Excel
et dans la base (117 lignes), `TEAM OUEST` sur le PDF et dans le XML. `FACTURE_19693635_A3B.pdf` (31/10/2026, 3 pages)
n'est reconnue par aucun extracteur, ses 39 lignes sont perdues. Le filet de poulet y est à 8,55 €/kg, le prix de la
décision 5.

Pourquoi : fournisseur de la première version, très important pour le boulanger.

Où : `pipeline/extractors/facturx_extractor.py`, `pipeline/router.py`.

Mesuré le 2026-11-07 sur cette facture :

- Son `factur-x.xml` est au profil EN 16931 et porte les 39 lignes du PDF, avec libellé, prix et quantité. Il ne faut
  donc pas d'extracteur sur le texte : les 2 factures de juin (19618693, 19629960) étaient au profil minimum, sans
  lignes. Le choix doit suivre le profil lu (décision 2). Un PDF de juin reste à essayer s'il revient.
- `FacturXExtractor.extraire` lit bien les 39 lignes, mais les attribue à `Transgourmet`, en dur, et l'unité sort
  `unité` sur les 39 : l'extracteur la cherche dans le texte du PDF (décision 7), dont le format diffère ici
  (`9.458 KG 8.550`, code parfois collé au libellé). Le XML donne `unitCode` : 19 `KGM`, 14 `C62`, 3 `XBX`, 2 `LTR`,
  1 `XPU`.
- `peut_traiter` répond non : il regarde le nom de fichier (`facturx`, `_fx`) ou `TRANSGOURMET`. À l'inverse, une
  facture d'un autre fournisseur nommée ainsi serait attribuée à Transgourmet.

À regarder au passage : lignes de matériel à ignorer (`CANDISSOIRE`, `CERCLE MOUSSE`, `MAIN ALUMINIUM`), et conversion
au kilo de `OEUF ECALE ... 150PI`, vendu à la pièce.
