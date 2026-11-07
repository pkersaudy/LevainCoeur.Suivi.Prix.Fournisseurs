# review.py prend les cellules vides pour remplies

Quoi : `review.py:23` compare à `""`, mais pandas lit une cellule vide en NaN, que `astype(str)` change en `'nan'`.
Mesuré avec pandas 3.1.1 : sur 2 lignes dont une vide, les 2 sont retenues, la vide avec la valeur `nan`.

Pourquoi : chaque ligne laissée vide entrerait en base comme une matière nommée `nan`, et deviendrait un alias.

Où : `review.py:23` et son pendant `review.py:45` (lignes restantes).
