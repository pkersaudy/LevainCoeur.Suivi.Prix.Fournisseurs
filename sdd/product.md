# Produit : mise à jour des prix matières premières depuis les factures

## Pourquoi

Le boulanger reçoit une dizaine de factures par mois de 4 à 5 fournisseurs. Chaque variation de prix doit être reportée
dans son fichier de référence `AAAAMMJJ_evolution_des_prix_ingredients.xlsx` (une ligne par matière, une colonne de prix
par fournisseur), qui sert ensuite à suivre ses marges. Aujourd'hui ce report est manuel, long, et piégeux : les
factures parlent en colis, sachets ou pièces quand le fichier parle en €/kg, et les libellés fournisseurs ne ressemblent
pas aux noms du fichier.

## Pour qui

Le boulanger, seul utilisateur, non développeur, sur son PC Linux. Il ouvre l'application sans terminal.

## Le parcours

1. Il importe une ou plusieurs factures PDF dans une interface simple.
2. L'application affiche, sous forme de tableau, les évolutions détectées par rapport à la version actuelle du fichier :
   matière (ligne du fichier), fournisseur (colonne), prix actuel, prix détecté, écart en € et en %, libellé d'origine
   sur la facture, et la confiance du rapprochement. Les prix modifiés, les produits sans ligne dans le fichier et les
   lignes non reconnues sont séparés ; les prix inchangés sont repliés.
3. Il vérifie, facture à l'appui : la facture est visible à côté du tableau.
4. Il corrige ce qui est faux : le prix, la ligne de rattachement, ou il ignore la ligne, ou crée une nouvelle matière.
5. Il valide, et alors seulement les prix sont écrits dans le fichier, avec leur trace.

## Règles

- Rien n'est écrit dans le fichier sans validation explicite du boulanger.
- Chaque prix écrit garde sa trace : ancien prix, facture d'origine, date. La version précédente du fichier reste
  récupérable.
- Un prix est comparé et écrit dans l'unité de la ligne du fichier (€/kg, €/L ou à la pièce). Une conversion de
  conditionnement affiche son calcul : 42,25 € le colis de 5 kg donne 8,45 €/kg.
- Un prix non numérique déjà présent dans le fichier (8 cellules au 21/07/2026, comme `23,50 ou 27`) est affiché tel
  quel, sans écart calculé, et n'est remplacé que sur confirmation. Un nombre saisi en texte (`173.44`) se lit comme un
  nombre.
- Des produits proches ne sont jamais fusionnés d'office : sel de Guérande, sel fin et gros sel sont trois matières.
- Un rattachement validé est retenu : la même désignation du même fournisseur est reconnue seule la fois suivante.
- Le fichier reste utilisable dans OnlyOffice : sa mise en forme, ses commentaires et ses couleurs existantes sont
  préservés, et la convention en place continue (prix modifié surligné, ancien prix en commentaire).
- Les factures restent sur le PC. Seul le recours à un LLM, pour les cas ambigus, envoie le libellé d'une ligne (jamais
  la facture) à un service externe ; on peut le couper.

## Fournisseurs de la première version

| Fournisseur | Colonne du fichier | Facture |
|---|---|---|
| Transgourmet | `Trans` | Factur-X avec les lignes d'articles |
| Distralis | `distralis` | PDF texte (son Factur-X ne porte pas les lignes) |
| Crèmerie de la Rance | `CREMERIE DE LA RANCE` | PDF texte |
| Minoterie du Château | aucune pour l'instant | PDF texte |
| Subéry Claude et Fils | aucune pour l'instant | PDF texte |

Ajouter un fournisseur ensuite doit rester un petit travail.

## Réussite

- Une facture se traite, de l'import à la validation, en moins de 5 minutes.
- Sur les 9 factures de juin 2026, au moins 90 % des lignes de matières premières tombent sur la bonne ligne du fichier
  sans correction.
- Aucune écriture non validée, jamais de fichier de référence perdu.

## Hors périmètre

- La mise à jour directe du tableur de marges `Carte_Produits_et_marges.xlsx` : étape suivante.
- Les factures scannées ou photographiées : seulement les PDF texte et Factur-X.
- Les avoirs, remises, TVA et la comptabilité.
- Les boissons et les consommables (Coca, film alimentaire, frais de facturation) : ignorés pour l'instant, la façon de
  les intégrer à l'application reste à arbitrer.
- Plusieurs utilisateurs, le cloud, le mobile.

## Questions ouvertes

Chacune tranchée passe dans `decisions.md` et sort d'ici.

1. Version du fichier : écrire une nouvelle copie datée `AAAAMMJJ_...xlsx` (recommandé) ou modifier en place avec une
   sauvegarde ?
2. Créer les colonnes Minoterie du Château et Subéry Claude et Fils dans le fichier (recommandé) ?
3. Interface : application web locale en Python ouverte dans le navigateur, qui réutilise le moteur existant
   (recommandé), ou application de bureau ?
4. Embeddings : `sentence-transformers` installe PyTorch, lourd pour le PC du boulanger ; une bibliothèque ONNX plus
   légère est à mesurer avant de choisir.
5. La base longue `data/base_prix_matieres_premieres.csv` devient-elle le journal des prix validés, ou disparaît-elle
   au profit des commentaires du fichier ?
