# Mettre Ruff en place

Quoi : ajouter Ruff, le configurer (largeur 120, `sdd/` exclu), reformater le code et lancer le contrôle dans le CI.
Choix du 7 novembre 2026, voir `sdd/coding-style.md`.

Pourquoi : aucun formateur ni linter n'existe. Le reformatage touche tous les modules, donc son batch part seul, avec
`Large-Batch`, et ne change aucun comportement.

Où : tout le code Python hors `sdd/`, `.github/workflows/sdd.yml`.
