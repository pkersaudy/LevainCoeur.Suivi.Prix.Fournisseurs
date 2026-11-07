# Factures Distralis au profil minimum

Quoi : les 2 factures Distralis de juin 2026 (19618693, 19629960) avaient un `factur-x.xml` au profil minimum, sans
lignes, alors que celle du 31/10/2026 est au profil EN 16931 (décision 9). Si ce profil revient, l'extracteur ne rend
aucune ligne, et seul `0 ligne(s)` le signale.

Pourquoi : ces factures seraient perdues en silence ; aucun PDF de ce profil n'est disponible pour mesurer.

Où : `pipeline/extractors/facturx_extractor.py`. À essayer si un PDF de juin revient.
