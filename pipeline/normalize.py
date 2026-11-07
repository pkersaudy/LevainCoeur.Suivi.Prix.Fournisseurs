"""Normalisation des prix vers EUR/kg (ou EUR/L) quand le poids/volume du
conditionnement est lisible dans le libellé. Sinon on garde tel quel."""

from __future__ import annotations

import re

RE_KG = re.compile(r"(\d+[.,]?\d*)\s*KG", re.IGNORECASE)
RE_G = re.compile(r"(\d+[.,]?\d*)\s*G\b", re.IGNORECASE)
RE_L = re.compile(r"(\d+[.,]?\d*)\s*L\b", re.IGNORECASE)
RE_CL = re.compile(r"(\d+[.,]?\d*)\s*CL", re.IGNORECASE)
RE_X = re.compile(r"X\s*(\d+)", re.IGNORECASE)  # ex: X18, X75


def _num(s: str) -> float:
    return float(s.replace(",", "."))


def vers_prix_kg(prix: float, unite: str, designation: str) -> tuple[float, str, bool]:
    """Retourne (prix_normalise, unite_finale, a_ete_converti).

    - unité 'kg'/'L' : déjà bon.
    - unité pièce/colis/barquette : on cherche un poids dans le libellé.
    """
    u = (unite or "").lower()
    if u in ("kg", "l"):
        return prix, u, False

    d = designation.upper()
    m = RE_KG.search(d)
    if m:
        return round(prix / _num(m.group(1)), 4), "kg", True
    m = RE_G.search(d)
    if m:
        return round(prix / (_num(m.group(1)) / 1000), 4), "kg", True
    m = RE_L.search(d)
    if m:
        return round(prix / _num(m.group(1)), 4), "L", True
    m = RE_CL.search(d)
    if m:
        return round(prix / (_num(m.group(1)) / 100), 4), "L", True
    # sinon on ne sait pas convertir : on laisse le prix à la pièce
    return prix, unite, False
